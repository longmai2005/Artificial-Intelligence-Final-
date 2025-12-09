import streamlit as st

def apply_custom_style():
    st.markdown("""
    <style>
        /* --- 1. ADAPTIVE BACKGROUND --- */
        :root {
            --bg-gradient: radial-gradient(circle at 10% 20%, #1a1c29 0%, #0d1117 90%);
            --card-bg: rgba(255, 255, 255, 0.05);
            --text-color: #ffffff;
            --input-bg: rgba(255, 255, 255, 0.05);
            --border-color: rgba(255, 255, 255, 0.1);
        }

        @media (prefers-color-scheme: light) {
            :root {
                --bg-gradient: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                --card-bg: rgba(255, 255, 255, 0.6);
                --text-color: #333333;
                --input-bg: rgba(255, 255, 255, 0.5);
                --border-color: rgba(0, 0, 0, 0.1);
            }
        }

        .stApp {
            background: var(--bg-gradient);
            color: var(--text-color);
            transition: all 0.5s ease;
        }

        /* --- 2. INPUT FIELDS & BUTTONS --- */
        .stTextInput>div>div>input {
            background-color: var(--input-bg) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
        }
        
        .stButton>button {
            border-radius: 30px;
            background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
            color: #000 !important;
            font-weight: 700;
            border: none;
            height: 45px;
            box-shadow: 0 4px 15px rgba(0,201,255,0.3);
        }

        /* --- 3. CUSTOM LOADER --- */
        .custom-loader {
            border: 4px solid rgba(128, 128, 128, 0.2);
            border-left-color: #00C9FF;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin { 100% { transform: rotate(360deg); } }

        /* --- 4. GLASS CARDS --- */
        .metric-card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            border-color: #00C9FF;
        }
        
        /* Chỉnh màu chữ trong thẻ */
        .metric-card p { color: var(--text-color) !important; opacity: 0.8; }
        .metric-card h3 { color: var(--text-color) !important; }

        /* --- 5. HERO BANNER --- */
        .hero-container {
            background: linear-gradient(135deg, rgba(0,201,255,0.1) 0%, rgba(146,254,157,0.1) 100%);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid var(--border-color);
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

# --- CÁC HÀM COMPONENT (Đây là phần bạn đang thiếu) ---

def card_container(title, value, delta=None):
    """Hiển thị thẻ chỉ số đẹp mắt"""
    delta_html = f"<span style='color: #4CAF50; font-size: 0.8em; margin-left: 5px;'>▲ {delta}</span>" if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">{title}</p>
        <h3 style="margin:5px 0 0 0; font-size: 24px; font-weight: 700;">{value} {delta_html}</h3>
    </div>
    """, unsafe_allow_html=True)

def render_hero_section(name):
    """Hiển thị Banner chào mừng"""
    st.markdown(f"""
    <div class="hero-container">
        <h1 style="
            background: -webkit-linear-gradient(0deg, #00C9FF, #92FE9D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3em; font-weight: 800; margin: 0;">Xin chào, {name}!</h1>
        <p style="font-size: 1.2em; margin-top: 10px; opacity: 0.8; color: var(--text-color);">
            Hệ thống đã sẵn sàng tối ưu năng lượng cho bạn.
        </p>
    </div>
    """, unsafe_allow_html=True)

def custom_spinner():
    """Hiển thị vòng xoay loading"""
    placeholder = st.empty()
    placeholder.markdown("""
        <div style="text-align: center; padding: 20px;">
            <div class="custom-loader"></div>
            <p style="color: #00C9FF; margin-top: 10px;">🤖 AI đang tính toán...</p>
        </div>
    """, unsafe_allow_html=True)
    return placeholder