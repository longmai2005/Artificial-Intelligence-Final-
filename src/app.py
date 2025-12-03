import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backend.data_loader import load_dataset
from src.backend.predictor import EnergyPredictor
from src.components.dashboard import render_dashboard
from src.components.forecast import render_forecast
from src.components.recommendation import render_recommendations

# --- CONFIG ---
st.set_page_config(page_title="Smart Energy Saver", layout="wide", page_icon="⚡")

def main():
    # 1. Load Data
    DATA_PATH = os.path.join("data", "household_power_consumption.txt")
    
    with st.spinner("Đang khởi động hệ thống và nạp dữ liệu..."):
        df = load_dataset(DATA_PATH, nrows=20000) # Load 20k dòng demo
    
    if df.empty:
        st.error("Chưa có dữ liệu. Vui lòng kiểm tra file data/household_power_consumption.txt")
        return

    # 2. Init Model
    predictor = EnergyPredictor()

    # 3. Sidebar Navigation & Control
    st.sidebar.title("⚡ Smart Energy Saver")
    
    menu = st.sidebar.radio("Chức năng:", ["Dashboard", "Dự báo (Forecast)", "Đề xuất (Savings)"])
    
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Bộ điều khiển Giả lập")
    
    # Chọn ngày giờ để "Replay"
    min_date = df.index.min()
    max_date = df.index.max()
    
    selected_date = st.sidebar.date_input("Ngày:", min_date)
    selected_hour = st.sidebar.slider("Giờ:", 0, 23, 19)
    
    # Lấy dữ liệu tại thời điểm chọn
    try:
        # Tạo timestamp (chọn phút 00 cho đơn giản)
        current_ts = pd.Timestamp(f"{selected_date} {selected_hour}:00:00")
        
        # Tìm dòng dữ liệu gần nhất (phòng trường hợp ngày đó không có data)
        # asof tìm điểm gần nhất phía trước
        idx = df.index.get_indexer([current_ts], method='nearest')[0]
        current_time = df.index[idx]
        current_data = df.iloc[idx]
        
    except Exception as e:
        st.error(f"Lỗi chọn thời gian: {e}")
        return

    # 4. Render Main Content
    if menu == "Dashboard":
        render_dashboard(current_data, current_time)
        
    elif menu == "Dự báo (Forecast)":
        render_forecast(predictor, df, current_time)
        
    elif menu == "Đề xuất (Savings)":
        render_recommendations(current_time, current_data)

if __name__ == "__main__":
    main()