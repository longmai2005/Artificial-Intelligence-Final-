import streamlit as st
import sys
import os
import time

# --- IMPORT MODULES ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.auth import authenticate, save_user, check_user_exists, reset_password
from src.components.user_page import render_user_page
from src.components.admin_page import render_admin_page
from src.components.chatbot import render_floating_chatbot
from src.utils.style import apply_custom_style

# --- CONFIG ---
st.set_page_config(page_title="Smart Energy Saver", layout="wide", page_icon="⚡")

# --- INIT SESSION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

def login_page():
    # 1. Nếu đã đăng nhập rồi thì KHÔNG hiện form đăng nhập nữa (Fix lỗi load trang)
    if st.session_state['logged_in']:
        return

    # Áp dụng Style ngay màn hình login
    apply_custom_style()
    
    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>🔐 Smart Energy Access</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Đăng Nhập", "Đăng Ký", "Quên Mật Khẩu"])
    
    # --- TAB 1: ĐĂNG NHẬP ---
    with tab1:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            with st.form("login_form"):
                username = st.text_input("Tên đăng nhập")
                password = st.text_input("Mật khẩu", type="password")
                submit = st.form_submit_button("Truy cập hệ thống", use_container_width=True)
                
                if submit:
                    user_info = authenticate(username, password)
                    if user_info:
                        # Lưu trạng thái vào Session
                        st.session_state['logged_in'] = True
                        st.session_state['user_role'] = user_info['role']
                        st.session_state['username'] = username
                        st.session_state['full_name'] = user_info['name']
                        
                        st.success("Đăng nhập thành công! Đang chuyển hướng...")
                        time.sleep(0.5)
                        st.rerun() # F5 lại trang ngay lập tức để vào Main App
                    else:
                        st.error("Sai tài khoản hoặc mật khẩu!")

    # --- TAB 2: ĐĂNG KÝ ---
    with tab2:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            with st.form("register_form"):
                new_user = st.text_input("Tên đăng nhập mới")
                new_email = st.text_input("Email")
                new_pass = st.text_input("Mật khẩu", type="password")
                full_name = st.text_input("Họ tên hiển thị")
                reg_submit = st.form_submit_button("Tạo tài khoản mới", use_container_width=True)
                
                if reg_submit:
                    if new_user and new_pass:
                        if save_user(new_user, new_pass, full_name, new_email):
                            st.success("Tạo thành công! Vui lòng quay lại tab Đăng nhập.")
                        else:
                            st.error("Tên đăng nhập đã tồn tại.")
                    else:
                        st.warning("Vui lòng điền đủ thông tin.")

    # --- TAB 3: QUÊN MẬT KHẨU (MỚI) ---
    with tab3:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.info("Nhập thông tin để đặt lại mật khẩu.")
            with st.form("forgot_pass_form"):
                fp_user = st.text_input("Tên đăng nhập cần khôi phục")
                fp_email = st.text_input("Email đã đăng ký")
                fp_new_pass = st.text_input("Mật khẩu mới", type="password")
                fp_submit = st.form_submit_button("Đặt lại mật khẩu", use_container_width=True)
                
                if fp_submit:
                    if check_user_exists(fp_user, fp_email):
                        if reset_password(fp_user, fp_new_pass):
                            st.success("Đổi mật khẩu thành công! Hãy đăng nhập ngay.")
                        else:
                            st.error("Có lỗi xảy ra.")
                    else:
                        st.error("Thông tin username hoặc email không khớp.")

def main_app():
    # Áp dụng CSS
    apply_custom_style()
    
    # Sidebar
    st.sidebar.title("⚡ Smart Energy")
    st.sidebar.write(f"Xin chào, **{st.session_state['full_name']}**")
    
    if st.sidebar.button("Đăng xuất", type="primary", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
        st.rerun() # F5 lại trang để về màn hình Login
    
    st.sidebar.markdown("---")
    
    # Điều hướng
    if st.session_state['user_role'] == 'admin':
        render_admin_page()
    else:
        render_user_page(st.session_state['username'], st.session_state['full_name'])

    # Chatbot
    render_floating_chatbot()

# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    if st.session_state['logged_in']:
        main_app()
    else:
        login_page()