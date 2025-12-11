import streamlit as st

def apply_custom_style():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        /* 1. MÀU MẶC ĐỊNH (DARK MODE) */
        :root {
            --bg-color: #0f172a;
            --glass-bg: rgba(255, 255, 255, 0.05);
            --border-color: rgba(255, 255, 255, 0.1);
            --text-color: #ffffff;
            --sub-text: #94a3b8;
            --primary: #3b82f6;
        }

        /* 2. MÀU SÁNG (LIGHT MODE) - Tự động nhận diện */
        @media (prefers-color-scheme: light) {
            :root {
                --bg-color: #f8fafc;
                --glass-bg: #ffffff;
                --border-color: #e2e8f0;
                --text-color: #0f172a;
                --sub-text: #64748b;
            }
        }

        /* 3. ÁP DỤNG BIẾN VÀO GIAO DIỆN */
        .stApp {
            background-color: var(--bg-color);
            /* Gradient nhẹ nền */
            background-image: radial-gradient(at 50% 0%, rgba(59, 130, 246, 0.1) 0%, transparent 50%);
            font-family: 'Inter', sans-serif;
            color: var(--text-color);
        }

        /* Container kính mờ (Login card, Admin cards) */
        div[data-testid="stVerticalBlockBorderWrapper"], .metric-card, .login-card {
            background: var(--glass-bg);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        }

        /* Text colors */
        h1, h2, h3, p, span, div, label {
            color: var(--text-color) !important;
        }
        .text-sub { color: var(--sub-text) !important; }

        /* Inputs */
        .stTextInput input {
            background: var(--glass-bg) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-color) !important;
            border-radius: 12px !important;
        }
        .stTextInput input:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
        }

        /* Buttons */
        .stButton button {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white !important; /* Chữ nút luôn trắng */
            border: none;
            border-radius: 12px;
            height: 48px;
            font-weight: 600;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
        }

        /* Dataframe fix color */
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border-color);
            border-radius: 12px;
        }
        
        /* Metric Card Specific */
        .metric-card { padding: 20px; text-align: center; }
        .metric-title { font-size: 0.85rem; color: var(--sub-text) !important; text-transform: uppercase; }
        .metric-value { font-size: 1.8rem; font-weight: 700; color: var(--text-color) !important; margin-top: 5px; }
        
        /* Homepage Specific */
        .hero-container {
            text-align: center; padding: 80px 20px;
            max-width: 900px; margin: 0 auto;
        }
        .hero-title {
            font-size: 3.5rem; font-weight: 800; line-height: 1.1; margin-bottom: 20px;
            background: linear-gradient(to right, #3b82f6, #8b5cf6);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        
    </style>
    """, unsafe_allow_html=True)

def card_container(title, value, delta=None):
    delta_html = f"<span style='color:#10b981; font-size:0.8em; font-weight:bold'>▲ {delta}</span>" if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value} {delta_html}</div>
    </div>
    """, unsafe_allow_html=True)

def render_hero_section(name):
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 30px; padding: 25px; border: 1px solid rgba(59,130,246,0.2); border-radius: 20px; background: rgba(59,130,246,0.05);">
        <h1 style="margin:0; font-size: 2.2rem; color: #3b82f6;">Xin chào, {name}!</h1>
        <p style="margin-top:5px; opacity: 0.8;">Hệ thống quản lý năng lượng thông minh.</p>
    </div>
    """, unsafe_allow_html=True)

def custom_spinner(): return st.empty()