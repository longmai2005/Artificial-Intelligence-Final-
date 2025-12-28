import streamlit as st
import time
from src.backend.ai_engine import ask_gemini

def render_floating_chatbot():
    """
    Hiển thị Chatbot bong bóng (Floating Bubble) chuẩn UI.
    Đã sửa lỗi Scroll (thanh cuộn).
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
            min-width: 60px !important;
            border-radius: 50% !important;
            
            background: linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%) !important;
            border: none !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
            
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

        div[data-testid="stPopover"] > button:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 0 25px rgba(0, 201, 255, 0.8) !important;
        }

        /* 3. Khung chat khi mở ra (ĐÃ SỬA LỖI SCROLL Ở ĐÂY) */
        div[data-testid="stPopoverBody"] {
            width: 380px !important;
            max-width: 90vw !important;
            height: 500px !important;
            max-height: 80vh !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            background-color: #111827 !important;
            padding: 0 !important;
            
            /* QUAN TRỌNG: Cho phép cuộn dọc, ẩn cuộn ngang */
            overflow-y: auto !important; 
            overflow-x: hidden !important;
            
            display: flex !important;
            flex-direction: column !important;
        }

        /* 4. Tùy chỉnh thanh cuộn (Scrollbar) cho đẹp */
        div[data-testid="stPopoverBody"]::-webkit-scrollbar {
            width: 8px;
        }
        div[data-testid="stPopoverBody"]::-webkit-scrollbar-track {
            background: #111827; 
        }
        div[data-testid="stPopoverBody"]::-webkit-scrollbar-thumb {
            background: #374151; 
            border-radius: 4px;
        }
        div[data-testid="stPopoverBody"]::-webkit-scrollbar-thumb:hover {
            background: #4b5563; 
        }
        
        /* 5. Tinh chỉnh tin nhắn */
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
        
        .stChatMessage .st-emotion-cache-1p1m4ay { display: none !important; }

        /* Đẩy input box xuống dưới cùng */
        .stChatInput {
            padding-bottom: 10px !important;
        }

    </style>
    """, unsafe_allow_html=True)

    # --- LOGIC CHATBOT ---
    
    with st.popover("💬"):
        # Header cố định (Dùng sticky để khi cuộn nó vẫn dính ở trên cùng)
        st.markdown("""
            <div style="
                position: sticky; top: 0; z-index: 100;
                background: linear-gradient(90deg, #3b82f6, #06b6d4); 
                padding: 15px; text-align: center; 
                margin: 0 0 10px 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            ">
                <h4 style="margin:0; color: white; font-size: 16px;">🤖 AI Energy Expert</h4>
            </div>
        """, unsafe_allow_html=True)

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {"role": "assistant", "content": "👋 Xin chào! Tôi là trợ lý tiết kiệm điện của bạn. Bạn cần giúp gì không?"}
            ]

        # Hiển thị lịch sử chat
        for msg in st.session_state.chat_history:
            avt = "🧑‍💻" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avt):
                st.markdown(msg["content"])

        # Input box
        if prompt := st.chat_input("Nhập câu hỏi...", key="float_chat_input"):
            
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)
            
            with st.chat_message("assistant", avatar="🤖"):
                message_placeholder = st.empty()
                message_placeholder.markdown("*(Đang suy nghĩ...)*")
                
                try:
                    response = ask_gemini(prompt)
                    
                    full_res = ""
                    for chunk in response.split():
                        full_res += chunk + " "
                        time.sleep(0.02)
                        message_placeholder.markdown(full_res + "▌")
                    message_placeholder.markdown(response)
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.rerun()
                    
                except Exception as e:
                    message_placeholder.error(f"Lỗi: {str(e)}")

        # Nút xóa lịch sử (cách một khoảng để không dính sát input)
        st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Xóa hội thoại", use_container_width=True):
            st.session_state.chat_history = [
                {"role": "assistant", "content": "👋 Lịch sử đã xóa. Tôi có thể giúp gì thêm?"}
            ]
            st.rerun()