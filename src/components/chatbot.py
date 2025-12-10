import streamlit as st
import time

try:
    from src.backend.ai_engine import ask_gemini
except ImportError:
    def ask_gemini(p): return "Chế độ Demo (Chưa có API Key): " + p

def render_floating_chatbot():
    """
    Hiển thị Chatbot bong bóng (Floating Bubble)
    Đã fix lỗi hiển thị thành thanh ngang dài.
    """
    
    # --- CSS CƯỠNG CHẾ GIAO DIỆN NÚT TRÒN ---
    st.markdown("""
    <style>
        /* 1. Container bao ngoài nút Popover */
        div[data-testid="stPopover"] {
            position: fixed !important;
            bottom: 30px !important;
            right: 30px !important;
            z-index: 99999 !important;
            width: auto !important; /* Quan trọng: Co lại vừa nút bấm */
            height: auto !important;
            background-color: transparent !important;
            border: none !important;
        }

        /* 2. Nút bấm chính (Hình tròn) */
        div[data-testid="stPopover"] > button {
            width: 60px !important;
            height: 60px !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%) !important;
            border: none !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: transform 0.2s ease !important;
        }

        /* Icon bên trong nút */
        div[data-testid="stPopover"] > button span {
            font-size: 30px !important;
            color: white !important;
        }

        /* Hiệu ứng khi di chuột */
        div[data-testid="stPopover"] > button:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 0 25px rgba(0, 201, 255, 0.7) !important;
        }

        /* 3. Khung chat khi mở ra */
        div[data-testid="stPopoverBody"] {
            width: 380px !important;
            max-width: 90vw !important;
            height: 500px !important;
            max-height: 80vh !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            background-color: #111827 !important; /* Nền tối */
            box-shadow: 0 10px 40px rgba(0,0,0,0.5) !important;
            padding: 0 !important;
            overflow: hidden !important;
        }

        /* 4. Tinh chỉnh tin nhắn bên trong */
        .stChatMessage { background-color: transparent !important; }
        
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
    with st.popover("💬", use_container_width=False):
        
        # Header xanh đẹp
        st.markdown("""
            <div style="background: linear-gradient(90deg, #3b82f6, #06b6d4); padding: 15px; text-align: center;">
                <h3 style="margin:0; color: white; font-size: 1.2rem;">🤖 AI Energy Expert</h3>
                <p style="margin:0; font-size: 0.8rem; color: rgba(255,255,255,0.9);">Hỗ trợ tiết kiệm điện 24/7</p>
            </div>
        """, unsafe_allow_html=True)

        # Lịch sử chat
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [{"role": "assistant", "content": "👋 Xin chào! Tôi có thể giúp gì cho bạn?"}]

        # Container chat
        chat_container = st.container(height=360)
        with chat_container:
            for msg in st.session_state.chat_history:
                # Avatar text thay vì ảnh
                avt = "🧑‍💻" if msg["role"] == "user" else "🤖"
                with st.chat_message(msg["role"], avatar=avt):
                    st.write(msg["content"])

        # Input
        if prompt := st.chat_input("Nhập câu hỏi...", key="float_chat_input"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with chat_container:
                st.chat_message("user", avatar="🧑‍💻").write(prompt)
                
                with st.chat_message("assistant", avatar="🤖"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown("typing...") 
                    
                    try:
                        full_response = ask_gemini(prompt)
                    except Exception:
                        full_response = "Lỗi kết nối AI. Vui lòng thử lại."
                    
                    # Hiệu ứng gõ chữ
                    display_text = ""
                    for chunk in full_response.split():
                        display_text += chunk + " "
                        time.sleep(0.05)
                        message_placeholder.markdown(display_text + "▌")
                    message_placeholder.markdown(full_response)
            
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})
            st.rerun()

        # Nút xóa
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("🗑️", help="Xóa lịch sử"):
                st.session_state.chat_history = []
                st.rerun()