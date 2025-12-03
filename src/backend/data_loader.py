import pandas as pd
import streamlit as st
import os
from src.utils.helpers import map_date_to_current_year

@st.cache_data
def load_dataset(file_path, nrows=50000):
    """
    Đọc file CSV, xử lý missing values và chuẩn hóa index.
    """
    if not os.path.exists(file_path):
        return pd.DataFrame()

    try:
        # 1. Đọc dữ liệu
        df = pd.read_csv(
            file_path, 
            sep=';', 
            nrows=nrows, 
            na_values=['?', 'nan'],
            low_memory=False
        )

        # 2. Xử lý thời gian
        df['dt'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True)
        df = df.drop(['Date', 'Time'], axis=1)
        df = df.set_index('dt')

        # 3. Ép kiểu số
        cols = ['Global_active_power', 'Global_reactive_power', 'Voltage', 
                'Global_intensity', 'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']
        for col in cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 4. Xử lý Missing (Nội suy)
        df = df.interpolate(method='time', limit_direction='both')

        # 5. Map sang năm 2025
        df = map_date_to_current_year(df, 2025)

        return df

    except Exception as e:
        st.error(f"Lỗi khi đọc dữ liệu: {e}")
        return pd.DataFrame()