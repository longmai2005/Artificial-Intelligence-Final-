import numpy as np
import pandas as pd
import pickle
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class EnergyPredictor:
    def __init__(self, model_path='checkpoints/best_model_lightgbm.pkl'):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.load_model_if_exists()

    def load_model_if_exists(self):
        """Load model package từ file .pkl"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    package = pickle.load(f)
                
                self.model = package['model']
                self.scaler = package['scaler']
                self.feature_names = package['feature_names']
                
                print(f"✅ Đã load model: {package['model_name']}")
                print(f"   • R² Score: {package['metrics']['R2']:.4f}")
                print(f"   • MAE: {package['metrics']['MAE']:.4f} kW")
                print(f"   • Features: {len(self.feature_names)}")
                
            except Exception as e:
                print(f"❌ Lỗi load model: {e}")
                self.model = None
        else:
            print(f"⚠️ Không tìm thấy model tại: {self.model_path}")
            self.model = None

    def create_features_from_history(self, timestamp, history_power=None, 
                                     voltage=240, intensity=None,
                                     sub1=0, sub2=0, sub3=0):
        """
        Tạo features từ timestamp và dữ liệu lịch sử
        
        Args:
            timestamp: Thời điểm cần dự đoán
            history_power: List các giá trị Global_active_power trước đó (tối thiểu 1440 điểm = 24h)
            voltage: Điện áp (V) - mặc định 240V
            intensity: Cường độ dòng điện (A) - tự tính nếu không có
            sub1, sub2, sub3: Giá trị Sub_metering
        
        Returns:
            dict: Features dictionary phù hợp với model
        """
        
        # Tính intensity nếu không có
        if intensity is None and history_power:
            # Công thức: I = P / V
            intensity = history_power[-1] / voltage if voltage > 0 else 0
        elif intensity is None:
            intensity = 1.0
        
        # Xác định season (mùa)
        month = timestamp.month
        if month in [12, 1, 2]:
            season = 3  # Winter (mùa đông)
        elif month in [3, 4, 5]:
            season = 0  # Spring (mùa xuân)
        elif month in [6, 7, 8]:
            season = 1  # Summer (mùa hè)
        else:
            season = 2  # Fall (mùa thu)
        
        # Tính rolling averages
        if history_power and len(history_power) > 0:
            # Đảm bảo có đủ dữ liệu cho rolling
            history = history_power[-1440:] if len(history_power) >= 1440 else history_power
            
            rolling_5 = np.mean(history[-5:]) if len(history) >= 5 else np.mean(history)
            rolling_15 = np.mean(history[-15:]) if len(history) >= 15 else np.mean(history)
            rolling_60 = np.mean(history[-60:]) if len(history) >= 60 else np.mean(history)
            rolling_1440 = np.mean(history[-1440:]) if len(history) >= 1440 else np.mean(history)
            
            # Lấy giá trị hiện tại từ history
            current_power = history[-1]
        else:
            # Giá trị mặc định nếu không có history
            current_power = 1.0
            rolling_5 = rolling_15 = rolling_60 = rolling_1440 = 1.0
        
        # Tạo features dict theo đúng thứ tự của model
        features = {
            'Global_active_power': current_power,
            'Global_reactive_power': current_power * 0.1,  # Ước tính
            'Voltage': voltage,
            'Global_intensity': intensity,
            'Sub_metering_1': sub1,
            'Sub_metering_2': sub2,
            'Sub_metering_3': sub3,
            'hour': timestamp.hour,
            'weekday': timestamp.dayofweek,
            'month': timestamp.month,
            'season': season,
            'rolling_5': rolling_5,
            'rolling_15': rolling_15,
            'rolling_60': rolling_60,
            'rolling_1440': rolling_1440
        }
        
        return features

    def predict_next_24h(self, history_data=None, start_time=None):
        """
        Dự đoán tiêu thụ điện cho 24 giờ tiếp theo
        
        Args:
            history_data: DataFrame hoặc dict chứa dữ liệu lịch sử
                         Cần có: Global_active_power (tối thiểu 1440 điểm cho rolling_1440)
            start_time: Thời điểm bắt đầu dự đoán (mặc định là hiện tại)
        
        Returns:
            predictions: List 24 giá trị dự đoán (kW)
        """
        
        # Nếu không có model, dùng chế độ giả lập
        if self.model is None:
            print("⚠️ Chế độ giả lập - Model chưa được load")
            return self._mock_predictions(history_data)
        
        # Xác định thời điểm bắt đầu
        if start_time is None:
            start_time = datetime.now()
        
        # Chuẩn bị history power
        if history_data is not None:
            if isinstance(history_data, pd.DataFrame):
                history_power = history_data['Global_active_power'].values.tolist()
            elif isinstance(history_data, dict):
                history_power = history_data.get('Global_active_power', [1.0])
            elif isinstance(history_data, (list, np.ndarray)):
                history_power = list(history_data)
            else:
                history_power = [1.0]
        else:
            history_power = [1.0]
        
        predictions = []
        
        for i in range(24):
            # Timestamp cho giờ hiện tại
            current_time = start_time + timedelta(hours=i)
            
            # Tạo features
            features_dict = self.create_features_from_history(
                timestamp=current_time,
                history_power=history_power
            )
            
            # Chuyển thành DataFrame với đúng thứ tự columns
            X = pd.DataFrame([features_dict])
            
            # Đảm bảo columns khớp với model
            if self.feature_names:
                X = X[self.feature_names]
            
            # Scale features
            if self.scaler:
                X_scaled = self.scaler.transform(X)
            else:
                X_scaled = X.values
            
            # Dự đoán
            try:
                pred = self.model.predict(X_scaled)[0]
                pred = max(0.1, pred)  # Đảm bảo không âm
                predictions.append(pred)
                
                # Thêm prediction vào history để tính rolling cho bước tiếp theo
                history_power.append(pred)
                
            except Exception as e:
                print(f"Lỗi dự đoán tại giờ {i}: {e}")
                predictions.append(1.0)  # Giá trị mặc định
        
        return predictions

    def predict_monthly_consumption(self, num_people=2, area_m2=50, 
                                   num_ac=1, num_fridge=1, 
                                   num_tv=1, hours_per_day=8):
        """
        Dự đoán tiêu thụ điện hàng tháng dựa trên thông số gia đình
        
        Args:
            num_people: Số người trong gia đình
            area_m2: Diện tích nhà (m²)
            num_ac: Số máy lạnh
            num_fridge: Số tủ lạnh
            num_tv: Số TV
            hours_per_day: Số giờ sử dụng trung bình/ngày
        
        Returns:
            total_kwh: Tổng kWh ước tính/tháng
            breakdown: Chi tiết từng thiết bị
        """
        
        # Công suất trung bình các thiết bị (kW)
        device_power = {
            'ac': 1.5,        # Máy lạnh
            'fridge': 0.15,   # Tủ lạnh (chạy cả ngày)
            'tv': 0.1,        # TV
            'lighting': 0.05, # Đèn (mỗi người)
            'others': 0.3     # Thiết bị khác
        }
        
        # Số giờ hoạt động/ngày
        usage_hours = {
            'ac': hours_per_day,
            'fridge': 24,
            'tv': hours_per_day * 0.6,
            'lighting': hours_per_day,
            'others': hours_per_day * 0.5
        }
        
        breakdown = {}
        total_kwh = 0
        
        # Tính từng loại thiết bị
        ac_kwh = num_ac * device_power['ac'] * usage_hours['ac'] * 30
        breakdown['Máy lạnh'] = ac_kwh
        total_kwh += ac_kwh
        
        fridge_kwh = num_fridge * device_power['fridge'] * usage_hours['fridge'] * 30
        breakdown['Tủ lạnh'] = fridge_kwh
        total_kwh += fridge_kwh
        
        tv_kwh = num_tv * device_power['tv'] * usage_hours['tv'] * 30
        breakdown['TV'] = tv_kwh
        total_kwh += tv_kwh
        
        lighting_kwh = num_people * device_power['lighting'] * usage_hours['lighting'] * 30
        breakdown['Chiếu sáng'] = lighting_kwh
        total_kwh += lighting_kwh
        
        # Thiết bị khác (phụ thuộc diện tích)
        others_kwh = (area_m2 / 20) * device_power['others'] * usage_hours['others'] * 30
        breakdown['Khác'] = others_kwh
        total_kwh += others_kwh
        
        return total_kwh, breakdown

    def _mock_predictions(self, history_data):
        """Chế độ giả lập khi chưa có model"""
        if history_data is not None:
            if isinstance(history_data, (list, np.ndarray)):
                last_val = history_data[-1] if len(history_data) > 0 else 1.0
            elif isinstance(history_data, pd.DataFrame):
                last_val = history_data['Global_active_power'].iloc[-1]
            else:
                last_val = 1.0
        else:
            last_val = 1.0
            
        predictions = []
        for i in range(24):
            noise = np.random.normal(0, 0.1)
            trend = np.sin(i / 4) * 0.5
            pred = last_val + trend + noise
            predictions.append(max(0.1, pred))
        return predictions


# ================== CÁCH SỬ DỤNG ==================

if __name__ == "__main__":
    # Khởi tạo predictor
    predictor = EnergyPredictor()
    
    print("\n" + "="*60)
    print("📊 DEMO DỰ ĐOÁN")
    print("="*60)
    
    # 1. Dự đoán 24 giờ tiếp theo (không có history)
    print("\n1️⃣ Dự đoán 24 giờ (không có dữ liệu lịch sử):")
    predictions = predictor.predict_next_24h()
    print(f"   Giờ 00:00 -> {predictions[0]:.2f} kW")
    print(f"   Giờ 08:00 -> {predictions[8]:.2f} kW")
    print(f"   Giờ 12:00 -> {predictions[12]:.2f} kW")
    print(f"   Giờ 18:00 -> {predictions[18]:.2f} kW")
    print(f"   Tổng 24h: {sum(predictions):.2f} kWh")
    
    # 2. Dự đoán với history data (giả lập)
    print("\n2️⃣ Dự đoán 24 giờ (có dữ liệu lịch sử):")
    # Giả lập dữ liệu 24h trước (1440 điểm = 24h * 60 phút)
    history = np.random.uniform(0.5, 2.5, 1440).tolist()
    predictions_with_history = predictor.predict_next_24h(history_data=history)
    print(f"   Giờ 00:00 -> {predictions_with_history[0]:.2f} kW")
    print(f"   Giờ 08:00 -> {predictions_with_history[8]:.2f} kW")
    print(f"   Giờ 12:00 -> {predictions_with_history[12]:.2f} kW")
    print(f"   Giờ 18:00 -> {predictions_with_history[18]:.2f} kW")
    print(f"   Tổng 24h: {sum(predictions_with_history):.2f} kWh")
    
    # 3. Dự đoán tiêu thụ hàng tháng
    print("\n3️⃣ Dự đoán tiêu thụ tháng (theo thông số gia đình):")
    total, breakdown = predictor.predict_monthly_consumption(
        num_people=3,
        area_m2=60,
        num_ac=2,
        num_fridge=1,
        num_tv=2,
        hours_per_day=10
    )
    
    print(f"\n   Tổng: {total:.0f} kWh/tháng")
    print("\n   Chi tiết:")
    for device, kwh in breakdown.items():
        print(f"      • {device}: {kwh:.0f} kWh ({kwh/total*100:.1f}%)")
    
    print("\n" + "="*60)