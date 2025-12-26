import pandas as pd
import numpy as np
import streamlit as st
import os

@st.cache_data
def load_dataset(file_path="data/cleaned_dataset.csv", nrows=None):
    """
    Ưu tiên load dữ liệu thật từ cleaned_dataset.csv.
    Nếu không thấy file, sẽ tự động chuyển sang chế độ DEMO.
    """
    
    # Kiểm tra xem file dữ liệu thật (đã qua xử lý) có tồn tại không
    if os.path.exists(file_path):
        try:
            # Load dữ liệu thật
            df = pd.read_csv(file_path, nrows=nrows)
            
            # Chuyển cột Datetime về đúng định dạng và set index
            if 'Datetime' in df.columns:
                df['Datetime'] = pd.to_datetime(df['Datetime'])
                df = df.set_index('Datetime')
            
            # Đảm bảo các cột categorical được xử lý nếu cần (ví dụ season)
            # Nếu model cần season là số (0,1,2,3), ta ánh xạ lại
            if 'season' in df.columns and df['season'].dtype == 'object':
                season_map = {'Spring': 0, 'Summer': 1, 'Autumn': 2, 'Winter': 3}
                df['season'] = df['season'].map(season_map)
                
            print(f"✅ Đã load dữ liệu thật từ {file_path}")
            return df
            
        except Exception as e:
            st.error(f"Lỗi khi đọc file dữ liệu thật: {e}")
            # Nếu lỗi thì rơi xuống phần DEMO bên dưới
    
    # --- CHẾ ĐỘ DEMO ---
    st.warning("⚠️ Không tìm thấy dữ liệu thật. Đang chạy chế độ DEMO (Dữ liệu giả lập).")
    
    # 1. Tạo timeline
    date_rng = pd.date_range(start='2006-12-16', end='2010-11-26', freq='min')
    df = pd.DataFrame(date_rng, columns=['dt'])
    df = df.set_index('dt')
    n = len(df)
    hours = df.index.hour.values + df.index.minute.values / 60.0

    # --- A. Tạo dữ liệu mô phỏng ---
    morning_peak = np.exp(-((hours - 8)**2) / 8)  
    evening_peak = np.exp(-((hours - 19)**2) / 8) 
    noise = np.random.normal(0, 0.2, n)
    power = 0.5 + (1.5 * morning_peak) + (2.5 * evening_peak) + noise
    df['Global_active_power'] = np.clip(power, 0.2, 8.0)
    
    df['Voltage'] = 240 + np.random.normal(0, 2, n)
    df['Global_intensity'] = (df['Global_active_power'] * 1000) / df['Voltage']
    df['Global_reactive_power'] = df['Global_active_power'] * 0.48 + np.random.normal(0, 0.05, n)
    
    # --- B. Thêm features cần thiết cho model ---
    df['hour'] = df.index.hour
    df['weekday'] = df.index.dayofweek
    df['month'] = df.index.month
    
    # Season mapping (0: Spring, 1: Summer, 2: Autumn, 3: Winter)
    df['season'] = df['month'].apply(lambda m: 3 if m in [12, 1, 2] else 0 if m in [3, 4, 5] else 1 if m in [6, 7, 8] else 2)
    
    # Rolling features
    df['rolling_5'] = df['Global_active_power'].rolling(window=5, min_periods=1).mean()
    df['rolling_15'] = df['Global_active_power'].rolling(window=15, min_periods=1).mean()
    df['rolling_60'] = df['Global_active_power'].rolling(window=60, min_periods=1).mean()
    df['rolling_1440'] = df['Global_active_power'].rolling(window=1440, min_periods=1).mean()
    
    df['energy_per_day_kwh'] = df['Global_active_power'] * (1/60) * 24
    
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