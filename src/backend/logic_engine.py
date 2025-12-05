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

# Giữ lại các hàm cũ nếu cần, hoặc cập nhật hàm logic cũ để dùng cái mới này
def calculate_cost(power_kw, hour):
    # Hàm cũ dùng cho realtime dashboard (giữ nguyên để không lỗi code cũ)
    return power_kw * 2500 

def generate_insights(current_hour, power, sub_meters):
    # (Giữ nguyên code cũ của hàm này...)
    insights = []
    # ... code logic cũ ...
    if not insights:
        insights.append({"type": "success", "msg": "Hệ thống hoạt động tối ưu.", "action": "Duy trì thói quen tốt!"})
    return insights