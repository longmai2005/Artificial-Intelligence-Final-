import pandas as pd

def format_currency(amount):
    """Định dạng số tiền sang VNĐ"""
    return f"{int(amount):,} VNĐ".replace(",", ".")

def map_date_to_current_year(df, target_year=2025):
    """
    Ánh xạ dữ liệu từ năm cũ sang năm mục tiêu (2025)
    nhưng vẫn giữ đúng Thứ trong tuần (Day of Week).
    """
    if df.empty:
        return df
        
    start_date_original = df.index[0]
    start_date_target = pd.Timestamp(f"{target_year}-01-01 00:00:00")
    
    time_delta = start_date_target - start_date_original
    
    df.index = df.index + time_delta
    return df