import streamlit as st
import time
from src.backend.ai_engine import ask_gemini

def render_floating_chatbot():
    """
    Hiển thị Chatbot bong bóng (Floating Bubble) chuẩn UI.
    """

    st.markdown("""
    <style>
        /* 1. Container bao ngoài nút Popover */
        div[data-testid="stPopover"] {
            position: fixed !important;
            bottom: 30px !important;
            right: 30px !important;
            z-index: 99999 !important;
            
            width: auto !important;
            height: auto !important;
            min-width: 0 !important;
            
            background-color: transparent !important;
            border: none !important;
        }

        /* 2. Nút bấm chính (Hình tròn) */
        div[data-testid="stPopover"] > button {
            width: 60px !important;
            height: 60px !important;
            min-width: 60px !important; /* Đảm bảo tròn */
            border-radius: 50% !important;
            
            background: linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%) !important;
            border: none !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
            
            /* Căn giữa icon */
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            
            transition: transform 0.2s ease !important;
        }

        /* Icon trong nút */
        div[data-testid="stPopover"] > button span {
            font-size: 30px !important;
            color: white !important;
        }

        /* Hiệu ứng di chuột */
        div[data-testid="stPopover"] > button:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 0 25px rgba(0, 201, 255, 0.8) !important;
        }

        /* 3. Khung chat khi mở ra */
        div[data-testid="stPopoverBody"] {
            width: 380px !important;
            max-width: 90vw !important;
            height: 500px !important;
            max-height: 80vh !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            background-color: #111827 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }
        
        /* 4. Tinh chỉnh tin nhắn */
        .stChatMessage { background: transparent !important; }
        
        /* Tin nhắn User (Phải) */
        div[data-testid="stChatMessage"]:nth-child(odd) {
            flex-direction: row-reverse !important;
        }
        div[data-testid="stChatMessage"]:nth-child(odd) div[data-testid="stMarkdownContainer"] {
            background-color: #3b82f6 !important;
            color: white !important;
            padding: 10px 15px !important;
            border-radius: 15px 15px 0 15px !important;
        }

        /* Tin nhắn Bot (Trái) */
        div[data-testid="stChatMessage"]:nth-child(even) div[data-testid="stMarkdownContainer"] {
            background-color: #1f2937 !important;
            color: #e5e7eb !important;
            padding: 10px 15px !important;
            border-radius: 15px 15px 15px 0 !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
        }
        
        /* Ẩn avatar mặc định */
        .stChatMessage .st-emotion-cache-1p1m4ay { display: none !important; }

    </style>
    """, unsafe_allow_html=True)

    # --- LOGIC CHATBOT ---
    
    # Nút Popover với icon chat
    with st.popover("💬"):
        st.markdown("""
            <div style="background: linear-gradient(90deg, #3b82f6, #06b6d4); padding: 10px; text-align: center; border-radius: 10px 10px 0 0; margin: -16px -16px 10px -16px;">
                <h4 style="margin:0; color: white;">🤖 AI Energy Expert</h4>
            </div>
        """, unsafe_allow_html=True)

        # 1. Khởi tạo lịch sử chat nếu chưa có
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {"role": "assistant", "content": "👋 Xin chào! Tôi là trợ lý tiết kiệm điện của bạn. Bạn cần giúp gì không?"}
            ]

        # 2. Hiển thị lịch sử chat từ session_state
        # Sử dụng container để tin nhắn cũ luôn hiển thị
        for msg in st.session_state.chat_history:
            avt = "🧑‍💻" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avt):
                st.markdown(msg["content"])

        # 3. Xử lý Input từ người dùng
        if prompt := st.chat_input("Nhập câu hỏi...", key="float_chat_input"):
            
            # CHỈ THÊM VÀO LỊCH SỬ 1 LẦN DUY NHẤT
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Hiển thị ngay tin nhắn của user lên giao diện
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)
            
            # 4. TỰ ĐỘNG GỌI AI VÀ TRẢ LỜI
            with st.chat_message("assistant", avatar="🤖"):
                message_placeholder = st.empty()
                message_placeholder.markdown("*(Đang suy nghĩ...)*")
                
                try:
                    # Gọi hàm Gemini mới từ ai_engine.py
                    response = ask_gemini(prompt)
                    
                    # Hiệu ứng gõ chữ
                    full_res = ""
                    for chunk in response.split():
                        full_res += chunk + " "
                        time.sleep(0.02)
                        message_placeholder.markdown(full_res + "▌")
                    message_placeholder.markdown(response)
                    
                    # Lưu câu trả lời của AI vào lịch sử
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
                    # Rerun để đồng bộ toàn bộ khung chat
                    st.rerun()
                    
                except Exception as e:
                    message_placeholder.error(f"Lỗi: {str(e)}")

        # Nút xóa lịch sử
        if st.button("🗑️ Xóa hội thoại", width='stretch'):
            st.session_state.chat_history = [
                {"role": "assistant", "content": "👋 Lịch sử đã xóa. Tôi có thể giúp gì thêm?"}
            ]
            st.rerun()