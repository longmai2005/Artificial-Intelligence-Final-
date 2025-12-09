import json
import os
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

USER_DB_PATH = "data/users.json"

# --- CẤU HÌNH EMAIL (Thay bằng email thật của bạn nếu muốn chạy thật) ---
# Nếu chạy demo, bạn cứ để nguyên, hệ thống sẽ tự giả lập.
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com" 
SENDER_PASSWORD = "your_app_password" # Mật khẩu ứng dụng (Không phải mật khẩu đăng nhập Gmail)

def load_users():
    if not os.path.exists(USER_DB_PATH):
        default_users = {
            "admin": {"password": "123", "role": "admin", "name": "Administrator", "email": "admin@example.com"},
            "user": {"password": "123", "role": "user", "name": "User Demo", "email": "user@example.com"}
        }
        os.makedirs(os.path.dirname(USER_DB_PATH), exist_ok=True)
        with open(USER_DB_PATH, "w") as f:
            json.dump(default_users, f)
        return default_users
    
    with open(USER_DB_PATH, "r") as f:
        return json.load(f)

def save_user(username, password, name, email=""):
    users = load_users()
    if username in users:
        return False
    
    users[username] = {
        "password": password,
        "role": "user",
        "name": name,
        "email": email
    }
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f)
    return True

def authenticate(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        return users[username]
    return None

def check_user_exists(username, email):
    users = load_users()
    # Kiểm tra xem username hoặc email đã tồn tại chưa
    for u, data in users.items():
        if u == username or data.get('email') == email:
            return True
    return False

# --- LOGIC OTP & EMAIL ---

def generate_otp():
    """Tạo mã OTP 6 số ngẫu nhiên"""
    return ''.join(random.choices(string.digits, k=6))

def send_email_otp(receiver_email, otp_code):
    """
    Gửi email chứa OTP. 
    Nếu cấu hình sai hoặc lỗi mạng, sẽ trả về False (để chuyển sang chế độ giả lập).
    """
    subject = "🔑 Mã xác thực đăng ký Smart Energy"
    body = f"""
    <html>
    <body>
        <h2 style="color: #00C9FF;">Xác thực tài khoản Smart Energy Saver</h2>
        <p>Xin chào,</p>
        <p>Cảm ơn bạn đã đăng ký. Đây là mã xác thực (OTP) của bạn:</p>
        <h1 style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; display: inline-block; letter-spacing: 5px;">{otp_code}</h1>
        <p>Mã này sẽ hết hạn trong 5 phút. Vui lòng không chia sẻ cho ai khác.</p>
        <br>
        <p>Trân trọng,<br>Smart Energy Team</p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        # Thử kết nối đến Server Gmail
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True # Gửi thành công
    except Exception as e:
        print(f"Lỗi gửi email: {e}")
        return False # Gửi thất bại (Chuyển sang giả lập)