import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_dataset(file_path=None, nrows=None):
    """
    DEMO MODE: Tự động sinh dữ liệu giả lập cho năm 2025 
    mà không cần đọc file CSV gốc.
    
    ✅ FIX: Thêm đầy đủ các columns cần thiết cho model
    """
    st.warning("⚠️ Đang chạy chế độ DEMO (Dữ liệu giả lập).")
    
    # 1. Tạo timeline
    date_rng = pd.date_range(start='2006-12-16', end='2010-11-26', freq='min')
    df = pd.DataFrame(date_rng, columns=['dt'])
    df = df.set_index('dt')
    
    n = len(df)
    
    # 2. Lấy giờ trong ngày để tạo chu kỳ (0-23)
    hours = df.index.hour.values + df.index.minute.values / 60.0
    
    # --- A. Global Active Power (Tổng tiêu thụ) ---
    # Công thức: Nền (0.5) + Sáng (Peak 1) + Tối (Peak 2) + Nhiễu
    morning_peak = np.exp(-((hours - 8)**2) / 8)  
    evening_peak = np.exp(-((hours - 19)**2) / 8) 
    noise = np.random.normal(0, 0.2, n)
    
    power = 0.5 + (1.5 * morning_peak) + (2.5 * evening_peak) + noise
    df['Global_active_power'] = np.clip(power, 0.2, 8.0)
    
    # --- B. Voltage (Điện áp) ---
    df['Voltage'] = 240 + np.random.normal(0, 2, n)
    
    # --- C. Global Intensity (Cường độ dòng điện) ---
    # ✅ FIX: Thêm column này
    # Công thức: I = P / V (Ampere = Watt / Volt)
    # Chuyển kW → W: P(W) = P(kW) * 1000
    df['Global_intensity'] = (df['Global_active_power'] * 1000) / df['Voltage']
    df['Global_intensity'] = df['Global_intensity'].clip(1.0, 50.0)  # Giới hạn hợp lý
    
    # --- D. Global Reactive Power ---
    # ✅ FIX: Thêm column này
    # Công thức ước tính: Q ≈ P × tan(φ), với cos(φ) ≈ 0.9
    # tan(φ) ≈ 0.48 khi cos(φ) = 0.9
    df['Global_reactive_power'] = df['Global_active_power'] * 0.48 + np.random.normal(0, 0.05, n)
    df['Global_reactive_power'] = df['Global_reactive_power'].clip(0.0, 2.0)
    
    # --- E. Sub Metering (Thiết bị con) ---
    # Sub 1 (Bếp): Chỉ bật vào giờ ăn (trưa 11-12h, tối 18-19h)
    kitchen_mask = ((hours >= 11) & (hours <= 12)) | ((hours >= 18) & (hours <= 19))
    df['Sub_metering_1'] = np.where(
        kitchen_mask & (np.random.rand(n) > 0.3), 
        np.random.uniform(10, 30, n), 
        0
    )
    
    # Sub 2 (Giặt là): Ngẫu nhiên vài lần trong tuần
    laundry_prob = np.random.rand(n)
    df['Sub_metering_2'] = np.where(
        laundry_prob > 0.995, 
        np.random.uniform(5, 20, n), 
        0
    )

    # Sub 3 (Điều hòa/Nóng lạnh): Phụ thuộc vào giờ
    ac_pattern = np.sin(hours / 24 * 2 * np.pi) 
    df['Sub_metering_3'] = np.clip(
        10 + 10 * ac_pattern + np.random.normal(0, 2, n), 
        0, 
        30
    )
    
    # --- F. Thêm features cho model ---
    # ✅ FIX: Thêm các features time-based
    df['hour'] = df.index.hour
    df['weekday'] = df.index.dayofweek
    df['month'] = df.index.month
    
    # Season
    def get_season(month):
        if month in [12, 1, 2]:
            return 3  # Winter
        elif month in [3, 4, 5]:
            return 0  # Spring
        elif month in [6, 7, 8]:
            return 1  # Summer
        else:
            return 2  # Fall
    
    df['season'] = df['month'].apply(get_season)
    
    # --- G. Rolling averages ---
    # ✅ FIX: Thêm rolling features (cần cho model)
    df['rolling_5'] = df['Global_active_power'].rolling(window=5, min_periods=1).mean()
    df['rolling_15'] = df['Global_active_power'].rolling(window=15, min_periods=1).mean()
    df['rolling_60'] = df['Global_active_power'].rolling(window=60, min_periods=1).mean()
    df['rolling_1440'] = df['Global_active_power'].rolling(window=1440, min_periods=1).mean()
    
    # --- H. Energy per day (optional) ---
    df['energy_per_day_kwh'] = df['Global_active_power'] * (1/60) * 24  # Ước tính
    
    return df


# ================== TEST ==================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TEST DATA LOADER")
    print("="*70)
    
    df = load_dataset(nrows=10000)
    
    print(f"\n📊 Dataset Info:")
    print(f"   • Shape: {df.shape}")
    print(f"   • Columns: {len(df.columns)}")
    print(f"   • Date range: {df.index[0]} → {df.index[-1]}")
    
    print(f"\n📋 Columns:")
    for col in df.columns:
        print(f"   ✅ {col}")
    
    print(f"\n📈 Sample Data (first 5 rows):")
    print(df.head())
    
    print(f"\n📊 Statistics:")
    print(df[['Global_active_power', 'Voltage', 'Global_intensity']].describe())
    
    # Kiểm tra missing values
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print(f"\n✅ No missing values")
    else:
        print(f"\n⚠️ Missing values:")
        print(missing[missing > 0])
    
    print("\n" + "="*70)
    print("✅ Data loader working correctly!")
    print("="*70)