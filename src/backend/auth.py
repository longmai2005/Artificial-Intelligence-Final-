import json
import os
import smtplib
import random
import string
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
# IMPORT LOGGER
from src.backend.logger import log_info, log_warning, log_error

USER_DB_PATH = "data/users.json"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "longmai0520@gmail.com"
SENDER_PASSWORD = "fyxl jibq ohmi xeio"

def load_users():
    if not os.path.exists(USER_DB_PATH):
        default = {
            "admin": {
                "password": "123", 
                "role": "admin", 
                "name": "Administrator", 
                "email": "admin@test.com",
                "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        with open(USER_DB_PATH, "w") as f: json.dump(default, f)
        log_info("Khởi tạo database người dùng mặc định.") # LOG
        return default
    try:
        with open(USER_DB_PATH, "r") as f: return json.load(f)
    except: return {}

def save_db(users):
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f, indent=4)

def save_user(username, password, name, email=""):
    users = load_users()
    username = username.strip()
    if username in users: 
        log_warning(f"Đăng ký thất bại: User '{username}' đã tồn tại.") # LOG
        return False
    
    users[username] = {
        "password": password.strip(),
        "role": "user",
        "name": name.strip(),
        "email": email.strip(),
        "last_login": "Chưa đăng nhập"
    }
    save_db(users)
    log_info(f"Người dùng mới đăng ký: {username} ({email})") # LOG
    return True

def authenticate(username, password):
    users = load_users()
    username = username.strip()
    password = password.strip()
    
    if username not in users:
        log_warning(f"Đăng nhập thất bại: User '{username}' không tồn tại.") # LOG
        return "NOT_FOUND"
    
    if users[username]["password"] == password:
        # Update last login
        users[username]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_db(users)
        log_info(f"User '{username}' đã đăng nhập thành công.") # LOG THÀNH CÔNG
        return users[username]
    
    log_warning(f"Đăng nhập thất bại: User '{username}' sai mật khẩu.") # LOG SAI PASS
    return "WRONG_PASS"

def check_user_exists(username, email):
    users = load_users()
    for u, d in users.items():
        if u == username.strip() or d.get('email') == email.strip(): return True
    return False

def reset_password(username, new_password):
    users = load_users()
    username = username.strip()
    if username in users:
        users[username]["password"] = new_password.strip()
        save_db(users)
        log_info(f"User '{username}' đã đổi mật khẩu.") # LOG
        return True
    return False

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_email_otp(receiver_email, otp_code):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = "Mã xác thực Smart Energy"
        msg.attach(MIMEText(f"Mã OTP của bạn là: {otp_code}", 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        log_info(f"Gửi OTP thành công tới {receiver_email}") # LOG
        return True
    except Exception as e:
        log_error(f"Gửi email thất bại tới {receiver_email}: {str(e)}") # LOG LỖI
        return False