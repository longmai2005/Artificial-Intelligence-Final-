import streamlit as st
import sys
import os
import time

# --- CẤU HÌNH TRANG (PHẢI Ở DÒNG ĐẦU TIÊN) ---
st.set_page_config(page_title="Smart Energy Access", layout="wide", page_icon="⚡")

# --- QUẢN LÝ SESSION STATE (KHỞI TẠO 1 LẦN DUY NHẤT) ---
# Sửa lỗi reset: Kiểm tra kỹ trước khi gán giá trị mặc định
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'auth_mode' not in st.session_state: st.session_state['auth_mode'] = 'login'
if 'user_role' not in st.session_state: st.session_state['user_role'] = None
if 'username' not in st.session_state: st.session_state['username'] = None
if 'full_name' not in st.session_state: st.session_state['full_name'] = None
if 'reg_step' not in st.session_state: st.session_state['reg_step'] = 1
if 'reg_otp' not in st.session_state: st.session_state['reg_otp'] = None
if 'reg_data' not in st.session_state: st.session_state['reg_data'] = {}

# --- IMPORT MODULES ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.auth import authenticate, save_user, check_user_exists, generate_otp, send_email_otp, reset_password
from src.components.user_page import render_user_page
from src.components.admin_page import render_admin_page
from src.components.chatbot import render_floating_chatbot
from src.utils.style import apply_custom_style

def switch_auth_mode(mode):
    """Chuyển đổi màn hình và reset trạng thái"""
    st.session_state['auth_mode'] = mode
    st.session_state['reg_step'] = 1
    st.rerun()

def login_page():
    """Màn hình xác thực"""
    # Fix lỗi: Nếu đã login thì return ngay, không render form login nữa
    if st.session_state['logged_in']: return

    apply_custom_style()
    col_left, col_card, col_right = st.columns([1, 1.2, 1])
    
    with col_card:
        # Header
        st.markdown("""
            <div class='login-container'>
                <div style="font-size: 45px; margin-bottom: 5px;">⚡</div>
                <h1 class='brand-text'>Smart Energy</h1>
                <p class='slogan-text'>Giải pháp năng lượng thông minh 4.0</p>
            </div>
        """, unsafe_allow_html=True)
        
        # --- LOGIN MODE ---
        if st.session_state['auth_mode'] == 'login':
            st.markdown("<h3 style='text-align:center; color:white; margin-bottom:20px;'>Đăng Nhập</h3>", unsafe_allow_html=True)
            
            # Form đăng nhập (Dùng st.form để tránh reload mỗi khi gõ phím)
            with st.form("login_form"):
                user_input = st.text_input("Tài khoản", key="li_user", placeholder="Username")
                pass_input = st.text_input("Mật khẩu", type="password", key="li_pass", placeholder="••••••")
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.form_submit_button("🚀 Truy cập Hệ thống", use_container_width=True):
                    # Gọi hàm authenticate
                    result = authenticate(user_input, pass_input)
                    
                    if result == "NOT_FOUND":
                        st.error("❌ Tài khoản chưa đăng ký!")
                    elif result == "WRONG_PASS":
                        st.error("❌ Mật khẩu không chính xác.")
                    elif result:
                        # Đăng nhập thành công
                        st.session_state['logged_in'] = True
                        st.session_state['user_role'] = result['role']
                        st.session_state['username'] = user_input
                        st.session_state['full_name'] = result['name']
                        st.toast("Đăng nhập thành công!", icon="🟢")
                        time.sleep(0.5)
                        st.rerun() # Quan trọng: Rerun để load vào main_app ngay

            c1, c2 = st.columns(2)
            with c1: 
                if st.button("✨ Tạo tài khoản"): switch_auth_mode('register')
            with c2:
                if st.button("❓ Quên mật khẩu"): switch_auth_mode('forgot')

        # --- REGISTER MODE ---
        elif st.session_state['auth_mode'] == 'register':
            st.markdown("<h3 style='text-align:center; color:white;'>Đăng Ký</h3>", unsafe_allow_html=True)
            
            if st.session_state['reg_step'] == 1:
                st.text_input("Họ và Tên", key="reg_name_in")
                st.text_input("Email", key="reg_email_in")
                c1, c2 = st.columns(2)
                with c1: st.text_input("Username", key="reg_user_in")
                with c2: st.text_input("Password", type="password", key="reg_pass_in")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Gửi OTP ➤", type="primary", use_container_width=True):
                    # Lấy giá trị từ session state do key input tạo ra
                    r_user = st.session_state.reg_user_in
                    r_email = st.session_state.reg_email_in
                    r_pass = st.session_state.reg_pass_in
                    r_name = st.session_state.reg_name_in
                    
                    if r_user and r_email and r_pass:
                        if check_user_exists(r_user, r_email):
                            st.error("⚠️ Tài khoản đã tồn tại!")
                        else:
                            otp = generate_otp()
                            st.session_state['reg_otp'] = otp
                            st.session_state['reg_data'] = {"user": r_user, "pass": r_pass, "name": r_name, "email": r_email}
                            
                            with st.spinner("Đang gửi mail..."):
                                if send_email_otp(r_email, otp):
                                    st.success(f"Đã gửi OTP đến {r_email}")
                                else:
                                    st.warning("Demo Mode: Gửi mail thất bại.")
                                    st.info(f"OTP giả lập: **{otp}**")
                            st.session_state['reg_step'] = 2
                            st.rerun()
                    else:
                        st.warning("Điền đủ thông tin nhé!")
                
                if st.button("⬅ Quay lại"): switch_auth_mode('login')

            elif st.session_state['reg_step'] == 2:
                st.info(f"Nhập OTP gửi về {st.session_state['reg_data']['email']}")
                otp_in = st.text_input("Mã OTP", max_chars=6)
                
                if st.button("✅ Xác nhận", type="primary", use_container_width=True):
                    if otp_in == st.session_state['reg_otp']:
                        d = st.session_state['reg_data']
                        save_user(d['user'], d['pass'], d['name'], d['email'])
                        st.balloons()
                        st.success("Thành công! Về trang đăng nhập...")
                        time.sleep(2)
                        switch_auth_mode('login')
                    else:
                        st.error("OTP sai rồi.")
                
                if st.button("Hủy"): 
                    st.session_state['reg_step'] = 1
                    st.rerun()

        # --- FORGOT MODE ---
        elif st.session_state['auth_mode'] == 'forgot':
            st.markdown("<h3 style='text-align:center; color:white;'>Khôi Phục</h3>", unsafe_allow_html=True)
            with st.form("forgot_f"):
                f_user = st.text_input("Username")
                f_email = st.text_input("Email")
                f_new = st.text_input("Pass mới", type="password")
                if st.form_submit_button("Đặt lại mật khẩu", use_container_width=True):
                    if check_user_exists(f_user, f_email):
                        reset_password(f_user, f_new)
                        st.success("Xong! Đăng nhập lại nhé.")
                        time.sleep(1.5)
                        switch_auth_mode('login')
                    else:
                        st.error("Thông tin không khớp.")
            if st.button("⬅ Quay lại"): switch_auth_mode('login')

def main_app():
    """Giao diện chính"""
    # Nếu chưa login thì hiển thị login_page
    if not st.session_state['logged_in']:
        login_page()
        return

    # Nếu đã login thì hiển thị App
    apply_custom_style()
    st.sidebar.title("⚡ Smart Energy")
    st.sidebar.write(f"Xin chào, **{st.session_state['full_name']}**")
    
    if st.sidebar.button("Đăng xuất", type="primary", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
        st.session_state['auth_mode'] = 'login'
        st.rerun()
    st.sidebar.markdown("---")
    
    if st.session_state['user_role'] == 'admin':
        render_admin_page()
    else:
        render_user_page(st.session_state['username'], st.session_state['full_name'])
        render_floating_chatbot() # Chatbot AI thật

if __name__ == "__main__":
    # Logic điều hướng chính nằm ở đây
    if st.session_state['logged_in']:
        main_app()
    else:
        login_page()