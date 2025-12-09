import streamlit as st
import sys
import os
import time

# --- SETUP ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.auth import authenticate, save_user, check_user_exists, generate_otp, send_email_otp, reset_password
from src.components.user_page import render_user_page
from src.components.admin_page import render_admin_page
from src.components.chatbot import render_floating_chatbot
from src.utils.style import apply_custom_style

# --- CONFIG ---
st.set_page_config(page_title="Smart Energy", layout="wide", page_icon="⚡")

# --- SESSION ---
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
    
    # Layout căn giữa màn hình
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        # --- KHUNG ĐĂNG NHẬP (Card) ---
        st.markdown("""
            <div class='login-card'>
                <div style="font-size: 40px; margin-bottom: 10px;">⚡</div>
                <h1 class='brand-text'>Smart Energy</h1>
                <p class='slogan-text'>Hãy Vì Một Năng Lượng Xanh</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Form logic
        if st.session_state['auth_mode'] == 'login':
            with st.form("login_form"):
                u = st.text_input("Tài khoản", placeholder="Username")
                p = st.text_input("Mật khẩu", type="password", placeholder="••••••")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("🚀 Đăng Nhập Ngay"):
                    res = authenticate(u, p)
                    if res == "NOT_FOUND": st.error("❌ Tài khoản không tồn tại!")
                    elif res == "WRONG_PASS": st.error("❌ Sai mật khẩu.")
                    elif res:
                        st.session_state['logged_in'] = True
                        st.session_state['user_role'] = res['role']
                        st.session_state['username'] = u
                        st.session_state['full_name'] = res['name']
                        st.toast("Đăng nhập thành công!", icon="🎉")
                        time.sleep(0.5)
                        st.rerun()
            
            # Các nút phụ (Nằm dưới form, căn đều)
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            c_reg, c_forgot = st.columns(2)
            with c_reg:
                if st.button("✨ Tạo tài khoản"): switch_mode('register')
            with c_forgot:
                if st.button("❓ Quên mật khẩu"): switch_mode('forgot')

        # --- ĐĂNG KÝ ---
        elif st.session_state['auth_mode'] == 'register':
            st.markdown("<h4 style='text-align:center;'>Tạo Tài Khoản Mới</h4>", unsafe_allow_html=True)
            
            if st.session_state['reg_step'] == 1:
                name = st.text_input("Họ Tên", key="rn")
                email = st.text_input("Email", key="re")
                user = st.text_input("Username", key="ru")
                pw = st.text_input("Password", type="password", key="rp")
                
                if st.button("Gửi mã OTP ➤", type="primary"):
                    if user and email and pw:
                        if check_user_exists(user, email): st.error("Đã tồn tại!")
                        else:
                            otp = generate_otp()
                            st.session_state['reg_otp'] = otp
                            st.session_state['reg_data'] = {"user": user, "pass": pw, "name": name, "email": email}
                            with st.spinner("Đang gửi mail..."):
                                if send_email_otp(email, otp): st.success(f"OTP đã gửi tới {email}")
                                else: st.info(f"Demo OTP: {otp}")
                            st.session_state['reg_step'] = 2
                            st.rerun()
                    else: st.warning("Nhập đủ thông tin nhé!")
                
                if st.button("⬅ Quay lại"): switch_mode('login')

            elif st.session_state['reg_step'] == 2:
                st.info(f"Nhập mã gửi về {st.session_state['reg_data']['email']}")
                otp_in = st.text_input("Mã OTP", max_chars=6)
                if st.button("✅ Xác nhận"):
                    if otp_in == st.session_state['reg_otp']:
                        d = st.session_state['reg_data']
                        save_user(d['user'], d['pass'], d['name'], d['email'])
                        st.balloons()
                        st.success("Thành công!")
                        time.sleep(1.5)
                        switch_mode('login')
                    else: st.error("Sai mã OTP.")
                if st.button("Hủy"): switch_mode('login')

        # --- QUÊN MK ---
        elif st.session_state['auth_mode'] == 'forgot':
            st.markdown("<h4 style='text-align:center;'>Khôi Phục Mật Khẩu</h4>", unsafe_allow_html=True)
            with st.form("forgot"):
                fu = st.text_input("Username")
                fe = st.text_input("Email")
                fp = st.text_input("Pass mới", type="password")
                if st.form_submit_button("Đặt lại"):
                    if check_user_exists(fu, fe):
                        reset_password(fu, fp)
                        st.success("Xong! Đăng nhập lại nhé.")
                        time.sleep(1.5)
                        switch_mode('login')
                    else: st.error("Sai thông tin.")
            if st.button("⬅ Quay lại"): switch_mode('login')

def main_app():
    apply_custom_style()
    st.sidebar.title("⚡ Smart Energy")
    st.sidebar.caption(f"User: {st.session_state['full_name']}")
    
    if st.sidebar.button("Đăng xuất"):
        st.session_state['logged_in'] = False
        st.session_state['auth_mode'] = 'login'
        st.rerun()
    st.sidebar.markdown("---")
    
    if st.session_state['user_role'] == 'admin':
        render_admin_page()
    else:
        render_user_page(st.session_state['username'], st.session_state['full_name'])
        render_floating_chatbot()

if __name__ == "__main__":
    if st.session_state['logged_in']: main_app()
    else: login_page()