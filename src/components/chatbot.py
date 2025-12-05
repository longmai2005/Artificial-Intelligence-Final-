# File: src/components/chatbot.py
import streamlit as st
import time

def get_bot_response(user_input):
    """Logic trả lời thông minh (Rule-based)"""
    user_input = user_input.lower()
    
    if any(x in user_input for x in ["xin chào", "hi", "hello"]):
        return "Chào bạn! Tôi là trợ lý năng lượng ảo. Bạn cần giúp gì về tiết kiệm điện hôm nay?"
    elif "tủ lạnh" in user_input:
        return "Tủ lạnh ngốn khoảng 20% điện gia đình. Mẹo: Đặt nhiệt độ ngăn mát 4-5°C, ngăn đông -18°C. Không để tủ quá trống hoặc quá đầy."
    elif any(x in user_input for x in ["máy lạnh", "điều hòa"]):
        return "Máy lạnh là 'vua' ngốn điện. Mẹo: Bật 26°C kèm quạt. Mỗi độ tăng lên giúp tiết kiệm 3% điện năng."
    elif "máy giặt" in user_input:
        return "Nên giặt nước lạnh và gom đủ quần áo một lần giặt. Tránh giặt vào giờ cao điểm (18h-20h)."
    elif any(x in user_input for x in ["bậc thang", "giá điện"]):
        return "Hệ thống tính tiền theo 6 bậc EVN. Bậc 1 rẻ nhất (1.806đ), Bậc 6 đắt nhất (3.151đ). Hãy cố gắng dùng dưới 200kWh/tháng."
    else:
        return "Tôi chưa hiểu rõ lắm. Bạn hãy thử hỏi về 'tủ lạnh', 'điều hòa' hoặc 'cách tính tiền điện' nhé."

def render_floating_chatbot():
    """Hiển thị Chatbot dạng bong bóng ở góc dưới"""
    
    # CSS để đẩy nút popover xuống góc phải (Floating Action Button style)
    # Lưu ý: st.popover mặc định nằm theo luồng, ta dùng CSS để trang trí thêm nếu cần
    # Ở đây ta dùng st.popover tiêu chuẩn của Streamlit mới nhất
    
    with st.popover("💬 Trợ lý AI", use_container_width=False):
        st.markdown("### 🤖 Hỗ trợ trực tuyến")
        st.caption("Hỏi tôi bất cứ điều gì về cách tiết kiệm điện!")
        
        # 1. Khởi tạo lịch sử chat
        if "messages" not in st.session_state:
            st.session_state.messages = []
            # Câu chào mặc định đầu tiên
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "👋 Xin chào! Tôi có thể giúp bạn tính toán chi phí hoặc gợi ý mẹo tiết kiệm điện cho Tủ lạnh, Máy lạnh..."
            })

        # 2. Container chứa nội dung chat (để scroll được)
        chat_container = st.container(height=300)
        
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        # 3. Khu vực nhập liệu
        if prompt := st.chat_input("Nhập câu hỏi...", key="chat_input_widget"):
            # Hiện câu hỏi user
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.write(prompt)

            # Bot trả lời
            response = get_bot_response(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Đang nhập..."):
                        time.sleep(0.5)
                        st.write(response)
        
        # Nút xóa lịch sử
        if st.button("Làm mới đoạn chat", type="primary"):
            st.session_state.messages = []
            st.rerun()