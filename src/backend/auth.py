import json
import os
import streamlit as st

USER_DB_PATH = "data/users.json"

def load_users():
    if not os.path.exists(USER_DB_PATH):
        default_users = {
            "admin": {"password": "123", "role": "admin", "name": "Administrator", "email": "admin@example.com"},
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

def reset_password(username, new_password):
    """Hàm đặt lại mật khẩu mới"""
    users = load_users()
    if username in users:
        users[username]["password"] = new_password
        with open(USER_DB_PATH, "w") as f:
            json.dump(users, f)
        return True
    return False

def check_user_exists(username, email):
    """Kiểm tra user có tồn tại để reset pass không"""
    users = load_users()
    if username in users and users[username].get("email") == email:
        return True
    return False