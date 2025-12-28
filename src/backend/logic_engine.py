def calculate_evn_bill(kwh):
    """
    Tính tiền điện theo biểu giá bậc thang sinh hoạt EVN
    CÓ CỘNG THÊM THUẾ VAT VÀ DÒNG TỔNG CỘNG
    """
    # Biểu giá bán lẻ điện sinh hoạt (Quyết định 2941/QĐ-BCT) - Chưa VAT
    tiers = [
        (50, 1806),
        (50, 1866),
        (100, 2167),
        (100, 2729),
        (100, 3050),
        (float('inf'), 3151)
    ]
    
    total_bill_pre_tax = 0
    remaining_kwh = kwh
    breakdown = [] 
    
    for limit, price in tiers:
        if remaining_kwh <= 0:
            break
        
        used = min(remaining_kwh, limit)
        cost = used * price
        total_bill_pre_tax += cost
        remaining_kwh -= used
        
        breakdown.append(f"• {used:.1f} kWh x {price:,}đ = {int(cost):,}đ")
    
    # --- TÍNH TOÁN THUẾ ---
    VAT_RATE = 0.08  # 8% (Hoặc đổi thành 0.10 tùy thời điểm)
    vat_cost = total_bill_pre_tax * VAT_RATE
    total_bill_final = total_bill_pre_tax + vat_cost
    
    # --- CẬP NHẬT HIỂN THỊ CHI TIẾT ---
    breakdown.append(f"-------------------------")
    breakdown.append(f"• Tổng trước thuế: {int(total_bill_pre_tax):,}đ")
    breakdown.append(f"• Thuế GTGT ({int(VAT_RATE*100)}%): {int(vat_cost):,}đ")
    
    # DÒNG QUAN TRỌNG: Hiển thị tổng cuối cùng để khớp với con số to bên ngoài
    breakdown.append(f"👉 TỔNG THANH TOÁN: {int(total_bill_final):,}đ")
    
    return int(total_bill_final), breakdown