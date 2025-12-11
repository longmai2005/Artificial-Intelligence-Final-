import streamlit as st
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.auth import authenticate, save_user, check_user_exists, generate_otp, send_email_otp, reset_password
from src.components.user_page import render_user_page
from src.components.admin_page import render_admin_page
from src.components.chatbot import render_floating_chatbot
from src.utils.style import apply_custom_style

st.set_page_config(page_title="Smart Energy", layout="wide", page_icon="⚡")

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'show_login' not in st.session_state: st.session_state['show_login'] = False
if 'auth_mode' not in st.session_state: st.session_state['auth_mode'] = 'login'
if 'user_role' not in st.session_state: st.session_state['user_role'] = None
if 'reg_step' not in st.session_state: st.session_state['reg_step'] = 1
if 'reg_otp' not in st.session_state: st.session_state['reg_otp'] = None
if 'reg_data' not in st.session_state: st.session_state['reg_data'] = {}

def nav_to_login():
    st.session_state['show_login'] = True
    st.rerun()

def nav_to_home():
    st.session_state['show_login'] = False
    st.rerun()

def switch_mode(mode):
    st.session_state['auth_mode'] = mode
    st.session_state['reg_step'] = 1
    st.rerun()

# --- HOMEPAGE ---
def render_homepage():
    apply_custom_style()
    
    # Navbar
    c1, c2 = st.columns([6, 1])
    with c1: st.markdown('<h3 style="margin:0; color:#3b82f6;">⚡ Smart Energy</h3>', unsafe_allow_html=True)
    with c2: 
        if st.button("Đăng Nhập", type="primary"): nav_to_login()

    # Hero
    st.markdown("""
    <div class="hero-container">
        <h1 class="hero-title">Kiểm soát Năng lượng<br>Tối ưu Tương lai</h1>
            <p1 class="hero-desc">Giải pháp AI tiên tiến giúp bạn giám sát, dự báo và tối ưu hóa chi phí điện năng hiệu quả.</p1>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA
    _, c_mid, _ = st.columns([1, 1, 1])
    with c_mid:
        if st.button("🚀 Bắt đầu ngay miễn phí", use_container_width=True): nav_to_login()

    # Features
    st.markdown("<br><br>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1: st.markdown("""<div class="feature-card"><span class="feature-icon">🤖</span><h3>AI Dự Báo</h3><p>Dự báo chính xác hóa đơn điện.</p></div>""", unsafe_allow_html=True)
    with f2: st.markdown("""<div class="feature-card"><span class="feature-icon">📊</span><h3>Giám Sát</h3><p>Theo dõi tiêu thụ thời gian thực.</p></div>""", unsafe_allow_html=True)
    with f3: st.markdown("""<div class="feature-card"><span class="feature-icon">💬</span><h3>Trợ Lý Ảo</h3><p0>Hỗ trợ giải đáp 24/7.</p0></div>""", unsafe_allow_html=True)

    st.markdown("<br><br><div style='text-align:center; color:#64748b;'>© 2025 Smart Energy Inc.</div>", unsafe_allow_html=True)

# --- LOGIN PAGE ---
def login_page():
    if st.session_state['logged_in']: return
    apply_custom_style()
    
    if st.button("⬅ Quay lại trang chủ"): nav_to_home()

    # Layout căn giữa
    _, col_card, _ = st.columns([1, 1.2, 1])
    
    with col_card:
        # SỬ DỤNG CONTAINER ĐỂ TẠO KHUNG KÍNH (FIX LỖI GIAO DIỆN)
        with st.container(border=True):
            st.markdown("""
                <div class="login-header">
                    <div style="font-size: 40px; margin-bottom: 5px;">⚡</div>
                    <h1 class='brand-text'>Smart Energy</h1>
                    <p style="color:#94a3b8;">Cổng đăng nhập hệ thống</p>
                </div>
            """, unsafe_allow_html=True)

            if st.session_state['auth_mode'] == 'login':
                with st.form("login_form"):
                    u = st.text_input("Username", placeholder="Nhập tài khoản")
                    p = st.text_input("Password", type="password", placeholder="Nhập mật khẩu")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("🚀 Đăng Nhập"):
                        res = authenticate(u, p)
                        if res == "NOT_FOUND": st.error("Tài khoản không tồn tại!")
                        elif res == "WRONG_PASS": st.error("Sai mật khẩu.")
                        elif res:
                            st.session_state['logged_in'] = True
                            st.session_state['user_role'] = res['role']
                            st.session_state['username'] = u
                            st.session_state['full_name'] = res['name']
                            st.rerun()
                
                st.markdown("---")
                c1, c2 = st.columns(2)
                if c1.button("Tạo tài khoản"): switch_mode('register')
                if c2.button("Quên mật khẩu"): switch_mode('forgot')

            elif st.session_state['auth_mode'] == 'register':
                st.markdown("<h3 style='text-align:center'>Đăng Ký</h3>", unsafe_allow_html=True)
                if st.session_state['reg_step'] == 1:
                    name = st.text_input("Họ Tên", key="rn")
                    email = st.text_input("Email", key="re")
                    user = st.text_input("Username", key="ru")
                    pw = st.text_input("Password", type="password", key="rp")
                    if st.button("Gửi OTP", type="primary"):
                        if user and email:
                            if check_user_exists(user, email): st.error("Tài khoản đã tồn tại!")
                            else:
                                otp = generate_otp()
                                st.session_state['reg_otp'] = otp
                                st.session_state['reg_data'] = {"user": user, "pass": pw, "name": name, "email": email}
                                with st.spinner("Đang gửi mail..."):
                                    if send_email_otp(email, otp): st.success("Đã gửi OTP!")
                                    else: st.info(f"Demo OTP: {otp}")
                                st.session_state['reg_step'] = 2
                                st.rerun()
                        else: st.warning("Nhập đủ thông tin!")
                    if st.button("Quay lại"): switch_mode('login')

                elif st.session_state['reg_step'] == 2:
                    otp_in = st.text_input("Nhập mã OTP")
                    if st.button("Xác nhận"):
                        if otp_in == st.session_state['reg_otp']:
                            d = st.session_state['reg_data']
                            save_user(d['user'], d['pass'], d['name'], d['email'])
                            st.success("Thành công!")
                            time.sleep(1)
                            switch_mode('login')
                        else: st.error("Sai OTP")

            elif st.session_state['auth_mode'] == 'forgot':
                st.markdown("<h3 style='text-align:center'>Khôi Phục</h3>", unsafe_allow_html=True)
                with st.form("forgot"):
                    fu = st.text_input("Username")
                    fe = st.text_input("Email")
                    fp = st.text_input("Mật khẩu mới", type="password")
                    if st.form_submit_button("Đặt lại"):
                        if check_user_exists(fu, fe):
                            reset_password(fu, fp)
                            st.success("Xong! Đăng nhập lại.")
                            time.sleep(1)
                            switch_mode('login')
                        else: st.error("Sai thông tin.")
                if st.button("Quay lại"): switch_mode('login')

# --- MAIN ---
def main_app():
    apply_custom_style()
    st.sidebar.title("⚡ Smart Energy")
    st.sidebar.caption(f"Hi, {st.session_state['full_name']}")
    if st.sidebar.button("Đăng xuất"):
        st.session_state['logged_in'] = False
        st.session_state['show_login'] = False
        st.rerun()
    st.sidebar.markdown("---")
    
    if st.session_state['user_role'] == 'admin':
        render_admin_page()
    else:
        render_user_page(st.session_state['username'], st.session_state['full_name'])
        render_floating_chatbot()

if __name__ == "__main__":
    if st.session_state['logged_in']: main_app()
    elif st.session_state['show_login']: login_page()
    else: render_homepage()