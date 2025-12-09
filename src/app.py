import streamlit as st
import sys
import os
import time

# --- SETUP PATH ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- IMPORTS ---
from src.backend.auth import authenticate, save_user, check_user_exists, generate_otp, send_email_otp, reset_password
from src.components.user_page import render_user_page
from src.components.admin_page import render_admin_page
from src.components.chatbot import render_floating_chatbot
from src.utils.style import apply_custom_style

# --- CONFIG ---
st.set_page_config(page_title="Smart Energy", layout="wide", page_icon="⚡")

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'auth_mode' not in st.session_state: st.session_state['auth_mode'] = 'login'
if 'user_role' not in st.session_state: st.session_state['user_role'] = None
if 'reg_step' not in st.session_state: st.session_state['reg_step'] = 1
if 'reg_otp' not in st.session_state: st.session_state['reg_otp'] = None
if 'reg_data' not in st.session_state: st.session_state['reg_data'] = {}

def switch_mode(mode):
    st.session_state['auth_mode'] = mode
    st.session_state['reg_step'] = 1
    st.rerun()

def login_page():
    if st.session_state['logged_in']: return
    apply_custom_style()
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        # HEADER
        st.markdown("""
            <div class='login-container'>
                <h1 class='brand-text'>Smart Energy</h1>
                <p style='color:#94a3b8;'>Giải pháp tiết kiệm năng lượng 4.0</p>
            </div>
        """, unsafe_allow_html=True)

        # --- LOGIN FORM ---
        if st.session_state['auth_mode'] == 'login':
            st.markdown("### 🔐 Đăng Nhập")
            with st.form("login"):
                u = st.text_input("Tài khoản", placeholder="Username")
                p = st.text_input("Mật khẩu", type="password", placeholder="••••••")
                if st.form_submit_button("Truy cập hệ thống", use_container_width=True):
                    res = authenticate(u, p)
                    if res == "NOT_FOUND": st.error("❌ Tài khoản chưa đăng ký!")
                    elif res == "WRONG_PASS": st.error("❌ Sai mật khẩu.")
                    elif res:
                        st.session_state['logged_in'] = True
                        st.session_state['user_role'] = res['role']
                        st.session_state['username'] = u
                        st.session_state['full_name'] = res['name']
                        st.toast("Đăng nhập thành công!", icon="🎉")
                        time.sleep(0.5)
                        st.rerun()
            
            c1, c2 = st.columns(2)
            if c1.button("✨ Đăng Ký"): switch_mode('register')
            if c2.button("❓ Quên MK"): switch_mode('forgot')

        # --- REGISTER FORM ---
        elif st.session_state['auth_mode'] == 'register':
            st.markdown("### ✨ Đăng Ký Tài Khoản")
            
            if st.session_state['reg_step'] == 1:
                name = st.text_input("Họ Tên", key="r_name")
                email = st.text_input("Email (Nhận OTP)", key="r_email")
                c_u, c_p = st.columns(2)
                user = c_u.text_input("Username", key="r_user")
                pw = c_p.text_input("Password", type="password", key="r_pass")
                
                if st.button("Gửi OTP ➤", type="primary", use_container_width=True):
                    if user and email and pw:
                        if check_user_exists(user, email):
                            st.error("Tài khoản hoặc Email đã tồn tại!")
                        else:
                            otp = generate_otp()
                            st.session_state['reg_otp'] = otp
                            st.session_state['reg_data'] = {"user": user, "pass": pw, "name": name, "email": email}
                            
                            with st.spinner("Đang gửi mail..."):
                                sent = send_email_otp(email, otp)
                                if sent: st.success(f"Đã gửi OTP đến {email}")
                                else: 
                                    st.warning("Gửi mail lỗi (Chế độ Demo)")
                                    st.info(f"OTP Demo: **{otp}**")
                            st.session_state['reg_step'] = 2
                            st.rerun()
                    else:
                        st.warning("Vui lòng điền đủ thông tin.")
                
                if st.button("⬅ Quay lại"): switch_mode('login')

            elif st.session_state['reg_step'] == 2:
                st.info(f"Nhập mã OTP gửi về {st.session_state['reg_data']['email']}")
                otp_in = st.text_input("Mã OTP", max_chars=6)
                
                if st.button("✅ Xác nhận", type="primary", use_container_width=True):
                    if otp_in == st.session_state['reg_otp']:
                        d = st.session_state['reg_data']
                        save_user(d['user'], d['pass'], d['name'], d['email'])
                        st.balloons()
                        st.success("Đăng ký thành công!")
                        time.sleep(2)
                        switch_mode('login')
                    else:
                        st.error("OTP không chính xác.")
                
                if st.button("Hủy"): switch_mode('login')

        # --- FORGOT PASSWORD ---
        elif st.session_state['auth_mode'] == 'forgot':
            st.markdown("### 🔑 Khôi phục mật khẩu")
            with st.form("forgot"):
                f_u = st.text_input("Username")
                f_e = st.text_input("Email")
                f_p = st.text_input("Mật khẩu mới", type="password")
                if st.form_submit_button("Đặt lại mật khẩu", use_container_width=True):
                    if check_user_exists(f_u, f_e):
                        reset_password(f_u, f_p)
                        st.success("Thành công! Hãy đăng nhập lại.")
                        time.sleep(1.5)
                        switch_mode('login')
                    else:
                        st.error("Thông tin không chính xác.")
            if st.button("⬅ Quay lại"): switch_mode('login')

def main_app():
    apply_custom_style()
    
    # Sidebar
    st.sidebar.title("⚡ Smart Energy")
    st.sidebar.write(f"Xin chào, **{st.session_state['full_name']}**")
    
    if st.sidebar.button("Đăng xuất", type="primary", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
        st.session_state['auth_mode'] = 'login'
        st.rerun()
    st.sidebar.markdown("---")
    
    # Routing
    if st.session_state['user_role'] == 'admin':
        render_admin_page()
    else:
        render_user_page(st.session_state['username'], st.session_state['full_name'])
        render_floating_chatbot() # Chỉ hiện Chatbot cho User

if __name__ == "__main__":
    if st.session_state['logged_in']:
        main_app()
    else:
        login_page()