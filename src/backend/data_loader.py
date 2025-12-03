import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_dataset(file_path=None, nrows=None):
    """
    DEMO MODE: Tự động sinh dữ liệu giả lập cho năm 2025 
    mà không cần đọc file CSV gốc.
    """
    st.warning("⚠️ Đang chạy chế độ DEMO (Dữ liệu giả lập).")
    
    date_rng = pd.date_range(start='2006-16-12', end='2010-11-26', freq='min')
    df = pd.DataFrame(date_rng, columns=['dt'])
    df = df.set_index('dt')
    
    n = len(df)
    
    # 2. Tạo dữ liệu giả lập (Sinh trắc học năng lượng)
    # Lấy giờ trong ngày để tạo chu kỳ (0-23)
    hours = df.index.hour.values + df.index.minute.values / 60.0
    
    # --- A. Global Active Power (Tổng tiêu thụ) ---
    # Công thức: Nền (0.5) + Sáng (Peak 1) + Tối (Peak 2) + Nhiễu ngẫu nhiên
    # Peak sáng lúc 8h, Peak tối lúc 19h
    morning_peak = np.exp(-((hours - 8)**2) / 8)  
    evening_peak = np.exp(-((hours - 19)**2) / 8) 
    noise = np.random.normal(0, 0.2, n) # Nhiễu
    
    # Kết hợp lại:
    power = 0.5 + (1.5 * morning_peak) + (2.5 * evening_peak) + noise
    df['Global_active_power'] = np.clip(power, 0.2, 8.0) # Kẹp giá trị không cho âm hoặc quá lớn
    
    # --- B. Voltage (Điện áp) ---
    # Dao động quanh 240V
    df['Voltage'] = 240 + np.random.normal(0, 2, n)
    
    # --- C. Sub Metering (Thiết bị con) ---
    # Sub 1 (Bếp): Chỉ bật vào giờ ăn (trưa 11-12h, tối 18-19h)
    kitchen_mask = ((hours >= 11) & (hours <= 12)) | ((hours >= 18) & (hours <= 19))
    df['Sub_metering_1'] = np.where(kitchen_mask & (np.random.rand(n) > 0.3), np.random.uniform(10, 30, n), 0)
    
    # Sub 2 (Giặt là): Ngẫu nhiên vài lần trong tuần
    # Giả lập random đốm nhỏ
    laundry_prob = np.random.rand(n)
    df['Sub_metering_2'] = np.where(laundry_prob > 0.995, np.random.uniform(5, 20, n), 0)

    # Sub 3 (Điều hòa/Nóng lạnh): Phụ thuộc vào giờ (đêm bật nhiều hơn hoặc tối bật)
    # Giả lập chạy liên tục nhưng ngắt quãng
    ac_pattern = np.sin(hours / 24 * 2 * np.pi) 
    df['Sub_metering_3'] = np.clip(10 + 10 * ac_pattern + np.random.normal(0, 2, n), 0, 30)

    # Đảm bảo logic: Tổng sub < Tổng Active Power * tỉ lệ quy đổi
    # (Chỉ mang tính tương đối cho demo)
    
    return df