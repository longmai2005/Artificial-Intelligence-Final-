"""
Improved Energy Predictor - Smart User Adjustment
Tích hợp AI RandomForest vào dự báo tiêu thụ hàng tháng
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
    1. AI Prediction (RandomForest) - Nếu có model
    2. Time pattern from history (Baseline fallback)
    3. User-specific scaling factors (Heuristic)
    """
    
    # Hệ số tiêu thụ thực tế
    DEVICE_PROFILES = {
        'ac': {'power_kw': 1.5, 'hours_per_day': 8, 'seasonal_factor': {'winter': 0.3, 'spring': 0.5, 'summer': 1.5, 'fall': 0.7}},
        'fridge': {'power_kw': 0.15, 'duty_cycle': 0.4, 'hours_per_day': 24},
        'tv': {'power_kw': 0.1, 'hours_per_day': 5},
        'washer': {'power_kw': 0.5, 'times_per_week': 4, 'hours_per_time': 1},
        'water_heater': {'power_kw': 2.5, 'hours_per_day': 2},
        'lighting': {'power_per_bulb': 0.01, 'bulbs_per_person': 3, 'bulbs_per_10m2': 1, 'hours_per_day': 10},
        'other': {'base_power': 0.05, 'hours_per_day': 24}
    }
    
    HOUSEHOLD_FACTORS = {
        'house_type': {'Chung cư': 0.85, 'Nhà phố': 1.0, 'Biệt thự': 1.3},
        'people_base': 2, 'people_increment': 0.15,
        'area_base': 50, 'area_increment': 0.01
    }
    
    def __init__(self, model_path='checkpoints/best_model_random_forest.pkl'):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.load_model_if_exists()
    
    def load_model_if_exists(self):
        """Load package chứa model, scaler và feature names"""
        if os.path.exists(self.model_path):
            try:
                package = joblib.load(self.model_path)
                # Truy xuất từ dict package
                self.model = package['model']
                self.scaler = package['scaler']
                self.feature_names = package['feature_names']
                print(f"✅ AI Ready: Đã tích hợp mô hình {package.get('model_name', 'Random Forest')}")
            except Exception as e:
                print(f"❌ Lỗi load model package: {e}")
                self.model = None
        else:
            print(f"⚠️ Không tìm thấy model tại {self.model_path} - Chạy chế độ Heuristic")
            self.model = None

    def predict_next_24h(self, last_sequence):
        """Dự báo 24 giờ tới sử dụng model AI thật"""
        if self.model is None:
            return np.full(24, np.mean(last_sequence))

        try:
            now = datetime.now()
            predictions = []
            for i in range(1, 25):
                future_time = now + timedelta(hours=i)
                feat_dict = {
                    'hour': future_time.hour,
                    'day_of_week': future_time.weekday(),
                    'month': future_time.month,
                    'lag_24h': last_sequence[i-1] if i <= len(last_sequence) else last_sequence[-1]
                }
                X_df = pd.DataFrame([feat_dict])
                if self.feature_names:
                    for col in self.feature_names:
                        if col not in X_df.columns: X_df[col] = 0
                    X_df = X_df[self.feature_names]
                
                X_scaled = self.scaler.transform(X_df)
                pred = self.model.predict(X_scaled)[0]
                predictions.append(max(0.1, pred))
            return np.array(predictions)
        except Exception as e:
            print(f"❌ Lỗi AI Predict: {e}")
            return last_sequence

    def calculate_baseline_consumption(self, history_df):
        """Tính baseline từ dữ liệu lịch sử (Fallback)"""
        if 'Global_active_power' in history_df.columns:
            return history_df['Global_active_power'].mean() * 24
        return 8.0

    def calculate_user_adjustment_factor(self, user_params, current_month=None):
        """
        Tính các hệ số điều chỉnh dựa trên thiết bị (Heuristic) 
        với logic Confidence đã được tối ưu cho thông tin đầu vào lớn.
        """
        house_factor = self.HOUSEHOLD_FACTORS['house_type'].get(user_params.get('house_type', 'Nhà phố'), 1.0)
        
        # 1. Tính toán Factor 
        num_people = user_params.get('num_people', 3)
        people_factor = 1.0 + ((num_people - self.HOUSEHOLD_FACTORS['people_base']) * self.HOUSEHOLD_FACTORS['people_increment'])
        
        area_m2 = user_params.get('area_m2', 60)
        area_factor = 1.0 + ((area_m2 - self.HOUSEHOLD_FACTORS['area_base']) * self.HOUSEHOLD_FACTORS['area_increment'])
        
        device_kwh = {}
        month = current_month or datetime.now().month
        season = 'summer' if month in [6,7,8] else 'winter' if month in [12,1,2] else 'spring'
        
        # Tính toán tiêu thụ thiết bị
        num_ac = user_params.get('num_ac', 0)
        ac_profile = self.DEVICE_PROFILES['ac']
        device_kwh['Máy lạnh'] = num_ac * ac_profile['power_kw'] * ac_profile['hours_per_day'] * ac_profile['seasonal_factor'][season] * 30
        device_kwh['Tủ lạnh'] = user_params.get('num_fridge', 1) * 0.15 * 24 * 0.4 * 30
        device_kwh['TV'] = user_params.get('num_tv', 0) * self.DEVICE_PROFILES['tv']['power_kw'] * self.DEVICE_PROFILES['tv']['hours_per_day'] * 30
        washer = self.DEVICE_PROFILES['washer']
        device_kwh['Máy giặt'] = user_params.get('num_washer', 0) * washer['power_kw'] * washer['times_per_week'] * washer['hours_per_time'] * 4
        device_kwh['Bình nóng lạnh'] = user_params.get('num_water_heater', 0) * self.DEVICE_PROFILES['water_heater']['power_kw'] * self.DEVICE_PROFILES['water_heater']['hours_per_day'] * 30
        
        total_device_kwh = sum(device_kwh.values())

        # A. Độ tin cậy theo số người: Coi là tin cậy 100% nếu từ 1 đến 6 người
        if 1 <= num_people <= 6:
            people_conf = 1.0
        else:
            # Nếu vượt quá 6 người, chỉ trừ rất nhẹ (2% mỗi người dư ra)
            people_conf = max(0.8, 1.0 - abs(num_people - 6) * 0.02)

        # B. Độ tin cậy theo diện tích: Coi là tin cậy 100% nếu từ 25m2 đến 150m2
        if 25 <= area_m2 <= 150:
            area_conf = 1.0
        else:
            # Nếu diện tích cực lớn (vượt 150m2), trừ nhẹ (1% cho mỗi 20m2 dư ra)
            area_conf = max(0.8, 1.0 - abs(area_m2 - 150) / 200)

        # C. Độ tin cậy tổng hợp
        # Cộng thêm 10% bonus nếu AI model đã được load thành công (self.model không phải None)
        model_bonus = 0.1 if self.model is not None else 0.0
        
        raw_confidence = (people_conf + area_conf) / 2
        confidence = np.clip(raw_confidence + model_bonus, 0.6, 0.95) 
        # Giới hạn luôn từ 60% đến 95% để người dùng không thấy kết quả "vô dụng"

        return {
            'overall_factor': house_factor * people_factor * area_factor,
            'device_kwh': device_kwh,
            'total_device_kwh': total_device_kwh,
            'confidence': confidence,
            'season': season
        }
    def predict_user_consumption(self, history_df, user_params, days=30):
        """
        DỰ BÁO CHÍNH: Kết hợp AI RandomForest và Heuristic
        """
        # --- BƯỚC 1: LẤY BASELINE 
        ai_forecast_daily_kwh = None
        if self.model is not None:
            try:
                # Lấy 24h gần nhất từ history làm đầu vào AI
                last_24h_data = history_df['Global_active_power'].values[-24:]
                forecast_24h = self.predict_next_24h(last_24h_data)
                ai_forecast_daily_kwh = np.sum(forecast_24h) 
                print(f"🤖 AI Forecast (24h): {ai_forecast_daily_kwh:.2f} kWh")
            except:
                pass

        # Fallback về baseline lịch sử nếu AI lỗi hoặc không có model
        history_baseline_daily = self.calculate_baseline_consumption(history_df)
        
        # Baseline sử dụng để tính toán tháng
        effective_baseline_daily = ai_forecast_daily_kwh if ai_forecast_daily_kwh else history_baseline_daily
        baseline_monthly = effective_baseline_daily * days
        
        # --- BƯỚC 2: TÍNH TOÁN USER ADJUSTMENT (Thiết bị) ---
        adjustment = self.calculate_user_adjustment_factor(user_params)
        device_monthly = adjustment['total_device_kwh']
        
        # --- BƯỚC 3: BLEND (Trộn AI và Heuristic) ---
        # Tính độ lệch giữa AI và Khai báo người dùng
        ratio = device_monthly / baseline_monthly if baseline_monthly > 0 else 1.0
        # Trọng số linh hoạt: Càng gần 1.0 thì càng tin Pattern (AI), càng lệch xa càng tin Device
        diff = abs(1.0 - ratio)
        
        # pattern_weight sẽ chạy từ 0.3 đến 0.8 tùy vào độ khớp dữ liệu
        pattern_weight = max(0.3, min(0.8, 1.0 - diff)) 
        device_weight = 1.0 - pattern_weight
        # Kết quả dự báo thô
        raw_predicted_kwh = (baseline_monthly * pattern_weight) + (device_monthly * device_weight)
        # Áp dụng Calibration 0.9 (Hệ số thực tế hóa)
        predicted_kwh = raw_predicted_kwh * 0.9
        
        # --- BƯỚC 4: KẾT QUẢ ---
        raw_shape = self._extract_hourly_pattern(history_df)
        # Tính mức kWh trung bình mỗi giờ dựa trên dự báo mới
        avg_hourly_kwh = (predicted_kwh / days) / 24
        # Nhân hình dạng với mức trung bình để ra pattern thực tế
        scaled_pattern = [val * avg_hourly_kwh for val in raw_shape]
        
        confidence = adjustment['confidence']
        margin = predicted_kwh * (1 - confidence) * 0.5
        
        return {
            'total_kwh': predicted_kwh,
            'lower_bound': predicted_kwh - margin,
            'upper_bound': predicted_kwh + margin,
            'confidence': confidence,
            'daily_avg_kwh': predicted_kwh / days,
            'ai_used': self.model is not None,
            'device_kwh': device_monthly,
            'baseline_kwh': baseline_monthly,
            'adjustment_details': adjustment,
            'hourly_pattern': scaled_pattern,
            'blend_weights': {
                'pattern': pattern_weight,
                'device': device_weight
            },
            'peak_hours': [i for i, h in enumerate(self._extract_hourly_pattern(history_df)) if h > 1.2]
        }

    def _extract_hourly_pattern(self, history_df):
        """Trích xuất pattern tiêu thụ thực tế từ dữ liệu lịch sử"""
        try:
            # Kiểm tra nếu chưa có cột 'hour', tạo từ index (nếu index là datetime)
            df = history_df.copy()
            if 'hour' not in df.columns:
                df['hour'] = df.index.hour
                
            if 'Global_active_power' in df.columns:
                # Tính giá trị trung bình tiêu thụ cho mỗi khung giờ (0-23h)
                hourly_avg = df.groupby('hour')['Global_active_power'].mean()
                # Đảm bảo đủ 24 giờ, điền 0 nếu giờ đó không có dữ liệu
                pattern = hourly_avg.reindex(range(24), fill_value=0).values
                
                # Chuẩn hóa: Nếu hoàn toàn không có dữ liệu, trả về mức cơ bản 0.5
                if pattern.sum() == 0:
                    return [0.5] * 24
                    
                return pattern.tolist()
        except Exception as e:
            print(f"⚠️ Lỗi trích xuất pattern: {e}")
            
        # Fallback: Trả về mức tiêu thụ mặc định
        return [0.5, 0.4, 0.3, 0.3, 0.4, 0.6, 1.2, 1.5, 1.0, 0.8, 0.7, 0.7, 
                0.8, 0.9, 0.8, 0.9, 1.1, 1.8, 2.2, 2.1, 1.5, 1.0, 0.7, 0.6]
    
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
ImprovedEnergyPredictor = EnergyPredictor
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

