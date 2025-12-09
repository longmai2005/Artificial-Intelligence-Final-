import streamlit as st
import sys
import os
import time

# --- IMPORT MODULES ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.auth import authenticate, save_user, check_user_exists, generate_otp, send_email_otp, reset_password
from src.components.user_page import render_user_page
from src.components.admin_page import render_admin_page
from src.components.chatbot import render_floating_chatbot
from src.utils.style import apply_custom_style

# --- CONFIG ---
st.set_page_config(page_title="Smart Energy Saver", layout="wide", page_icon="⚡")

# --- INIT SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
    
# Quản lý trạng thái màn hình Authentication (login | register | forgot)
if 'auth_mode' not in st.session_state:
    st.session_state['auth_mode'] = 'login' 

# State cho quy trình đăng ký OTP
if 'reg_step' not in st.session_state:
    st.session_state['reg_step'] = 1 
if 'reg_otp' not in st.session_state:
    st.session_state['reg_otp'] = None
if 'reg_data' not in st.session_state:
    st.session_state['reg_data'] = {}

def switch_auth_mode(mode):
    """Hàm chuyển đổi màn hình (Login <-> Register)"""
    st.session_state['auth_mode'] = mode
    # Reset các trạng thái form khi chuyển màn hình để tránh lỗi lưu form cũ
    st.session_state['reg_step'] = 1
    st.session_state['reg_otp'] = None
    st.rerun()

def login_page():
    if st.session_state['logged_in']:
        return

    apply_custom_style()
    
    # Layout căn giữa
    col_spacer1, col_main, col_spacer2 = st.columns([1, 1.2, 1])
    
    with col_main:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; margin-bottom: 10px;'>⚡ Smart Energy</h1>", unsafe_allow_html=True)
        
        # --- MÀN HÌNH 1: ĐĂNG NHẬP ---
        if st.session_state['auth_mode'] == 'login':
            st.markdown("<h3 style='text-align: center;'>Đăng Nhập</h3>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("Tên đăng nhập", placeholder="Nhập username...")
                password = st.text_input("Mật khẩu", type="password", placeholder="••••••")
                submit = st.form_submit_button("Truy cập hệ thống", use_container_width=True)
                
                if submit:
                    # Gọi hàm authenticate (đã có .strip() để xóa khoảng trắng thừa)
                    user_info = authenticate(username, password)
                    
                    if user_info:
                        st.session_state['logged_in'] = True
                        st.session_state['user_role'] = user_info['role']
                        st.session_state['username'] = username
                        st.session_state['full_name'] = user_info['name']
                        st.toast("✅ Đăng nhập thành công!", icon="🎉")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Sai tài khoản hoặc mật khẩu! Vui lòng thử lại.")
            
            # Các nút chuyển hướng
            col_link1, col_link2 = st.columns(2)
            with col_link1:
                if st.button("Tạo tài khoản mới"):
                    switch_auth_mode('register')
            with col_link2:
                if st.button("Quên mật khẩu?"):
                    switch_auth_mode('forgot')

        # --- MÀN HÌNH 2: ĐĂNG KÝ ---
        elif st.session_state['auth_mode'] == 'register':
            st.markdown("<h3 style='text-align: center;'>Đăng Ký Tài Khoản</h3>", unsafe_allow_html=True)
            
            if st.session_state['reg_step'] == 1:
                new_user = st.text_input("Tên đăng nhập mới", key="reg_user")
                new_email = st.text_input("Email (để nhận OTP)", key="reg_email")
                full_name = st.text_input("Họ và Tên", key="reg_name")
                new_pass = st.text_input("Mật khẩu", type="password", key="reg_pass")
                
                if st.button("Gửi mã xác thực (OTP)", type="primary", use_container_width=True):
                    if new_user and new_email and new_pass:
                        if check_user_exists(new_user, new_email):
                            st.error("Username hoặc Email đã tồn tại!")
                        else:
                            otp_code = generate_otp()
                            st.session_state['reg_otp'] = otp_code
                            st.session_state['reg_data'] = {"user": new_user, "pass": new_pass, "name": full_name, "email": new_email}
                            
                            with st.spinner("Đang gửi OTP..."):
                                is_sent = send_email_otp(new_email, otp_code)
                                if is_sent:
                                    st.success(f"Đã gửi OTP đến {new_email}!")
                                else:
                                    st.warning("⚠️ Chế độ Demo (Gửi mail thất bại)")
                                    st.info(f"Mã OTP giả lập: **{otp_code}**")
                            
                            st.session_state['reg_step'] = 2
                            st.rerun()
                    else:
                        st.warning("Vui lòng nhập đủ thông tin.")
                
                if st.button("⬅ Quay lại Đăng nhập"):
                    switch_auth_mode('login')

            elif st.session_state['reg_step'] == 2:
                st.info(f"Nhập mã OTP đã gửi tới {st.session_state['reg_data']['email']}")
                otp_input = st.text_input("Mã xác thực", max_chars=6, key="otp_in")
                
                if st.button("Xác nhận Đăng ký", type="primary", use_container_width=True):
                    if otp_input == st.session_state['reg_otp']:
                        data = st.session_state['reg_data']
                        save_user(data['user'], data['pass'], data['name'], data['email'])
                        
                        st.balloons()
                        st.success("🎉 Đăng ký thành công!")
                        time.sleep(2)
                        
                        # QUAN TRỌNG: Tự động chuyển về màn hình Login sau khi thành công
                        switch_auth_mode('login') 
                    else:
                        st.error("Mã OTP sai!")
                
                if st.button("Hủy bỏ"):
                    switch_auth_mode('login')

        # --- MÀN HÌNH 3: QUÊN MẬT KHẨU ---
        elif st.session_state['auth_mode'] == 'forgot':
            st.markdown("<h3 style='text-align: center;'>Khôi Phục Mật Khẩu</h3>", unsafe_allow_html=True)
            
            with st.form("forgot_form"):
                fp_user = st.text_input("Tên đăng nhập")
                fp_email = st.text_input("Email đăng ký")
                fp_new_pass = st.text_input("Mật khẩu mới", type="password")
                fp_submit = st.form_submit_button("Đặt lại mật khẩu", use_container_width=True)
                
                if fp_submit:
                    # Kiểm tra user và email có khớp nhau không
                    if check_user_exists(fp_user, fp_email):
                        reset_password(fp_user, fp_new_pass)
                        st.success("Đổi mật khẩu thành công! Vui lòng đăng nhập lại.")
                        time.sleep(1.5)
                        # Tự động chuyển về login
                        st.session_state['auth_mode'] = 'login'
                        st.rerun()
                    else:
                        st.error("Thông tin không chính xác.")
            
            if st.button("⬅ Quay lại"):
                switch_auth_mode('login')

        st.markdown("</div>", unsafe_allow_html=True)

def main_app():
    apply_custom_style()
    
    # Sidebar
    st.sidebar.title("⚡ Smart Energy")
    st.sidebar.write(f"User: **{st.session_state['full_name']}**")
    
    if st.sidebar.button("Đăng xuất", type="primary", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
        st.session_state['auth_mode'] = 'login' # Reset về login khi đăng xuất
        st.rerun()
    st.sidebar.markdown("---")
    
    # Điều hướng
    if st.session_state['user_role'] == 'admin':
        render_admin_page()
    else:
        render_user_page(st.session_state['username'], st.session_state['full_name'])

    render_floating_chatbot()

if __name__ == "__main__":
    if st.session_state['logged_in']:
        main_app()
    else:
        login_page()