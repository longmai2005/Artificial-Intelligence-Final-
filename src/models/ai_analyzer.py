"""
Module AI Analyzer - Phân tích thông minh về tiêu thụ điện
Tích hợp với Google Gemini để tạo đề xuất cá nhân hóa
"""

import google.generativeai as genai
from datetime import datetime

GOOGLE_API_KEY = "AIzaSyA9KbCCUBWqMbTnA2V0kLuvTyaHLHZA3YY"

def analyze_with_gemini(total_kwh, breakdown, user_inputs):
    
    if not GOOGLE_API_KEY:
        return generate_fallback_analysis(total_kwh, breakdown, user_inputs)
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Tạo prompt chi tiết
        prompt = f"""
Bạn là chuyên gia tư vấn tiết kiệm năng lượng tại Việt Nam. Hãy phân tích dữ liệu tiêu thụ điện sau và đưa ra đề xuất CỤ THỂ, DỄ THỰC HIỆN:

📊 THÔNG TIN HỘ GIA ĐÌNH:
- Loại nhà: {user_inputs['house_type']}
- Diện tích: {user_inputs['area_m2']}m²
- Số người: {user_inputs['num_people']} người
- Máy lạnh: {user_inputs['num_ac']} cái
- Tủ lạnh: {user_inputs['num_fridge']} cái
- TV: {user_inputs['num_tv']} cái
- Thời gian sử dụng: {user_inputs['hours_per_day']} giờ/ngày

⚡ DỰ ĐOÁN TIÊU THỤ:
- Tổng: {total_kwh:.0f} kWh/tháng
- Phân bổ:
{chr(10).join([f"  • {device}: {kwh:.0f} kWh ({kwh/total_kwh*100:.1f}%)" for device, kwh in breakdown.items()])}

📋 YÊU CẦU PHÂN TÍCH:

1. Đánh giá tổng quan (1-2 câu ngắn gọn)
2. Phân tích TOP 3 điểm CẦN CẢI THIỆN cụ thể
3. ĐỀ XUẤT 5 HÀNH ĐỘNG NGAY LẬP TỨC:
   - Mỗi hành động phải CỤ THỂ, CÓ SỐ LIỆU
   - Nêu rõ TIẾT KIỆM ƯỚC TÍNH (kWh + tiền)
   - Độ khó thực hiện: Dễ/Trung bình/Khó

4. Lộ trình 30 ngày:
   - Tuần 1: Làm gì?
   - Tuần 2-3: Làm gì?
   - Tuần 4: Kiểm tra & điều chỉnh

Hãy trả lời NGẮN GỌN, DỄ HIỂU, THỰC TẾ cho người Việt Nam. Sử dụng emoji phù hợp.
"""
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        print(f"Lỗi Gemini API: {e}")
        return generate_fallback_analysis(total_kwh, breakdown, user_inputs)


def generate_fallback_analysis(total_kwh, breakdown, user_inputs):
    """
    Phân tích dự phòng khi không có Gemini API
    """
    
    # Xác định mức tiêu thụ
    if total_kwh > 400:
        level = "RẤT CAO ⚠️"
        status_msg = "Hóa đơn điện của bạn đang ở mức báo động!"
    elif total_kwh > 300:
        level = "CAO 🟡"
        status_msg = "Bạn có thể tiết kiệm nhiều hơn nữa."
    elif total_kwh > 200:
        level = "TRUNG BÌNH 🟢"
        status_msg = "Mức tiêu thụ hợp lý, nhưng vẫn có thể tối ưu."
    else:
        level = "THẤP ✅"
        status_msg = "Tuyệt vời! Bạn đang quản lý điện năng rất tốt."
    
    # Tìm thiết bị tiêu thụ nhiều nhất
    max_device = max(breakdown.items(), key=lambda x: x[1])
    
    analysis = f"""
## 📊 ĐÁNH GIÁ TỔNG QUAN

Mức tiêu thụ: **{level}** ({total_kwh:.0f} kWh/tháng)

{status_msg}

---

## 🎯 PHÂN TÍCH CHI TIẾT

### 1️⃣ Thiết bị tiêu thụ nhiều nhất: **{max_device[0]}**
- Chiếm **{max_device[1]/total_kwh*100:.1f}%** tổng tiêu thụ ({max_device[1]:.0f} kWh/tháng)
- Tiềm năng tiết kiệm: ~**{max_device[1]*0.2:.0f} kWh** = **{max_device[1]*0.2*2500:,.0f}đ**/tháng

### 2️⃣ So sánh với hộ gia đình trung bình
- Trung bình VN: 250 kWh/tháng
- Bạn: {total_kwh:.0f} kWh/tháng
- Chênh lệch: {"+" if total_kwh > 250 else ""}{total_kwh-250:.0f} kWh ({(total_kwh-250)/250*100:.0f}%)

### 3️⃣ Phân bổ chi tiêu
"""
    
    for device, kwh in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
        percent = (kwh / total_kwh) * 100
        analysis += f"\n- {device}: {kwh:.0f} kWh ({percent:.0f}%)"
    
    analysis += """

---

## 💡 5 HÀNH ĐỘNG TIẾT KIỆM NGAY

### ❄️ Điều hòa (Dễ - Hiệu quả cao)
- **Hành động:** Tăng nhiệt độ lên 26-27°C
- **Tiết kiệm:** ~40-50 kWh/tháng ≈ **100,000-125,000đ**
- **Cách làm:** Mỗi độ tăng = tiết kiệm 5-10%

### 💡 Chiếu sáng (Dễ)
- **Hành động:** Thay bóng LED toàn bộ nhà
- **Tiết kiệm:** ~30 kWh/tháng ≈ **75,000đ**
- **Chi phí đầu tư:** ~500,000đ (hoàn vốn sau 6 tháng)

### 🔌 Thiết bị Chờ (Rất dễ)
- **Hành động:** Rút phích cắm khi không dùng
- **Tiết kiệm:** ~15-20 kWh/tháng ≈ **40,000-50,000đ**
- **Tips:** Dùng ổ cắm có công tắc

### 🧊 Tủ lạnh (Dễ)
- **Hành động:** Không để đồ nóng, kiểm tra gioăng
- **Tiết kiệm:** ~10 kWh/tháng ≈ **25,000đ**
- **Bonus:** Giảm hao mòn máy

### ⏰ Thời gian sử dụng (Trung bình)
- **Hành động:** Tránh giờ cao điểm (18h-22h)
- **Tiết kiệm:** ~5-10% hóa đơn
- **Cách làm:** Dùng hẹn giờ cho máy giặt, nấu cơm

---

## 📅 LỘ TRÌNH 30 NGÀY

### 🗓️ Tuần 1 (Ngày 1-7): Bắt đầu dễ
- [ ] Điều chỉnh nhiệt độ máy lạnh
- [ ] Rút phích cắm thiết bị không dùng
- [ ] Ghi lại số điện hàng ngày

### 🗓️ Tuần 2-3 (Ngày 8-21): Nâng cấp
- [ ] Thay 5-10 bóng LED quan trọng nhất
- [ ] Vệ sinh máy lạnh, tủ lạnh
- [ ] Lên lịch dùng điện tránh giờ cao điểm

### 🗓️ Tuần 4 (Ngày 22-30): Đánh giá
- [ ] So sánh hóa đơn với tháng trước
- [ ] Điều chỉnh thói quen
- [ ] Lập kế hoạch tiếp theo

---

## 🎯 MỤC TIÊU KỲ VỌNG

Nếu thực hiện đầy đủ:
- **Tiết kiệm:** {total_kwh*0.15:.0f}-{total_kwh*0.25:.0f} kWh/tháng
- **Giảm hóa đơn:** {total_kwh*0.15*2500:,.0f}-{total_kwh*0.25*2500:,.0f}đ/tháng
- **Trong 1 năm:** {total_kwh*0.2*2500*12:,.0f}đ

💪 **Chúc bạn thành công!**
"""
    
    return analysis


def get_quick_tips_by_device(device_name, kwh, percent):
    """
    Lấy tips nhanh cho từng loại thiết bị
    """
    tips = {
        "Máy lạnh": [
            f"🌡️ Đặt 26-27°C thay vì <25°C → Tiết kiệm 10-15%",
            f"🧹 Vệ sinh lưới lọc mỗi 2 tuần → Tăng hiệu suất 5%",
            f"🚪 Đóng cửa kín phòng → Giảm thất thoát nhiệt",
            f"⏰ Bật chế độ hẹn giờ để tắt khi ngủ"
        ],
        "Tủ lạnh": [
            f"🌡️ Đặt nhiệt độ 3-4°C (ngăn mát) và -18°C (đông)",
            f"🍲 Không để thức ăn nóng vào tủ",
            f"📏 Để cách tường 10cm để thoát nhiệt",
            f"🔍 Kiểm tra gioăng cao su cửa"
        ],
        "TV": [
            f"💡 Giảm độ sáng màn hình xuống 50-70%",
            f"🔌 Rút phích khi không xem (standby vẫn tốn điện)",
            f"⏱️ Bật chế độ tự tắt sau 30 phút"
        ],
        "Chiếu sáng": [
            f"💡 Thay bóng LED 9W thay vì 60W → Tiết kiệm 85%",
            f"☀️ Tận dụng ánh sáng tự nhiên ban ngày",
            f"🔦 Dùng đèn bàn thay vì đèn trần khi đọc sách",
            f"🤖 Lắp cảm biến tự động cho hành lang"
        ],
        "Khác": [
            f"🔌 Rút phích cắm sạc điện thoại sau khi đầy",
            f"⚡ Dùng ổ cắm thông minh có hẹn giờ",
            f"🌙 Tắt router WiFi khi đi ngủ (nếu không cần)"
        ]
    }
    
    return tips.get(device_name, tips["Khác"])


def calculate_roi_for_upgrades():
    """
    Tính toán ROI cho các nâng cấp thiết bị
    """
    upgrades = [
        {
            "name": "Thay toàn bộ bóng LED",
            "cost": 500000,  # VNĐ
            "monthly_saving": 75000,  # VNĐ
            "payback_months": 6.7,
            "priority": "HIGH"
        },
        {
            "name": "Máy lạnh Inverter mới",
            "cost": 8000000,
            "monthly_saving": 300000,
            "payback_months": 26.7,
            "priority": "MEDIUM"
        },
        {
            "name": "Tủ lạnh Inverter",
            "cost": 7000000,
            "monthly_saving": 150000,
            "payback_months": 46.7,
            "priority": "LOW"
        },
        {
            "name": "Bình nóng lạnh Heat Pump",
            "cost": 10000000,
            "monthly_saving": 400000,
            "payback_months": 25,
            "priority": "MEDIUM"
        }
    ]
    
    return upgrades