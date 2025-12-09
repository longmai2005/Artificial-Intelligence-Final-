import streamlit as st
import time
# Nếu chưa có file ai_engine thì dùng hàm giả lập bên dưới
# from src.backend.ai_engine import ask_gemini 

# --- HÀM GIẢ LẬP AI (Dùng cái này nếu chưa gắn API Key) ---
def ask_gemini(prompt):
    time.sleep(1)
    if "tủ lạnh" in prompt.lower(): return "Tủ lạnh tiêu thụ khoảng 20% điện năng gia đình. Hãy đặt nhiệt độ ngăn mát 4-5°C nhé!"
    return "Tôi là AI Energy Expert. Tôi có thể giúp bạn tối ưu hóa hóa đơn tiền điện."
# -----------------------------------------------------------

def render_floating_chatbot():
    # Nút Popover ở góc phải (CSS đã xử lý vị trí)
    # Icon là 💬
    with st.popover("💬", use_container_width=False):
        
        # Header Chatbot đẹp
        st.markdown("""
            <div style="padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 15px;">
                <h3 style="margin: 0; color: #00C9FF; display: flex; align-items: center; gap: 10px;">
                    🤖 AI Energy Expert
                </h3>
                <p style="margin: 0; font-size: 0.8em; color: #94a3b8;">Hỗ trợ trực tuyến 24/7</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Init Chat History
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "👋 Xin chào! Bạn muốn hỏi về thiết bị nào?"}]

        # Container chat (Chiều cao cố định để scroll)
        chat_container = st.container(height=350)
        
        with chat_container:
            for msg in st.session_state.messages:
                # Chọn Avatar
                if msg["role"] == "assistant":
                    st.chat_message("assistant", avatar="🤖").write(msg["content"])
                else:
                    st.chat_message("user", avatar="🧑‍💻").write(msg["content"])

        # Input Area
        # Lưu ý: st.chat_input trong popover cần key unique để không lỗi
        prompt = st.chat_input("Nhập câu hỏi...", key="float_chat_input")
        
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                st.chat_message("user", avatar="🧑‍💻").write(prompt)
                
                with st.chat_message("assistant", avatar="🤖"):
                    # Placeholder cho hiệu ứng typing
                    text_placeholder = st.empty()
                    text_placeholder.markdown("typing...")
                    
                    # Gọi AI
                    response = ask_gemini(prompt)
                    
                    # Hiệu ứng đánh máy
                    full_text = ""
                    for chunk in response.split():
                        full_text += chunk + " "
                        time.sleep(0.05)
                        text_placeholder.markdown(full_text + "▌")
                    text_placeholder.markdown(full_text)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun() # Rerun để cập nhật UI ngay lập tức

        # Footer Tools
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🗑️", help="Xóa lịch sử chat"):
                st.session_state.messages = []
                st.rerun()