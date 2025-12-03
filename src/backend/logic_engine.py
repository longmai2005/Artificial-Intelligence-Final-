def calculate_cost(power_kw, hour):
    """Tính tiền điện dựa trên giờ cao điểm/thấp điểm"""
    # Giá điện giả định (VNĐ)
    PRICE_LOW = 1800
    PRICE_NORMAL = 2500
    PRICE_PEAK = 4500
    
    # Khung giờ cao điểm: 9h-11h, 17h-20h
    if 9 <= hour <= 11 or 17 <= hour <= 20:
        return power_kw * PRICE_PEAK
    elif 22 <= hour or hour <= 6:
        return power_kw * PRICE_LOW
    else:
        return power_kw * PRICE_NORMAL

def generate_insights(current_hour, power, sub_meters):
    """Tạo các action items dựa trên dữ liệu"""
    insights = []
    sub1, sub2, sub3 = sub_meters
    
    # Check giờ cao điểm
    is_peak = (9 <= current_hour <= 11) or (17 <= current_hour <= 20)
    
    if is_peak:
        if sub3 > 10: # Máy lạnh/Nóng lạnh cao
            saving = calculate_cost(sub3 * 60/1000, current_hour) * 0.2 # Giả sử tiết kiệm 20%
            insights.append({
                "type": "warning",
                "msg": "Cảnh báo cao điểm: Máy lạnh/Bình nóng lạnh đang hoạt động mạnh.",
                "action": f"Giảm nhiệt độ để tiết kiệm ~{int(saving)}đ/giờ."
            })
        if sub2 > 5: # Giặt là
             insights.append({
                "type": "info",
                "msg": "Phát hiện máy giặt đang chạy trong giờ giá cao.",
                "action": "Nên dời sang sau 22:00."
            })
            
    if not insights:
        insights.append({"type": "success", "msg": "Hệ thống hoạt động tối ưu.", "action": "Duy trì thói quen tốt!"})
        
    return insights