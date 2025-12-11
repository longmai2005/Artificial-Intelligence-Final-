import os
from datetime import datetime

# Đường dẫn file log (tự động tạo nếu chưa có)
LOG_FILE = "data/system.log"

def _write_log(level, message):
    """Hàm nội bộ để ghi log vào file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{level}] {timestamp} - {message}\n"
    
    try:
        # Đảm bảo thư mục data tồn tại
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        # Ghi nối tiếp (append) vào file, dùng encoding utf-8 để không lỗi tiếng Việt
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Lỗi ghi log: {e}")

def log_info(message):
    _write_log("INFO", message)

def log_warning(message):
    _write_log("WARN", message)

def log_error(message):
    _write_log("ERROR", message)

def get_recent_logs(limit=20):
    """Đọc n dòng log mới nhất để hiển thị lên Admin Dashboard"""
    if not os.path.exists(LOG_FILE):
        return ["⏳ Chưa có nhật ký hệ thống nào."]
    
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Lấy limit dòng cuối cùng và đảo ngược (Mới nhất lên đầu) để admin dễ xem
        return lines[-limit:][::-1]
    except Exception:
        return ["❌ Lỗi đọc file log."]