import json
import os
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

USER_DB_PATH = "data/users.json"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "longmai0520@gmail.com"
SENDER_PASSWORD = "fyxl jibq ohmi xeio"

def load_users():
    if not os.path.exists(USER_DB_PATH):
        default = {"admin": {"password": "123", "role": "admin", "name": "Admin", "email": "admin@test.com"}}
        with open(USER_DB_PATH, "w") as f: json.dump(default, f)
        return default
    try:
        with open(USER_DB_PATH, "r") as f: return json.load(f)
    except: return {}

def save_user(username, password, name, email=""):
    users = load_users()
    username = username.strip()
    if username in users: return False
    users[username] = {"password": password.strip(), "role": "user", "name": name.strip(), "email": email.strip()}
    with open(USER_DB_PATH, "w") as f: json.dump(users, f)
    return True

def authenticate(username, password):
    users = load_users()
    username = username.strip()
    password = password.strip()
    
    # 1. Kiểm tra user có tồn tại không
    if username not in users:
        return "NOT_FOUND" # Trả về mã lỗi riêng
    
    # 2. Kiểm tra mật khẩu
    if users[username]["password"] == password:
        return users[username] # Trả về thông tin user
    
    return "WRONG_PASS" # Sai mật khẩu

def check_user_exists(username, email):
    users = load_users()
    for u, d in users.items():
        if u == username.strip() or d.get('email') == email.strip(): return True
    return False

def reset_password(username, new_password):
    users = load_users()
    if username in users:
        users[username]["password"] = new_password
        with open(USER_DB_PATH, "w") as f:
            json.dump(users, f)
        return True
    return False

def generate_otp():
    """Tạo mã OTP 6 số ngẫu nhiên"""
    return ''.join(random.choices(string.digits, k=6))

def send_email_otp(receiver_email, otp_code):
    """Gửi email chứa OTP"""
    subject = "🔑 Mã xác thực đăng ký Smart Energy"
    body = f"""
    <html>
    <body>
        <h2 style="color: #00C9FF;">Xác thực tài khoản Smart Energy Saver</h2>
        <p>Xin chào,</p>
        <p>Cảm ơn bạn đã đăng ký. Đây là mã xác thực (OTP) của bạn:</p>
        <h1 style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; display: inline-block; letter-spacing: 5px;">{otp_code}</h1>
        <p>Mã này sẽ hết hạn trong 5 phút.</p>
        <p><i>(Email được gửi tự động từ hệ thống Smart Energy Saver)</i></p>
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
        # Đăng nhập bằng Mật khẩu ứng dụng (App Password)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True # Gửi thành công
    except Exception as e:
        print(f"Lỗi gửi email: {e}")
        return False # Gửi thất bại