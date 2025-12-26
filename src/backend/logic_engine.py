def calculate_evn_bill(kwh):
    """
    Tính tiền điện theo biểu giá bậc thang sinh hoạt EVN (Cập nhật mới nhất)
    """
    # Bảng giá bậc thang (kWh mốc, Giá VNĐ)
    # Bậc 1: 0 - 50 kWh: 1.806 đồng/kWh
    # Bậc 2: 51 - 100 kWh: 1.866 đồng/kWh
    # Bậc 3: 101 - 200 kWh: 2.167 đồng/kWh
    # Bậc 4: 201 - 300 kWh: 2.729 đồng/kWh
    # Bậc 5: 301 - 400 kWh: 3.050 đồng/kWh
    # Bậc 6: 401 trở lên: 3.151 đồng/kWh
    
    tiers = [
        (50, 1806),
        (50, 1866),  # 50 số tiếp theo (51-100)
        (100, 2167), # 100 số tiếp theo (101-200)
        (100, 2729), # 100 số tiếp theo (201-300)
        (100, 3050), # 100 số tiếp theo (301-400)
        (float('inf'), 3151) # Còn lại
    ]
    
    total_bill = 0
    remaining_kwh = kwh
    breakdown = [] # Để hiển thị chi tiết cho user xem
    
    for limit, price in tiers:
        if remaining_kwh <= 0:
            break
        
        used = min(remaining_kwh, limit)
        cost = used * price
        total_bill += cost
        remaining_kwh -= used
        
        breakdown.append(f"• {used:.1f} kWh x {price:,}đ = {int(cost):,}đ")
        
    return int(total_bill), breakdown

def calculate_cost(power_kw, hour):
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
