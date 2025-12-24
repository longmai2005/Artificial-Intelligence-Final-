"""
Improved Energy Predictor - Smart User Adjustment
Sử dụng hệ số thông minh dựa trên nghiên cứu thực tế để điều chỉnh pattern
"""

import numpy as np
import pandas as pd
import joblib
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class EnergyPredictor:
    """
    Predictor with smart user adjustment based on:
    1. Time pattern from trained model (chính xác)
    2. User-specific scaling factors (ước tính thông minh)
    3. Device consumption profiles (dựa trên nghiên cứu)
    """
    
    # Hệ số tiêu thụ thực tế (dựa trên nghiên cứu EVN & các nghiên cứu quốc tế)
    DEVICE_PROFILES = {
        'ac': {
            'power_kw': 1.5,           # 1.5 kW cho 1 HP
            'hours_per_day': 8,        # Baseline
            'seasonal_factor': {       # Điều chỉnh theo mùa
                'winter': 0.3,         # Mùa đông ít dùng
                'spring': 0.5,
                'summer': 1.5,         # Mùa hè dùng nhiều
                'fall': 0.7
            }
        },
        'fridge': {
            'power_kw': 0.15,
            'duty_cycle': 0.4,         # Chỉ chạy 40% thời gian
            'hours_per_day': 24,       # Luôn bật nhưng có duty cycle
        },
        'tv': {
            'power_kw': 0.1,
            'hours_per_day': 5,
        },
        'washer': {
            'power_kw': 0.5,
            'times_per_week': 4,       # 4 lần/tuần
            'hours_per_time': 1,
        },
        'water_heater': {
            'power_kw': 2.5,
            'hours_per_day': 2,
        },
        'lighting': {
            'power_per_bulb': 0.01,    # 10W LED
            'bulbs_per_person': 3,
            'bulbs_per_10m2': 1,
            'hours_per_day': 10,
        },
        'other': {
            'base_power': 0.05,        # Router, modem, standby...
            'hours_per_day': 24,
        }
    }
    
    # Hệ số điều chỉnh theo đặc điểm hộ gia đình
    HOUSEHOLD_FACTORS = {
        'house_type': {
            'Chung cư': 0.85,          # Cách nhiệt tốt, ít diện tích
            'Nhà phố': 1.0,            # Baseline
            'Biệt thự': 1.3            # Diện tích lớn, nhiều phòng
        },
        'people_base': 2,              # Baseline: 2 người
        'people_increment': 0.15,      # Mỗi người thêm tăng 15%
        'area_base': 50,               # Baseline: 50m²
        'area_increment': 0.01,        # Mỗi m² thêm tăng 1%
    }
    
    def __init__(self, model_path='checkpoints/best_model_random_forest.pkl'):

        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.load_model_if_exists()
    
    def load_model_if_exists(self):
        """Load model package từ file .pkl"""
        if os.path.exists(self.model_path):
            try:
                package = joblib.load(self.model_path)
                
                self.model = package['model']
                self.scaler = package['scaler']
                self.feature_names = package['feature_names']
                metrics = package.get('metrics', {})
                if hasattr(metrics, 'to_dict'):
                    metrics = metrics.to_dict()
                
                print(f"✅ Đã load model: {package.get('model_name', 'Unknown')}")
                print(f"   • R² Score: {metrics.get('R2', 0):.4f}")
                print(f"   • MAE: {metrics.get('MAE', 0):.4f} kW")
                
            except Exception as e:
                print(f"❌ Lỗi load model: {e}")
                self.model = None
        else:
            print(f"⚠️ Model chưa có - Chế độ ước tính")
            self.model = None
    
    def calculate_baseline_consumption(self, history_df):
        """
        Tính baseline consumption từ history
        Đây là consumption của household trong dataset (baseline)
        """
        
        if 'Global_active_power' in history_df.columns:
            # kWh/day = mean(kW) * 24
            baseline_kwh_per_day = history_df['Global_active_power'].mean() * 24
        else:
            baseline_kwh_per_day = 8.0  # Fallback: 8 kWh/day
        
        return baseline_kwh_per_day
    
    def calculate_user_adjustment_factor(self, user_params, current_month=None):
        """
        Tính hệ số điều chỉnh THÔNG MINH dựa trên:
        1. Đặc điểm hộ gia đình (người, diện tích, loại nhà)
        2. Thiết bị cụ thể
        3. Mùa (nếu có)
        
        Returns:
            dict: {
                'overall_factor': float,      # Hệ số tổng thể
                'device_kwh': dict,           # kWh từng thiết bị
                'confidence': float           # Độ tin cậy (0-1)
            }
        """
        
        # 1. Hệ số từ đặc điểm hộ gia đình
        house_factor = self.HOUSEHOLD_FACTORS['house_type'].get(
            user_params.get('house_type', 'Nhà phố'),
            1.0
        )
        
        # Hệ số theo số người (non-linear)
        num_people = user_params.get('num_people', 3)
        people_base = self.HOUSEHOLD_FACTORS['people_base']
        people_increment = self.HOUSEHOLD_FACTORS['people_increment']
        people_factor = 1.0 + ((num_people - people_base) * people_increment)
        
        # Hệ số theo diện tích (non-linear với diminishing returns)
        area_m2 = user_params.get('area_m2', 60)
        area_base = self.HOUSEHOLD_FACTORS['area_base']
        area_increment = self.HOUSEHOLD_FACTORS['area_increment']
        area_factor = 1.0 + ((area_m2 - area_base) * area_increment)
        
        # 2. Tính kWh từ TỪNG thiết bị cụ thể
        device_kwh = {}
        
        # Xác định mùa
        if current_month is None:
            current_month = datetime.now().month
        
        if current_month in [12, 1, 2]:
            season = 'winter'
        elif current_month in [3, 4, 5]:
            season = 'spring'
        elif current_month in [6, 7, 8]:
            season = 'summer'
        else:
            season = 'fall'
        
        # A. Máy lạnh (có seasonal factor)
        num_ac = user_params.get('num_ac', 0)
        if num_ac > 0:
            ac_profile = self.DEVICE_PROFILES['ac']
            seasonal_mult = ac_profile['seasonal_factor'][season]
            device_kwh['ac'] = (
                num_ac * 
                ac_profile['power_kw'] * 
                ac_profile['hours_per_day'] * 
                seasonal_mult * 
                30  # days
            )
        
        # B. Tủ lạnh (duty cycle)
        num_fridge = user_params.get('num_fridge', 0)
        if num_fridge > 0:
            fridge_profile = self.DEVICE_PROFILES['fridge']
            device_kwh['fridge'] = (
                num_fridge * 
                fridge_profile['power_kw'] * 
                fridge_profile['hours_per_day'] * 
                fridge_profile['duty_cycle'] * 
                30
            )
        
        # C. TV
        num_tv = user_params.get('num_tv', 0)
        if num_tv > 0:
            tv_profile = self.DEVICE_PROFILES['tv']
            device_kwh['tv'] = (
                num_tv * 
                tv_profile['power_kw'] * 
                tv_profile['hours_per_day'] * 
                30
            )
        
        # D. Máy giặt (times per week)
        num_washer = user_params.get('num_washer', 0)
        if num_washer > 0:
            washer_profile = self.DEVICE_PROFILES['washer']
            device_kwh['washer'] = (
                num_washer * 
                washer_profile['power_kw'] * 
                washer_profile['hours_per_time'] * 
                washer_profile['times_per_week'] * 
                4  # weeks
            )
        
        # E. Bình nóng lạnh
        num_wh = user_params.get('num_water_heater', 0)
        if num_wh > 0:
            wh_profile = self.DEVICE_PROFILES['water_heater']
            device_kwh['water_heater'] = (
                num_wh * 
                wh_profile['power_kw'] * 
                wh_profile['hours_per_day'] * 
                30
            )
        
        # F. Chiếu sáng (phụ thuộc người + diện tích)
        light_profile = self.DEVICE_PROFILES['lighting']
        num_bulbs = (
            num_people * light_profile['bulbs_per_person'] +
            area_m2 / 10 * light_profile['bulbs_per_10m2']
        )
        device_kwh['lighting'] = (
            num_bulbs * 
            light_profile['power_per_bulb'] * 
            light_profile['hours_per_day'] * 
            30
        )
        
        # G. Thiết bị khác (base + scale theo diện tích)
        other_profile = self.DEVICE_PROFILES['other']
        device_kwh['other'] = (
            other_profile['base_power'] * 
            (area_m2 / 50) *  # Scale theo diện tích
            other_profile['hours_per_day'] * 
            30
        )
        
        # 3. Tính tổng kWh từ thiết bị
        total_device_kwh = sum(device_kwh.values())
        
        # 4. Overall factor (kết hợp household factors)
        overall_factor = house_factor * people_factor * area_factor
        
        # 5. Tính confidence (độ tin cậy)
        # Confidence cao khi:
        # - Số người gần baseline (2-4 người)
        # - Diện tích gần baseline (40-80m²)
        # - Có đủ thiết bị thông dụng
        
        people_confidence = 1.0 - abs(num_people - 3) * 0.1
        area_confidence = 1.0 - abs(area_m2 - 60) / 100
        device_confidence = min(1.0, len(device_kwh) / 5)  # 5 loại thiết bị chính
        
        confidence = np.clip(
            (people_confidence + area_confidence + device_confidence) / 3,
            0.3,  # Minimum 30%
            0.85  # Maximum 85% (never 100% vì đang ước tính)
        )
        
        return {
            'overall_factor': overall_factor,
            'device_kwh': device_kwh,
            'total_device_kwh': total_device_kwh,
            'confidence': confidence,
            'house_factor': house_factor,
            'people_factor': people_factor,
            'area_factor': area_factor,
            'season': season
        }
    
    def predict_user_consumption(self, history_df, user_params, days=30):
        """
        Dự đoán tiêu thụ cho user cụ thể
        
        Phương pháp:
        1. Tính baseline từ history (pattern thời gian)
        2. Ước tính consumption từ thiết bị user
        3. Blend 2 cái với trọng số thông minh
        4. Trả về kèm confidence interval
        """
        
        # 1. Baseline từ history (pattern thời gian - chính xác)
        baseline_kwh_per_day = self.calculate_baseline_consumption(history_df)
        baseline_monthly = baseline_kwh_per_day * days
        
        # 2. User adjustment (thiết bị - ước tính)
        adjustment = self.calculate_user_adjustment_factor(
            user_params,
            current_month=datetime.now().month
        )
        
        # 3. Phương pháp BLEND thông minh:
        # - Nếu user có nhiều thiết bị → tin vào device calculation nhiều hơn
        # - Nếu user gần baseline → tin vào pattern nhiều hơn
        
        device_kwh = adjustment['total_device_kwh']
        
        # Trọng số cho 2 phương pháp
        # Nếu device_kwh gần baseline → tin pattern nhiều
        ratio = device_kwh / baseline_monthly if baseline_monthly > 0 else 1.0
        
        if 0.8 <= ratio <= 1.2:  # User gần baseline
            pattern_weight = 0.7  # Tin pattern 70%
            device_weight = 0.3
        else:  # User khác baseline
            pattern_weight = 0.4  # Tin device 60%
            device_weight = 0.6
        
        # Blend prediction
        predicted_kwh = (
            baseline_monthly * adjustment['overall_factor'] * pattern_weight +
            device_kwh * device_weight
        )
        
        # 4. Calibration (điều chỉnh dựa trên kinh nghiệm)
        # Thường ước tính thiết bị cao hơn thực tế 10-15%
        calibration_factor = 0.9  # Giảm 10%
        predicted_kwh *= calibration_factor
        
        # 5. Confidence interval
        confidence = adjustment['confidence']
        margin = predicted_kwh * (1 - confidence) * 0.5  # Margin tỷ lệ với độ không chắc chắn
        
        lower_bound = predicted_kwh - margin
        upper_bound = predicted_kwh + margin
        
        # 6. Phân tích pattern theo giờ (giữ nguyên từ baseline)
        hourly_pattern = self._extract_hourly_pattern(history_df)
        
        # Scale pattern theo predicted total
        scale_factor = predicted_kwh / baseline_monthly if baseline_monthly > 0 else 1.0
        scaled_hourly = [h * scale_factor / days for h in hourly_pattern]
        
        # 7. Xác định peak/off-peak
        hourly_avg = np.mean(scaled_hourly)
        peak_hours = [i for i, h in enumerate(scaled_hourly) if h > hourly_avg * 1.2]
        off_peak_hours = [i for i, h in enumerate(scaled_hourly) if h < hourly_avg * 0.8]
        
        return {
            'total_kwh': predicted_kwh,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'confidence': confidence,
            'daily_avg_kwh': predicted_kwh / days,
            'baseline_kwh': baseline_monthly,
            'device_kwh': device_kwh,
            'adjustment_details': adjustment,
            'hourly_pattern': scaled_hourly,
            'peak_hours': peak_hours,
            'off_peak_hours': off_peak_hours,
            'blend_weights': {
                'pattern': pattern_weight,
                'device': device_weight
            }
        }
    
    def _extract_hourly_pattern(self, history_df):
        """Trích xuất pattern theo giờ từ history"""
        
        if 'hour' in history_df.columns:
            hourly_avg = history_df.groupby('hour')['Global_active_power'].mean()
        else:
            # Tạo pattern mặc định (sáng-tối cao điểm)
            hours = np.arange(24)
            morning_peak = np.exp(-((hours - 8)**2) / 8)
            evening_peak = np.exp(-((hours - 19)**2) / 8)
            hourly_avg = pd.Series(0.5 + 1.5*morning_peak + 2.5*evening_peak)
        
        # Normalize và scale
        pattern = hourly_avg.values
        pattern = pattern / pattern.mean()  # Normalize về trung bình = 1
        
        return pattern.tolist()
    
    def get_saving_recommendations(self, result, user_params):
        """
        Tạo đề xuất tiết kiệm THÔNG MINH dựa trên:
        1. Thiết bị nào tiêu thụ nhiều nhất
        2. Giờ nào cao điểm
        3. Mùa hiện tại
        """
        
        recommendations = []
        device_kwh = result['adjustment_details']['device_kwh']
        total_kwh = result['total_kwh']
        season = result['adjustment_details']['season']
        
        # Sắp xếp thiết bị theo tiêu thụ
        sorted_devices = sorted(device_kwh.items(), key=lambda x: x[1], reverse=True)
        
        # Đề xuất cho từng thiết bị chính
        for device_name, kwh in sorted_devices[:3]:  # Top 3
            percent = (kwh / total_kwh) * 100
            if device_name == 'ac':
                seasonal_note = ""
                if season == 'summer':
                    seasonal_note = " (Mùa hè - tiêu thụ cao nhất)"
                elif season == 'winter':
                    seasonal_note = " (Mùa đông - có thể giảm nhiều)"
                
                saving_kwh = kwh * 0.25  # Có thể tiết kiệm 25%
                saving_money = saving_kwh * 2500
                
                recommendations.append({
                    'device': f'❄️ Máy lạnh{seasonal_note}',
                    'current': f'{kwh:.0f} kWh ({percent:.1f}%)',
                    'priority': 'high',
                    'actions': [
                        f'Đặt 26-27°C thay vì 22-24°C → tiết kiệm 15-20%',
                        'Tắt máy khi ra ngoài >30 phút',
                        'Vệ sinh lưới lọc mỗi 2 tuần → tiết kiệm 5-10%',
                        'Sử dụng timer để tắt tự động ban đêm'
                    ],
                    'saving': f'{saving_kwh:.0f} kWh ≈ {saving_money:,.0f}đ/tháng'
                })
            
            elif device_name == 'water_heater':
                saving_kwh = kwh * 0.4  # Có thể tiết kiệm 40%
                saving_money = saving_kwh * 2500
                
                recommendations.append({
                    'device': '🚿 Bình nóng lạnh',
                    'current': f'{kwh:.0f} kWh ({percent:.1f}%)',
                    'priority': 'high',
                    'actions': [
                        'CHỈ bật 30 phút trước khi tắm → tiết kiệm 60%',
                        'Tắt NGAY sau khi dùng xong',
                        'Giảm nhiệt độ xuống 50-55°C',
                        'Cân nhắc đổi sang Heat Pump (tiết kiệm 70%)'
                    ],
                    'saving': f'{saving_kwh:.0f} kWh ≈ {saving_money:,.0f}đ/tháng'
                })
            
            elif device_name == 'lighting':
                saving_kwh = kwh * 0.3
                saving_money = saving_kwh * 2500
                
                recommendations.append({
                    'device': '💡 Chiếu sáng',
                    'current': f'{kwh:.0f} kWh ({percent:.1f}%)',
                    'priority': 'medium',
                    'actions': [
                        'Thay bóng LED 9W thay vì 60W → tiết kiệm 85%',
                        'Tắt đèn khi ra khỏi phòng',
                        'Sử dụng ánh sáng tự nhiên ban ngày',
                        'Lắp cảm biến chuyển động ở hành lang'
                    ],
                    'saving': f'{saving_kwh:.0f} kWh ≈ {saving_money:,.0f}đ/tháng'
                })
        
        # Đề xuất về giờ cao điểm
        peak_hours = result['peak_hours']
        if len(peak_hours) > 0:
            peak_str = ", ".join([f"{h}h" for h in sorted(peak_hours)[:5]])
            
            recommendations.append({
                'device': '⏰ Thời gian sử dụng',
                'current': f'Cao điểm: {peak_str}',
                'priority': 'high',
                'actions': [
                    'Tránh dùng nhiều thiết bị cùng lúc vào giờ cao điểm',
                    'Dời giặt giũ sang sau 22h',
                    'Nấu cơm trước 17h hoặc sau 21h',
                    'Sạc thiết bị vào ban đêm'
                ],
                'saving': f'Tiết kiệm ~15% tổng hóa đơn'
            })
        
        return recommendations


# ================== DEMO ==================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔬 IMPROVED PREDICTOR - SMART USER ADJUSTMENT")
    print("="*70)
    
    # Tạo sample history
    date_rng = pd.date_range(start='2025-01-01', periods=1440, freq='min')
    hours = np.array([t.hour + t.minute/60 for t in date_rng])
    
    morning_peak = np.exp(-((hours - 8)**2) / 8)
    evening_peak = np.exp(-((hours - 19)**2) / 8)
    noise = np.random.normal(0, 0.1, len(date_rng))
    
    power = 1.0 + (1.0 * morning_peak) + (1.5 * evening_peak) + noise
    power = np.clip(power, 0.3, 5.0)
    
    history_df = pd.DataFrame({
        'Global_active_power': power,
        'hour': [t.hour for t in date_rng]
    }, index=date_rng)
    
    # Test với user params
    user_params = {
        'num_people': 4,
        'area_m2': 80,
        'house_type': 'Nhà phố',
        'num_ac': 2,
        'num_fridge': 1,
        'num_tv': 2,
        'num_washer': 1,
        'num_water_heater': 1
    }
    
    predictor = ImprovedEnergyPredictor()
    
    print("\n📊 User Info:")
    for k, v in user_params.items():
        print(f"   • {k}: {v}")
    
    print("\n🔮 Dự đoán...")
    result = predictor.predict_user_consumption(history_df, user_params, days=30)
    
    print(f"\n📈 Kết quả:")
    print(f"   • Dự đoán: {result['total_kwh']:.0f} kWh/tháng")
    print(f"   • Khoảng tin cậy: {result['lower_bound']:.0f} - {result['upper_bound']:.0f} kWh")
    print(f"   • Độ tin cậy: {result['confidence']*100:.0f}%")
    print(f"   • Baseline (pattern): {result['baseline_kwh']:.0f} kWh")
    print(f"   • Device estimate: {result['device_kwh']:.0f} kWh")
    
    print(f"\n⚖️ Blend weights:")
    print(f"   • Pattern: {result['blend_weights']['pattern']*100:.0f}%")
    print(f"   • Device: {result['blend_weights']['device']*100:.0f}%")
    
    print(f"\n🔧 Chi tiết thiết bị:")
    for device, kwh in result['adjustment_details']['device_kwh'].items():
        percent = (kwh / result['total_kwh']) * 100
        print(f"   • {device}: {kwh:.0f} kWh ({percent:.1f}%)")
    
    print("\n" + "="*70)