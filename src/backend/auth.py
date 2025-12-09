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
SENDER_PASSWORD = "điền_mật_khẩu_ứng_dụng_vào_đây" # Nhớ điền App Password

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

# ... (Giữ nguyên các hàm gửi email, reset pass, generate_otp như cũ) ...
def reset_password(username, new_password):
    users = load_users()
    username = username.strip()
    if username in users:
        users[username]["password"] = new_password.strip()
        with open(USER_DB_PATH, "w") as f: json.dump(users, f)
        return True
    return False

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_email_otp(receiver_email, otp_code):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = "Smart Energy OTP"
        msg.attach(MIMEText(f"Mã OTP của bạn là: {otp_code}", 'plain'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except: return False