import streamlit as st
import sys
import os
import time

# 1. Cấu hình trang
st.set_page_config(page_title="Smart Energy", layout="wide", page_icon="⚡")

# 2. Thiết lập đường dẫn import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 3. Import các module dự án
from src.backend.auth import authenticate, save_user, check_user_exists, generate_otp, send_email_otp, reset_password
from src.components.user_page import render_user_page
from src.components.admin_page import render_admin_page
from src.components.chatbot import render_floating_chatbot
from src.utils.style import apply_custom_style

# 4. Khởi tạo Session State (Trạng thái ứng dụng)
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'show_login' not in st.session_state: st.session_state['show_login'] = False # True: Hiện trang Login, False: Hiện Homepage
if 'auth_mode' not in st.session_state: st.session_state['auth_mode'] = 'login' # Các chế độ: 'login', 'register', 'forgot'
if 'user_role' not in st.session_state: st.session_state['user_role'] = None
if 'reg_step' not in st.session_state: st.session_state['reg_step'] = 1
if 'reg_otp' not in st.session_state: st.session_state['reg_otp'] = None
if 'reg_data' not in st.session_state: st.session_state['reg_data'] = {}

# --- HÀM ĐIỀU HƯỚNG ---
def nav_to_login():
    st.session_state['show_login'] = True
    st.session_state['auth_mode'] = 'login' # Luôn vào login trước
    st.rerun()

def nav_to_home():
    st.session_state['show_login'] = False
    st.rerun()

def switch_mode(mode):
    """Chuyển đổi giữa Đăng nhập / Đăng ký / Quên MK"""
    st.session_state['auth_mode'] = mode
    st.session_state['reg_step'] = 1 # Reset bước đăng ký
    st.rerun()

# --- GIAO DIỆN HOMEPAGE (TRANG CHỦ) ---
def render_homepage():
    apply_custom_style()
    
    # Navbar
    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown('<div style="font-size:1.8rem; font-weight:800; background:linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">⚡ Smart Energy</div>', unsafe_allow_html=True)
    with c2:
        if st.button("Đăng Nhập / Đăng Ký", type="primary", width='stretch'):
            nav_to_login()

    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <h1 class="hero-title">Kiểm soát Năng lượng<br>Tối ưu Tương lai</h1>
        <p1 class="hero-desc">
            Nền tảng AI tiên tiến giúp bạn giám sát, dự báo và cắt giảm đến 30% chi phí điện năng mỗi tháng. Đơn giản, Hiệu quả và Tự động hóa.
        </p1>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Button
    _, c_cta, _ = st.columns([1, 1, 1])
    with c_cta:
        if st.button("🚀 Bắt đầu ngay bây giờ", width='stretch'):
            nav_to_login()

    # Features Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    
    with f1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🤖</span>
            <h3 class="feature-title">AI Dự Báo</h3>
            <p>Mô hình Deep Learning phân tích thói quen để dự báo hóa đơn chính xác.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with f2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <h3 class="feature-title">Giám Sát</h3>
            <p>Theo dõi tiêu thụ điện thời gian thực, phát hiện thiết bị tiêu tốn năng lượng.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with f3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">💬</span>
            <h3 class="feature-title">Trợ Lý Ảo</h3>
            <p>Chatbot AI hỗ trợ giải đáp thắc mắc và đưa ra mẹo tiết kiệm 24/7.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='text-align:center; color:#64748b;'>© 2025 Smart Energy Inc.</div>", unsafe_allow_html=True)

# --- GIAO DIỆN LOGIN / REGISTER / FORGOT ---
def login_page():
    if st.session_state['logged_in']: return
    apply_custom_style()
    
    # Nút quay về Home
    if st.button("⬅ Về Trang chủ"): nav_to_home()

    # Layout căn giữa
    _, col_card, _ = st.columns([1, 1.2, 1])
    
    with col_card:
        # Container tạo khung kính mờ
        with st.container(border=True):
            st.markdown("""
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 40px;">⚡</div>
                    <h1 class='brand-text'>Smart Energy</h1>
                    <p style="color:#94a3b8;">Hệ thống quản lý năng lượng thông minh</p>
                </div>
            """, unsafe_allow_html=True)

            # === MODE 1: ĐĂNG NHẬP ===
            if st.session_state['auth_mode'] == 'login':
                st.markdown("<h3 style='text-align:center'>Đăng Nhập</h3>", unsafe_allow_html=True)
                
                # Khởi tạo biến lưu lỗi trong session nếu chưa có
                if 'login_error' not in st.session_state: 
                    st.session_state['login_error'] = None

                with st.form("login_form"):
                    u = st.text_input("Tài khoản", placeholder="Username")
                    p = st.text_input("Mật khẩu", type="password", placeholder="••••••")
                    
                    submit = st.form_submit_button("🚀 Đăng nhập")
                    
                    if submit:
                        res = authenticate(u, p)
                        if res == "NOT_FOUND": 
                            st.session_state['login_error'] = "❌ Tài khoản không tồn tại!"
                        elif res == "WRONG_PASS": 
                            st.session_state['login_error'] = "❌ Sai mật khẩu."
                        elif res:
                            # Nếu đăng nhập đúng, xóa lỗi và thực hiện đăng nhập
                            st.session_state['login_error'] = None 
                            st.session_state['logged_in'] = True
                            st.session_state['user_role'] = res['role']
                            st.session_state['username'] = u
                            st.session_state['full_name'] = res['name']
                            st.toast("Đăng nhập thành công!", icon="🟢")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            # Trường hợp mặc định nếu authenticate trả về None chung chung
                            st.session_state['login_error'] = "❌ Lỗi hệ thống, vui lòng thử lại."

                # HIỂN THỊ LỖI Ở ĐÂY (Bên ngoài form để không bị mất khi rerun)
                if st.session_state['login_error']:
                    st.error(st.session_state['login_error'])
                
                
                # Các nút chuyển hướng
                st.markdown("---")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✨ Tạo tài khoản"): switch_mode('register')
                with c2:
                    if st.button("❓ Quên mật khẩu"): switch_mode('forgot')

            # === MODE 2: ĐĂNG KÝ (Có OTP) ===
            elif st.session_state['auth_mode'] == 'register':
                st.markdown("<h3 style='text-align:center'>Đăng Ký</h3>", unsafe_allow_html=True)
                
                # Bước 1: Nhập thông tin
                if st.session_state['reg_step'] == 1:
                    name = st.text_input("Họ và Tên", key="reg_name")
                    email = st.text_input("Email (Nhận OTP)", key="reg_email")
                    user = st.text_input("Username", key="reg_user")
                    pw = st.text_input("Password", type="password", key="reg_pass")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Gửi mã OTP ➤", type="primary"):
                        if user and email and pw:
                            if check_user_exists(user, email):
                                st.error("⚠️ Username hoặc Email đã tồn tại!")
                            else:
                                otp = generate_otp()
                                st.session_state['reg_otp'] = otp
                                st.session_state['reg_data'] = {"user": user, "pass": pw, "name": name, "email": email}
                                
                                with st.spinner("Đang gửi OTP..."):
                                    sent = send_email_otp(email, otp)
                                    if sent: st.success(f"Đã gửi OTP tới {email}")
                                    else: st.info(f"Demo OTP: {otp}") # Fallback cho demo
                                
                                st.session_state['reg_step'] = 2
                                st.rerun()
                        else:
                            st.warning("Vui lòng nhập đầy đủ thông tin!")
                    
                    if st.button("⬅ Quay lại Đăng nhập"): switch_mode('login')

                # Bước 2: Xác thực OTP
                elif st.session_state['reg_step'] == 2:
                    st.info(f"Nhập mã OTP đã gửi tới: {st.session_state['reg_data']['email']}")
                    otp_in = st.text_input("Mã xác thực (6 số)", max_chars=6)
                    
                    if st.button("✅ Xác nhận & Hoàn tất", type="primary"):
                        if otp_in == st.session_state['reg_otp']:
                            d = st.session_state['reg_data']
                            save_user(d['user'], d['pass'], d['name'], d['email'])
                            st.balloons()
                            st.success("Tạo tài khoản thành công! Đang chuyển về đăng nhập...")
                            time.sleep(1.5)
                            switch_mode('login')
                        else:
                            st.error("❌ Mã OTP không chính xác.")
                    
                    if st.button("Hủy bỏ"): switch_mode('login')

            # === MODE 3: QUÊN MẬT KHẨU ===
            elif st.session_state['auth_mode'] == 'forgot':
                st.markdown("<h3 style='text-align:center'>Khôi Phục Mật Khẩu</h3>", unsafe_allow_html=True)
                with st.form("forgot_form"):
                    fu = st.text_input("Username")
                    fe = st.text_input("Email đăng ký")
                    fp = st.text_input("Mật khẩu mới", type="password")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("Đặt lại mật khẩu"):
                        if check_user_exists(fu, fe):
                            reset_password(fu, fp)
                            st.success("Thành công! Vui lòng đăng nhập lại.")
                            time.sleep(1.5)
                            switch_mode('login')
                        else:
                            st.error("Thông tin không khớp với hệ thống.")
                
                if st.button("⬅ Quay lại"): switch_mode('login')

# --- LOGIC CHÍNH SAU KHI ĐĂNG NHẬP ---
def main_app():
    apply_custom_style()
    
    # Sidebar thông tin
    st.sidebar.title("⚡ Smart Energy")
    st.sidebar.write(f"Xin chào, **{st.session_state['full_name']}**")
    
    # Nút Đăng xuất
    if st.sidebar.button("Đăng xuất"):
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
        st.session_state['show_login'] = False # Về Homepage
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Phân quyền Admin / User
    if st.session_state['user_role'] == 'admin':
        render_admin_page()
    else:
        render_user_page(st.session_state['username'], st.session_state['full_name'])
        render_floating_chatbot()

# --- ĐIỂM KHỞI CHẠY (ENTRY POINT) ---
if __name__ == "__main__":
    if st.session_state['logged_in']:
        main_app()
    elif st.session_state['show_login']:
        login_page()
    else:
        render_homepage()