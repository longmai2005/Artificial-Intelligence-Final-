import streamlit as st
import sys
import os
import time

# --- IMPORT MODULES ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.auth import authenticate, save_user, check_user_exists, generate_otp, send_email_otp
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
# State cho quy trình đăng ký OTP
if 'reg_step' not in st.session_state:
    st.session_state['reg_step'] = 1 # 1: Nhập info, 2: Nhập OTP
if 'reg_otp' not in st.session_state:
    st.session_state['reg_otp'] = None
if 'reg_data' not in st.session_state:
    st.session_state['reg_data'] = {}

def login_page():
    if st.session_state['logged_in']:
        return

    apply_custom_style()
    
    # Giao diện căn giữa đẹp mắt
    col_spacer1, col_main, col_spacer2 = st.columns([1, 1.2, 1])
    
    with col_main:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; margin-bottom: 10px;'>⚡ Smart Energy</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; opacity: 0.7; margin-bottom: 30px;'>Hệ thống dự báo & tối ưu điện năng</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Đăng Nhập", "Đăng Ký Tài Khoản"])
        
        # --- TAB 1: ĐĂNG NHẬP ---
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Tên đăng nhập", placeholder="Nhập username...")
                password = st.text_input("Mật khẩu", type="password", placeholder="••••••")
                submit = st.form_submit_button("Đăng nhập")
                
                if submit:
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
                        st.error("Sai tài khoản hoặc mật khẩu.")

        # --- TAB 2: ĐĂNG KÝ (Có OTP) ---
        with tab2:
            # BƯỚC 1: NHẬP THÔNG TIN
            if st.session_state['reg_step'] == 1:
                st.caption("📝 Bước 1/2: Nhập thông tin cá nhân")
                new_user = st.text_input("Tên đăng nhập mới", key="reg_user")
                new_email = st.text_input("Email (để nhận OTP)", key="reg_email")
                full_name = st.text_input("Họ và Tên", key="reg_name")
                new_pass = st.text_input("Mật khẩu", type="password", key="reg_pass")
                
                if st.button("Gửi mã xác thực (OTP)", type="primary"):
                    if new_user and new_email and new_pass:
                        # Kiểm tra trùng lặp
                        if check_user_exists(new_user, new_email):
                            st.error("Username hoặc Email đã tồn tại!")
                        else:
                            # 1. Sinh OTP
                            otp_code = generate_otp()
                            st.session_state['reg_otp'] = otp_code
                            
                            # 2. Lưu tạm thông tin
                            st.session_state['reg_data'] = {
                                "user": new_user, "pass": new_pass, 
                                "name": full_name, "email": new_email
                            }
                            
                            # 3. Gửi Email (Có fallback giả lập)
                            with st.spinner("Đang gửi mã OTP đến email..."):
                                is_sent = send_email_otp(new_email, otp_code)
                                
                                if is_sent:
                                    st.success(f"Đã gửi OTP đến {new_email}!")
                                else:
                                    # CHẾ ĐỘ GIẢ LẬP (Nếu không gửi được email thật)
                                    st.warning("⚠️ Chế độ Demo (Do chưa cấu hình SMTP Gmail)")
                                    st.info(f"Mã OTP giả lập của bạn là: **{otp_code}**")
                            
                            # Chuyển sang bước 2
                            st.session_state['reg_step'] = 2
                            st.rerun()
                    else:
                        st.warning("Vui lòng điền đầy đủ thông tin.")

            # BƯỚC 2: XÁC THỰC OTP
            elif st.session_state['reg_step'] == 2:
                st.caption(f"🛡️ Bước 2/2: Xác thực OTP (Đã gửi tới {st.session_state['reg_data']['email']})")
                
                # Input OTP
                otp_input = st.text_input("Nhập mã 6 số", max_chars=6, key="otp_in", help="Kiểm tra email hoặc xem thông báo giả lập")
                
                col_back, col_conf = st.columns([1, 1])
                with col_back:
                    if st.button("Quay lại"):
                        st.session_state['reg_step'] = 1
                        st.rerun()
                with col_conf:
                    if st.button("Xác nhận Đăng ký", type="primary"):
                        if otp_input == st.session_state['reg_otp']:
                            # OTP Đúng -> Lưu User vào DB
                            data = st.session_state['reg_data']
                            save_user(data['user'], data['pass'], data['name'], data['email'])
                            
                            st.balloons() # Hiệu ứng chúc mừng
                            st.success("🎉 Đăng ký thành công! Đang chuyển về đăng nhập...")
                            
                            # Reset trạng thái
                            st.session_state['reg_step'] = 1
                            st.session_state['reg_otp'] = None
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("Mã OTP không chính xác!")

        st.markdown("</div>", unsafe_allow_html=True)

def main_app():
    apply_custom_style()
    
    # Sidebar
    st.sidebar.title("⚡ Smart Energy")
    st.sidebar.write(f"User: **{st.session_state['full_name']}**")
    
    if st.sidebar.button("Đăng xuất", type="primary"):
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
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