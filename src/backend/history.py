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

def clear_history(username):
    """
    Xóa lịch sử của một user cụ thể trong file JSON chung
    """
    if not os.path.exists(HISTORY_FILE):
        return False
    
    try:
        # 1. Đọc dữ liệu hiện có
        with open(HISTORY_FILE, "r") as f:
            all_history = json.load(f)
        
        # 2. Kiểm tra và xóa user
        if username in all_history:
            del all_history[username] # Xóa key của user này
            
            # 3. Lưu lại file đã cập nhật
            with open(HISTORY_FILE, "w") as f:
                json.dump(all_history, f, indent=4)
            return True
        else:
            return False # User chưa có lịch sử
            
    except Exception as e:
        print(f"Lỗi khi xóa lịch sử: {e}")
        return False
    
def delete_selected_history(username, timestamps_to_delete):
    """
    Xóa các bản ghi cụ thể dựa trên danh sách timestamp
    """
    if not os.path.exists(HISTORY_FILE):
        return False
    
    try:
        with open(HISTORY_FILE, "r") as f:
            all_history = json.load(f)
        
        if username in all_history:
            # Giữ lại những bản ghi KHÔNG nằm trong danh sách cần xóa
            # (Lọc ngược: Chỉ lấy những cái không bị xóa)
            original_list = all_history[username]
            new_list = [
                record for record in original_list 
                if record.get('timestamp') not in timestamps_to_delete
            ]
            
            # Cập nhật lại danh sách cho user
            all_history[username] = new_list
            
            # Lưu file
            with open(HISTORY_FILE, "w") as f:
                json.dump(all_history, f, indent=4)
            return True
        return False
    except Exception as e:
        print(f"Lỗi khi xóa dòng đã chọn: {e}")
        return False