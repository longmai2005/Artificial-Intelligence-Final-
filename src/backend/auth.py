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
    """Luôn đọc lại file để đảm bảo có dữ liệu mới nhất"""
    if not os.path.exists(USER_DB_PATH):
        default_users = {
            "admin": {"password": "123", "role": "admin", "name": "Administrator", "email": "admin@example.com"},
            "user": {"password": "123", "role": "user", "name": "User Demo", "email": "user@example.com"}
        }
        os.makedirs(os.path.dirname(USER_DB_PATH), exist_ok=True)
        with open(USER_DB_PATH, "w") as f:
            json.dump(default_users, f)
        return default_users
    
    try:
        with open(USER_DB_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {} # Trả về rỗng nếu file lỗi

def save_user(username, password, name, email=""):
    users = load_users()
    # Xóa khoảng trắng thừa
    username = username.strip()
    
    if username in users:
        return False
    
    users[username] = {
        "password": password.strip(),
        "role": "user",
        "name": name.strip(),
        "email": email.strip()
    }
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f)
    return True

def authenticate(username, password):
    users = load_users()
    # Quan trọng: Xóa khoảng trắng thừa khi người dùng nhập
    username = username.strip()
    password = password.strip()
    
    if username in users and users[username]["password"] == password:
        return users[username]
    return None

def check_user_exists(username, email):
    users = load_users()
    username = username.strip()
    email = email.strip()
    
    for u, data in users.items():
        if u == username and data.get('email') == email: # Phải khớp cả user lẫn email
            return True
    return False

def reset_password(username, new_password):
    users = load_users()
    username = username.strip()
    
    if username in users:
        users[username]["password"] = new_password.strip()
        with open(USER_DB_PATH, "w") as f:
            json.dump(users, f)
        return True
    return False

# ... (Giữ nguyên các hàm gửi email generate_otp, send_email_otp như cũ) ...
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_email_otp(receiver_email, otp_code):
    subject = "🔑 Mã xác thực đăng ký Smart Energy"
    body = f"""
    <html>
    <body>
        <h2 style="color: #00C9FF;">Xác thực tài khoản Smart Energy Saver</h2>
        <p>Mã OTP của bạn là:</p>
        <h1 style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; display: inline-block;">{otp_code}</h1>
        <p>Mã hết hạn sau 5 phút.</p>
    </body>
    </html>
    """
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Lỗi gửi email: {e}")
        return False