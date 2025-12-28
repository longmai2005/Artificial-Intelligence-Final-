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
    # CẬP NHẬT TRONG predictor.py
    DEVICE_PROFILES = {
        'ac': {'power_kw': 0.8, 'hours_per_day': 8, 'seasonal_factor': {'winter': 0.2, 'spring': 0.4, 'summer': 1.8, 'fall': 0.8}},
        'fridge': {'power_kw': 0.1, 'duty_cycle': 0.35, 'hours_per_day': 24},
        'tv': {'power_kw': 0.15, 'hours_per_day': 4},
        'washer': {'power_kw': 0.8, 'times_per_week': 4, 'hours_per_time': 1.5},
        'water_heater': {'power_kw': 2.5, 'hours_per_day': 0.5}, # Thực tế chỉ bật 15-30p là đủ nóng
        'lighting': {'power_per_bulb': 0.009, 'bulbs_per_person': 4, 'bulbs_per_10m2': 1.5, 'hours_per_day': 6},
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
        if os.path.exists(self.model_path):
            try:
                package = joblib.load(self.model_path)
                self.model = package['model']
                self.scaler = package['scaler']
                self.feature_names = package['feature_names']
                print(f"✅ AI Loaded: {package.get('model_name')}")
            except: self.model = None
        else: self.model = None

    def predict_next_24h_sum(self, last_sequence):
        """Chỉ trả về TỔNG kWh của 24h tiếp theo (Không cần chi tiết từng giờ để vẽ)"""
        if self.model is None:
            return np.mean(last_sequence) * 24 if len(last_sequence) > 0 else 8.0

        try:
            now = datetime.now()
            daily_sum = 0
            avg_val = np.mean(last_sequence) if len(last_sequence) > 0 else 0.5
            
            for i in range(1, 25):
                future_time = now + timedelta(hours=i)
                # Logic Lag & Season (Giữ nguyên vì nó giúp AI chính xác)
                lag_24 = last_sequence[i-1] if i <= len(last_sequence) else avg_val
                
                weekday = future_time.weekday()
                lag_7d = lag_24 * (1.15 if weekday == 5 else (0.85 if weekday == 0 else 1.0))
                
                m = future_time.month
                if m in [12, 1, 2]: season = 0
                elif m in [3, 4, 5]: season = 1
                elif m in [6, 7, 8]: season = 2
                else: season = 3
                
                # Tạo input
                feat_dict = {
                    'hour': future_time.hour, 'weekday': weekday, 'month': m,
                    'season': season, 'lag_24h': lag_24, 'lag_7d': lag_7d
                }
                
                # Predict
                X_df = pd.DataFrame([feat_dict])
                if self.feature_names:
                    for col in self.feature_names:
                        if col not in X_df.columns: X_df[col] = 0
                    X_df = X_df[self.feature_names]
                
                pred = self.model.predict(self.scaler.transform(X_df))[0]
                daily_sum += max(0.05, pred)
                
            return daily_sum
        except:
            return np.mean(last_sequence) * 24

    def calculate_baseline_consumption(self, history_df):
        """Tính baseline từ dữ liệu lịch sử (Fallback)"""
        if 'Global_active_power' in history_df.columns:
            return history_df['Global_active_power'].mean() * 24
        return 8.0

    def calculate_user_adjustment_factor(self, user_params, days=30):
        """
        Tính toán tiêu thụ dựa trên thiết bị người dùng khai báo.
        Đã cập nhật công suất chuẩn 2025 (Inverter/LED).
        """
        # 1. Hệ số Nhà & Con người
        house_factor = self.HOUSEHOLD_FACTORS['house_type'].get(user_params.get('house_type', 'Nhà phố'), 1.0)
        
        num_people = user_params.get('num_people', 3)
        people_factor = 1.0 + ((num_people - self.HOUSEHOLD_FACTORS['people_base']) * self.HOUSEHOLD_FACTORS['people_increment'])
        
        area_m2 = user_params.get('area_m2', 60)
        area_factor = 1.0 + ((area_m2 - self.HOUSEHOLD_FACTORS['area_base']) * self.HOUSEHOLD_FACTORS['area_increment'])
        
        # 2. Xác định Mùa (để tính Máy lạnh)
        month = user_params.get('month', datetime.now().month)
        if month in [5, 6, 7, 8]: season = 'summer'
        elif month in [11, 12, 1, 2]: season = 'winter'
        elif month in [3, 4]: season = 'spring'
        else: season = 'fall'

        # 3. Tính toán từng thiết bị (Lưu ý: Luôn nhân với days)
        device_kwh = {}
        
        # [A] Máy lạnh (AC): Công suất 0.8kW (Inverter), chạy 8h/ngày
        # Nhân hệ số mùa: Mùa hè (1.8) tốn hơn nhiều so với mùa đông (0.2)
        ac_profile = self.DEVICE_PROFILES['ac']
        num_ac = user_params.get('num_ac', 0)
        season_factor = ac_profile['seasonal_factor'].get(season, 1.0)
        device_kwh['Máy lạnh'] = num_ac * ac_profile['power_kw'] * ac_profile['hours_per_day'] * season_factor * days
        
        # [B] Tủ lạnh: 0.1kW * 24h * 0.35 (Duty cycle - chạy ngắt quãng)
        fridge_profile = self.DEVICE_PROFILES['fridge']
        device_kwh['Tủ lạnh'] = user_params.get('num_fridge', 1) * fridge_profile['power_kw'] * 24 * fridge_profile['duty_cycle'] * days
        
        # [C] TV: 0.15kW * 4h/ngày
        tv_profile = self.DEVICE_PROFILES['tv']
        device_kwh['TV'] = user_params.get('num_tv', 0) * tv_profile['power_kw'] * tv_profile['hours_per_day'] * days
        
        # [D] Máy giặt: 0.8kW * 1.5h/lần * 4 lần/tuần
        # Quy đổi ra ngày: (4 lần / 7 ngày)
        washer = self.DEVICE_PROFILES['washer']
        washer_daily_avg = washer['times_per_week'] / 7
        device_kwh['Máy giặt'] = user_params.get('num_washer', 0) * washer['power_kw'] * washer_daily_avg * washer['hours_per_time'] * days
        
        # [E] Bình nóng lạnh: 2.5kW * 0.5h/ngày (chỉ bật lúc tắm)
        heater = self.DEVICE_PROFILES['water_heater']
        device_kwh['Bình nóng lạnh'] = user_params.get('num_water_heater', 0) * heater['power_kw'] * heater['hours_per_day'] * days
        
        # [F] Chiếu sáng (LED): Giả định 4 bóng/người, dùng 6h/ngày
        lighting = self.DEVICE_PROFILES['lighting']
        total_bulbs = num_people * lighting['bulbs_per_person']
        device_kwh['Chiếu sáng'] = total_bulbs * lighting['power_per_bulb'] * lighting['hours_per_day'] * days
        
        # [G] Khác (Wifi, Sạc, Quạt...): Base load 0.1kW chạy 24/24
        other = self.DEVICE_PROFILES['other']
        device_kwh['Wifi, Quạt & Khác'] = other['base_power'] * other['hours_per_day'] * days

        # Tổng hợp
        total_device_kwh = sum(device_kwh.values())

        # 4. Tính độ tin cậy (Confidence Score)
        base_score = 0.85
        
        # Phạt nếu thiếu thiết bị cơ bản (Nhà >40m2 mà không có Tủ lạnh)
        if user_params.get('num_fridge', 0) == 0 and area_m2 > 40:
            base_score -= 0.15
            
        # Phạt nếu mật độ tiêu thụ quá vô lý (kWh/m2 quá thấp)
        kwh_per_m2 = total_device_kwh / area_m2
        if kwh_per_m2 < 0.5: base_score -= 0.25
        elif kwh_per_m2 < 1.0: base_score -= 0.10
        
        # Thưởng nếu có AI Model
        if self.model is not None: base_score += 0.05
        
        confidence = np.clip(base_score, 0.40, 0.98)
        
        return {
            'overall_factor': house_factor * people_factor * area_factor, # Hệ số điều chỉnh chung
            'total_device_kwh': total_device_kwh,
            'device_kwh': device_kwh,
            'confidence': confidence,
            'season': season
        }
    def predict_user_consumption(self, history_df, user_params, days=30):
        """
        DỰ BÁO CHÍNH: Kết hợp AI RandomForest (30%) và Heuristic (70%)
        """
        # BƯỚC 1: AI FORECAST (Dựa trên pattern quá khứ)
        ai_daily_kwh = 0
        if self.model is not None:
            try:
                # Lấy 24h dữ liệu cuối cùng để làm đầu vào cho AI
                last_24h = history_df['Global_active_power'].values[-24:]
                ai_daily_kwh = self.predict_next_24h_sum(last_24h)
            except: 
                pass
        
        # Fallback nếu AI lỗi: Lấy trung bình lịch sử hoặc mặc định 8kWh/ngày
        if ai_daily_kwh == 0:
            ai_daily_kwh = self.calculate_baseline_consumption(history_df) / 30
            
        ai_monthly_kwh = ai_daily_kwh * days
        
        # BƯỚC 2: DEVICE CALCULATION (Dựa trên thiết bị hiện tại)
        adjustment = self.calculate_user_adjustment_factor(user_params, days=days)
        device_monthly = adjustment['total_device_kwh']
        
        # BƯỚC 3: BLENDING (TRỘN KẾT QUẢ)
        # Growth factor 1.05: Giả định mức sống năm sau cao hơn năm trước 5%
        GROWTH_FACTOR = 1.05 
        
        # Công thức: (AI * 30% * Tăng trưởng) + (Thiết bị * 70%)
        # Sau đó nhân với hệ số Nhà (Biệt thự/Chung cư)
        raw_predicted = ((ai_monthly_kwh * 0.3 * GROWTH_FACTOR) + (device_monthly * 0.7)) * adjustment['overall_factor']
        
        # Calibration: Nhân 0.95 để trừ hao các lúc đi vắng/tiết kiệm
        final_kwh = raw_predicted * 0.95
        
        # Tính khoảng tin cậy (Margin)
        confidence = adjustment['confidence']
        margin = final_kwh * (1 - confidence) * 0.5
        
        return {
            'total_kwh': final_kwh,
            'lower_bound': final_kwh - margin,
            'upper_bound': final_kwh + margin,
            'confidence': confidence,
            'device_kwh': device_monthly, # Dùng để vẽ biểu đồ tròn
            'adjustment_details': adjustment
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
        Tạo danh sách lời khuyên dựa trên thiết bị tiêu thụ nhiều nhất.
        """
        recommendations = []
        device_kwh = result['adjustment_details']['device_kwh']
        season = result['adjustment_details']['season']
        total_kwh = result['total_kwh']
        
        # Sắp xếp thiết bị từ cao xuống thấp
        sorted_devices = sorted(device_kwh.items(), key=lambda x: x[1], reverse=True)
        
        # Lấy Top 3 thiết bị ngốn điện nhất
        for device_name, kwh in sorted_devices[:3]:
            if kwh < 10: continue # Bỏ qua nếu quá nhỏ
            
            percent = (kwh / total_kwh) * 100
            
            # 1. Lời khuyên cho Máy lạnh
            if device_name == 'Máy lạnh':
                note = " (Mùa Hè cao điểm)" if season == 'summer' else ""
                recommendations.append({
                    'device': f'❄️ Máy lạnh{note}',
                    'current': f'{kwh:.0f} kWh ({percent:.1f}%)',
                    'priority': 'high',
                    'actions': [
                        'Đặt nhiệt độ 26-27°C thay vì 20°C (Tiết kiệm 15%)',
                        'Dùng chế độ "Eco" hoặc "Sleep" vào ban đêm',
                        'Vệ sinh lưới lọc bụi (Tiết kiệm 10%)'
                    ],
                    'saving': f'Giảm ~{kwh*0.2:.0f} kWh'
                })
                
            # 2. Lời khuyên cho Bình nóng lạnh
            elif device_name == 'Bình nóng lạnh':
                recommendations.append({
                    'device': '🚿 Bình nóng lạnh',
                    'current': f'{kwh:.0f} kWh ({percent:.1f}%)',
                    'priority': 'high',
                    'actions': [
                        'Bật trước khi tắm 15p rồi TẮT NGAY',
                        'Không bật aptomat 24/24',
                        'Hạ nhiệt độ làm nóng xuống mức trung bình'
                    ],
                    'saving': f'Giảm ~{kwh*0.4:.0f} kWh'
                })
                
            # 3. Lời khuyên cho Tủ lạnh
            elif device_name == 'Tủ lạnh':
                recommendations.append({
                    'device': '🧊 Tủ lạnh',
                    'current': f'{kwh:.0f} kWh ({percent:.1f}%)',
                    'priority': 'medium',
                    'actions': [
                        'Hạn chế mở tủ quá lâu',
                        'Không để thức ăn còn nóng vào tủ',
                        'Kiểm tra gioăng cao su cửa tủ'
                    ],
                    'saving': f'Giảm ~{kwh*0.1:.0f} kWh'
                })

            # 4. Lời khuyên cho Chiếu sáng
            elif device_name == 'Chiếu sáng':
                recommendations.append({
                    'device': '💡 Chiếu sáng',
                    'current': f'{kwh:.0f} kWh ({percent:.1f}%)',
                    'priority': 'low',
                    'actions': [
                        'Thay toàn bộ sang bóng LED',
                        'Tận dụng ánh sáng tự nhiên',
                        'Lắp cảm biến chuyển động ở hành lang'
                    ],
                    'saving': f'Giảm ~{kwh*0.3:.0f} kWh'
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
    
    predictor = EnergyPredictor()
    
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

