import streamlit as st
import pandas as pd
import sys
import os
import time

# --- IMPORT MODULES ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.data_loader import load_dataset
from src.backend.predictor import EnergyPredictor
from src.backend.auth import authenticate, save_user
from src.components.dashboard import render_dashboard
from src.components.forecast import render_forecast
from src.components.recommendation import render_recommendations
from src.components.user_page import render_user_page
from src.utils.style import apply_custom_style

# --- CONFIG ---
st.set_page_config(page_title="Smart Energy Saver", layout="wide", page_icon="⚡")

# --- SESSION STATE SETUP ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'full_name' not in st.session_state:
    st.session_state['full_name'] = None

def login_page():
    st.markdown("<h1 style='text-align: center;'>🔐 Đăng Nhập Hệ Thống</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Đăng Nhập", "Đăng Ký Tài Khoản"])
    
    with tab1:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            with st.form("login_form"):
                username = st.text_input("Tên đăng nhập")
                password = st.text_input("Mật khẩu", type="password")
                submit = st.form_submit_button("Đăng nhập")
                
                if submit:
                    user_info = authenticate(username, password)
                    if user_info:
                        st.session_state['logged_in'] = True
                        st.session_state['user_role'] = user_info['role']
                        st.session_state['username'] = username
                        st.session_state['full_name'] = user_info['name']
                        st.success("Đăng nhập thành công!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Sai tên đăng nhập hoặc mật khẩu!")

    with tab2:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            with st.form("register_form"):
                new_user = st.text_input("Tên đăng nhập mới")
                new_pass = st.text_input("Mật khẩu mới", type="password")
                full_name = st.text_input("Họ và Tên hiển thị")
                reg_submit = st.form_submit_button("Đăng Ký")
                
                if reg_submit:
                    if new_user and new_pass:
                        if save_user(new_user, new_pass, full_name):
                            st.success("Tạo tài khoản thành công! Vui lòng quay lại tab Đăng nhập.")
                        else:
                            st.error("Tên đăng nhập đã tồn tại.")
                    else:
                        st.warning("Vui lòng điền đủ thông tin.")

def main_app():
    # Áp dụng CSS làm đẹp
    apply_custom_style()
    
    # --- SIDEBAR ---
    st.sidebar.title("⚡ Smart Energy")
    st.sidebar.write(f"Xin chào, **{st.session_state['full_name']}**")
    
    # Nút Đăng xuất
    if st.sidebar.button("Đăng xuất"):
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # --- PHÂN QUYỀN GIAO DIỆN ---
    
    # 1. GIAO DIỆN ADMIN (Xem toàn bộ hệ thống giả lập)
    if st.session_state['user_role'] == 'admin':
        st.sidebar.header("🔧 Admin Panel")
        menu = st.sidebar.radio("Menu:", ["Tổng quan (Dashboard)", "Dự báo (Forecast)", "Đề xuất (Savings)"])
        
        # Admin controls simulation
        st.sidebar.markdown("---")
        st.sidebar.caption("Điều khiển Simulator")
        
        # Load Data Logic (Admin Only)
        DATA_PATH = os.path.join("data", "household_power_consumption.txt")
        df = load_dataset(DATA_PATH, nrows=20000)
        
        min_date = df.index.min()
        selected_date = st.sidebar.date_input("Ngày:", min_date)
        selected_hour = st.sidebar.slider("Giờ:", 0, 23, 19)
        
        # Lấy data giả lập
        try:
            current_ts = pd.Timestamp(f"{selected_date} {selected_hour}:00:00")
            idx = df.index.get_indexer([current_ts], method='nearest')[0]
            current_time = df.index[idx]
            current_data = df.iloc[idx]
            predictor = EnergyPredictor() # Load model
            
            if menu == "Tổng quan (Dashboard)":
                render_dashboard(current_data, current_time)
            elif menu == "Dự báo (Forecast)":
                render_forecast(predictor, df, current_time)
            elif menu == "Đề xuất (Savings)":
                render_recommendations(current_time, current_data)
                
        except Exception as e:
            st.error(f"Lỗi Simulator: {e}")

    # 2. GIAO DIỆN USER THƯỜNG (Chỉ xem trang cá nhân)
    else:
        st.sidebar.info("Đây là trang dành cho người dùng cá nhân.")
        render_user_page(st.session_state['username'], st.session_state['full_name'])

if __name__ == "__main__":
    if st.session_state['logged_in']:
        main_app()
    else:
        login_page()