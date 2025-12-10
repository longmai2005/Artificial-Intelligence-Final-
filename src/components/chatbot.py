import streamlit as st
import time

try:
    from src.backend.ai_engine import ask_gemini
except ImportError:
    def ask_gemini(p): return "Chế độ Demo (Chưa có API Key): " + p

def render_floating_chatbot():
    st.markdown("""
    <style>
        div[data-testid="stPopover"] { position: fixed; bottom: 30px; right: 30px; z-index: 9999; }
        div[data-testid="stPopover"] > button {
            width: 60px; height: 60px; border-radius: 50%;
            background: linear-gradient(135deg, #6366f1, #a855f7);
            color: white; border: none; box-shadow: 0 4px 14px rgba(0,0,0,0.25);
            font-size: 24px;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.popover("💬", use_container_width=False):
        st.markdown("### 🤖 Trợ lý AI")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [{"role": "assistant", "content": "Xin chào!"}]

        container = st.container(height=350)
        with container:
            for msg in st.session_state.chat_history:
                st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input("Nhập câu hỏi..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            container.chat_message("user").write(prompt)
            with container.chat_message("assistant"):
                with st.spinner("..."):
                    reply = ask_gemini(prompt)
                    st.write(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})