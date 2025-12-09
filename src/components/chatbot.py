import streamlit as st
import time
# Nếu chưa có file ai_engine thì dùng hàm giả lập bên dưới, nếu có rồi thì uncomment dòng sau:
from src.backend.ai_engine import ask_gemini 

def render_floating_chatbot():
    # CSS để tùy chỉnh Chatbot đẹp hơn
    st.markdown("""
    <style>
        .stPopover {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 9999;
        }
        .stChatInputContainer {
            padding-bottom: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.popover("💬 Trợ lý AI", use_container_width=False):
        st.markdown("### 🤖 Energy Expert AI")
        st.caption("Hỏi tôi về cách tiết kiệm điện, phân tích hóa đơn...")
        
        # Init Chat History
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Xin chào! Tôi có thể giúp gì cho bạn?"}]

        # Container chat (Scrollable)
        chat_container = st.container(height=400)
        
        with chat_container:
            for msg in st.session_state.messages:
                avatar = "🤖" if msg["role"] == "assistant" else "👤"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.write(msg["content"])

        # Input Area
        if prompt := st.chat_input("Nhập câu hỏi...", key="bot_input"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user", avatar="👤"):
                    st.write(prompt)
                
                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("Đang suy nghĩ..."):
                        # --- GỌI AI ---
                        try:
                            response = ask_gemini(prompt) # Gọi từ ai_engine.py
                        except:
                            time.sleep(1)
                            response = "Tôi đang gặp chút sự cố kết nối AI. Bạn hãy thử lại sau nhé!"
                        
                        # Hiệu ứng đánh máy
                        text_placeholder = st.empty()
                        full_text = ""
                        for chunk in response.split():
                            full_text += chunk + " "
                            time.sleep(0.05)
                            text_placeholder.markdown(full_text + "▌")
                        text_placeholder.markdown(full_text)
            
            st.session_state.messages.append({"role": "assistant", "content": response})