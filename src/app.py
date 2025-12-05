# File: src/app.py
import streamlit as st
import pandas as pd
import sys
import os
import time

# --- IMPORT MODULES ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.auth import authenticate, save_user
from src.components.user_page import render_user_page
from src.components.admin_page import render_admin_page  # Import trang Admin mới
from src.components.chatbot import render_floating_chatbot # Import Chatbot bong bóng
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
    # (Giữ nguyên code phần login_page như cũ...)
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
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Sai thông tin!")

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
                            st.success("Tạo tài khoản thành công! Quay lại tab Đăng nhập.")
                        else:
                            st.error("User đã tồn tại.")

def main_app():
    # Áp dụng CSS làm đẹp
    apply_custom_style()
    
    # --- HEADER & SIDEBAR ---
    st.sidebar.title("⚡ Smart Energy")
    st.sidebar.write(f"Xin chào, **{st.session_state['full_name']}**")
    
    if st.sidebar.button("Đăng xuất", type="primary"):
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # --- ROUTING (ĐIỀU HƯỚNG) ---
    
    # 1. TRANG ADMIN (Giao diện mới)
    if st.session_state['user_role'] == 'admin':
        st.sidebar.info("🔧 Bạn đang ở chế độ Quản trị viên")
        render_admin_page() # Gọi trang admin mới đã thiết kế lại

    # 2. TRANG USER THƯỜNG
    else:
        st.sidebar.info("👤 Đây là trang người dùng cá nhân")
        render_user_page(st.session_state['username'], st.session_state['full_name'])

    # --- CHATBOT TOÀN CỤC (Hiển thị mọi nơi) ---
    # Đặt chatbot ở đây để nó luôn hiện ở góc dưới dù là trang Admin hay User
    render_floating_chatbot()

if __name__ == "__main__":
    if st.session_state['logged_in']:
        main_app()
    else:
        login_page()