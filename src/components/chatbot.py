# File: src/components/chatbot.py
import streamlit as st
import time

def get_bot_response(user_input):
    """Logic trả lời thông minh dựa trên từ khóa"""
    user_input = user_input.lower()
    
    if "xin chào" in user_input or "hi" in user_input:
        return "Chào bạn! Tôi là trợ lý năng lượng ảo (AI Energy Bot). Tôi có thể giúp gì cho bạn về cách tiết kiệm điện?"
        
    elif "tủ lạnh" in user_input:
        return "Với tủ lạnh, bạn nên:\n1. Đặt nhiệt độ ngăn mát khoảng 4-5°C, ngăn đông -18°C.\n2. Hạn chế đóng mở cửa quá nhiều.\n3. Để tủ cách tường ít nhất 10cm để tản nhiệt tốt."
        
    elif "máy lạnh" in user_input or "điều hòa" in user_input:
        return "Máy lạnh là thiết bị tốn điện nhất! Mẹo:\n1. Bật 26-27°C kèm quạt gió.\n2. Dùng chế độ 'Sleep' vào ban đêm.\n3. Vệ sinh lưới lọc 3 tháng/lần (giúp tiết kiệm 15% điện)."
        
    elif "máy giặt" in user_input:
        return "Hãy gom đủ quần áo rồi mới giặt một mẻ. Sử dụng nước lạnh thay vì nước nóng nếu không cần thiết. Tránh giặt vào giờ cao điểm (18h-20h)."
        
    elif "bậc thang" in user_input or "giá điện" in user_input:
        return "Hệ thống đang tính tiền theo 6 bậc của EVN. Càng dùng nhiều, đơn giá càng cao. Hãy cố gắng giữ mức tiêu thụ dưới 200kWh/tháng để có giá tốt nhất."
        
    else:
        return "Câu hỏi thú vị! Tuy nhiên tôi chỉ chuyên về tiết kiệm năng lượng. Bạn hãy thử hỏi về 'tủ lạnh', 'máy lạnh' hoặc 'giá điện' xem sao?"

def render_chatbot():
    st.markdown("### 🤖 Trợ lý AI (Hỗ trợ 24/7)")
    
    # Khởi tạo lịch sử chat
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Xin chào! Bạn muốn hỏi về thiết bị nào?"}]

    # Hiển thị lịch sử chat cũ
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Nhập câu hỏi mới
    if prompt := st.chat_input("Nhập câu hỏi của bạn (VD: Làm sao tiết kiệm tủ lạnh?)..."):
        # Hiện câu hỏi người dùng
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Bot suy nghĩ và trả lời
        with st.chat_message("assistant"):
            with st.spinner("AI đang tra cứu dữ liệu..."):
                time.sleep(1) # Giả vờ suy nghĩ cho giống thật
                response = get_bot_response(prompt)
                st.write(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})