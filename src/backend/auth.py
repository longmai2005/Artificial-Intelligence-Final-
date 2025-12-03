import json
import os
import streamlit as st

USER_DB_PATH = "data/users.json"

def load_users():
    """Đọc database user từ file json"""
    if not os.path.exists(USER_DB_PATH):
        # Tạo user mặc định nếu chưa có file
        default_users = {
            "admin": {"password": "123", "role": "admin", "name": "Administrator"},
            "user": {"password": "123", "role": "user", "name": "Người dùng Demo"}
        }
        os.makedirs(os.path.dirname(USER_DB_PATH), exist_ok=True)
        with open(USER_DB_PATH, "w") as f:
            json.dump(default_users, f)
        return default_users
    
    with open(USER_DB_PATH, "r") as f:
        return json.load(f)

def save_user(username, password, name):
    """Lưu user mới"""
    users = load_users()
    if username in users:
        return False # User đã tồn tại
    
    users[username] = {
        "password": password,
        "role": "user", # Mặc định đăng ký mới là user thường
        "name": name
    }
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f)
    return True

def authenticate(username, password):
    """Kiểm tra đăng nhập"""
    users = load_users()
    if username in users and users[username]["password"] == password:
        return users[username]
    return None