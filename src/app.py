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

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'show_login' not in st.session_state: st.session_state['show_login'] = False
if 'auth_mode' not in st.session_state: st.session_state['auth_mode'] = 'login'
if 'user_role' not in st.session_state: st.session_state['user_role'] = None
if 'reg_step' not in st.session_state: st.session_state['reg_step'] = 1
if 'reg_otp' not in st.session_state: st.session_state['reg_otp'] = None
if 'reg_data' not in st.session_state: st.session_state['reg_data'] = {}

def nav_to_login(): st.session_state['show_login'] = True; st.rerun()
def nav_to_home(): st.session_state['show_login'] = False; st.rerun()
def switch_mode(mode): st.session_state['auth_mode'] = mode; st.session_state['reg_step'] = 1; st.rerun()

def render_homepage():
    apply_custom_style()
    c1, c2 = st.columns([6, 1])
    with c1: st.markdown('<h3 style="margin:0; color:#3b82f6;">⚡ Smart Energy</h3>', unsafe_allow_html=True)
    with c2: 
        if st.button("Đăng Nhập / Đăng Ký", type="primary"): nav_to_login()

    st.markdown("""
    <div class="hero-container">
        <h1 class="hero-title">Kiểm soát Năng lượng<br>Tối ưu Tương lai</h1>
        <p1 style="font-size:1.2rem; opacity:0.8;">Giải pháp AI tiên tiến giúp giám sát, dự báo và tiết kiệm chi phí điện năng.</p1>
    </div>
    """, unsafe_allow_html=True)
    
    _, c_cta, _ = st.columns([1, 1, 1])
    with c_cta:
        if st.button("🚀 Bắt đầu ngay bây giờ", use_container_width=True): nav_to_login()

    st.markdown("<br><br>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1: st.info("🤖 **AI Dự Báo**: Deep Learning phân tích thói quen.")
    with f2: st.success("📊 **Giám Sát**: Theo dõi tiêu thụ điện thời gian thực.")
    with f3: st.warning("💬 **Trợ Lý Ảo**: Chatbot AI giải đáp 24/7.")

def login_page():
    if st.session_state['logged_in']: return
    apply_custom_style()
    
    if st.button("⬅ Trang chủ"): nav_to_home()

    _, col_card, _ = st.columns([1, 1.2, 1])
    with col_card:
        with st.container(border=True):
            st.markdown("<h2 style='text-align:center;'>🔐 Đăng Nhập</h2>", unsafe_allow_html=True)
            
            if st.session_state['auth_mode'] == 'login':
                with st.form("login_form"):
                    u = st.text_input("Tài khoản")
                    p = st.text_input("Mật khẩu", type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("🚀 Đăng nhập"):
                        res = authenticate(u, p)
                        if res == "NOT_FOUND": st.error("Tài khoản không tồn tại!")
                        elif res == "WRONG_PASS": st.error("Sai mật khẩu.")
                        elif res:
                            st.session_state['logged_in'] = True
                            st.session_state['user_role'] = res['role']
                            st.session_state['username'] = u
                            st.session_state['full_name'] = res['name']
                            st.success("Thành công!")
                            time.sleep(0.5)
                            st.rerun()
                
                c1, c2 = st.columns(2)
                if c1.button("Tạo tài khoản"): switch_mode('register')
                if c2.button("Quên mật khẩu"): switch_mode('forgot')

            elif st.session_state['auth_mode'] == 'register':
                st.markdown("### Đăng Ký")
                # (Phần code đăng ký giữ nguyên như logic cũ...)
                if st.button("Quay lại"): switch_mode('login')

            elif st.session_state['auth_mode'] == 'forgot':
                st.markdown("### Khôi Phục")
                if st.button("Quay lại"): switch_mode('login')

def main_app():
    apply_custom_style()
    st.sidebar.title("⚡ Smart Energy")
    st.sidebar.write(f"Xin chào, **{st.session_state['full_name']}**")
    
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