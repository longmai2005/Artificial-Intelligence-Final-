import streamlit as st
import time
from src.backend.ai_engine import ask_gemini  # Import bộ não AI mới

def render_floating_chatbot():
    """Hiển thị Chatbot AI thông minh"""
    
    # CSS tùy chỉnh cho Chatbot đẹp hơn
    st.markdown("""
        <style>
        .stChatInput {
            position: fixed;
            bottom: 20px;
            z-index: 1000;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.popover("💬 Trợ lý AI Pro", use_container_width=False):
        st.markdown("### 🤖 AI Energy Expert")
        st.caption("Sử dụng công nghệ Google Gemini")
        
        # 1. Khởi tạo lịch sử chat
        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Xin chào! Tôi là AI thực thụ. Bạn có thể hỏi tôi bất cứ điều gì về cách tiết kiệm điện, cách chọn điều hòa, hay phân tích hóa đơn..."
            })

        # 2. Container nội dung chat
        chat_container = st.container(height=350)
        
        with chat_container:
            for msg in st.session_state.messages:
                # Phân biệt icon user và bot
                avatar = "👤" if msg["role"] == "user" else "🤖"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.write(msg["content"])

        # 3. Khu vực nhập liệu
        if prompt := st.chat_input("Hỏi tôi bất cứ gì...", key="chat_input_widget"):
            # Hiện câu hỏi user
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user", avatar="👤"):
                    st.write(prompt)

            # --- GỌI AI TRẢ LỜI ---
            with chat_container:
                with st.chat_message("assistant", avatar="🤖"):
                    # Hiệu ứng loading chuyên nghiệp
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    with st.spinner("AI đang suy nghĩ..."):
                        # Gọi hàm từ ai_engine.py
                        ai_reply = ask_gemini(prompt)
                        
                        # Hiệu ứng đánh máy (Typewriter effect)
                        for chunk in ai_reply.split():
                            full_response += chunk + " "
                            time.sleep(0.05)
                            message_placeholder.markdown(full_response + "▌")
                        
                        message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # Nút xóa lịch sử
        if st.button("🗑️ Xóa đoạn chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()