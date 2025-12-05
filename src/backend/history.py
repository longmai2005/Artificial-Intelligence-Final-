import json
import os
from datetime import datetime

HISTORY_FILE = "data/history.json"

def load_history(username):
    """Đọc lịch sử của một user cụ thể"""
    if not os.path.exists(HISTORY_FILE):
        return []
    
    with open(HISTORY_FILE, "r") as f:
        all_history = json.load(f)
    
    # Trả về list lịch sử của user đó, sắp xếp mới nhất lên đầu
    user_history = all_history.get(username, [])
    return user_history[::-1] 

def save_history(username, input_data, result_kwh, total_cost):
    """Lưu một lần dự báo vào file"""
    if not os.path.exists(HISTORY_FILE):
        all_history = {}
    else:
        with open(HISTORY_FILE, "r") as f:
            all_history = json.load(f)
    
    if username not in all_history:
        all_history[username] = []
        
    # Tạo bản ghi
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "inputs": input_data, # (Số máy lạnh, diện tích...)
        "kwh": round(result_kwh, 2),
        "cost": int(total_cost)
    }
    
    all_history[username].append(record)
    
    # Lưu lại
    with open(HISTORY_FILE, "w") as f:
        json.dump(all_history, f, indent=4)