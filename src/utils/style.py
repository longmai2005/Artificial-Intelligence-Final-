import streamlit as st

def apply_custom_style():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        :root {
            --bg-dark: #0f172a;
            --primary: #3b82f6;
            --accent: #8b5cf6;
            --glass: rgba(255, 255, 255, 0.05);
            --border: rgba(255, 255, 255, 0.1);
            --text-main: #ffffff;
            --text-sub: #94a3b8;
        }

        /* Light Mode overrides */
        @media (prefers-color-scheme: light) {
            :root {
                --bg-dark: #f8fafc;
                --glass: rgba(255, 255, 255, 0.8);
                --border: rgba(0, 0, 0, 0.1);
                --text-main: #0f172a;
                --text-sub: #64748b;
            }
        }

        .stApp {
            background-color: var(--bg-dark);
            /* Gradient background nhẹ */
            background-image: 
                radial-gradient(at 0% 0%, hsla(253,16%,7%,0.5) 0, transparent 50%), 
                radial-gradient(at 50% 0%, hsla(225,39%,30%,0.5) 0, transparent 50%);
            font-family: 'Inter', sans-serif;
            color: var(--text-main);
        }

        /* --- LOGIN CARD --- */
        .login-container {
            background: var(--glass);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            margin-top: 20px;
            text-align: center;
        }

        .brand-text {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }

        .slogan-text {
            color: var(--text-sub);
            font-size: 0.95rem;
            margin-bottom: 30px;
        }

        /* --- METRIC CARD --- */
        .metric-card {
            background: var(--glass);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            border-color: var(--primary);
        }
        .metric-title {
            color: var(--text-sub);
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }
        .metric-value {
            color: var(--text-main);
            font-size: 1.5rem;
            font-weight: 700;
        }

        /* --- INPUTS --- */
        .stTextInput input {
            background: rgba(15, 23, 42, 0.05) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            color: var(--text-main) !important;
            padding: 10px 15px !important;
        }
        .stTextInput input:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }

        /* --- BUTTONS --- */
        .stButton button {
            background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
            color: white !important;
            border-radius: 12px;
            border: none;
            height: 48px;
            font-weight: 600;
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
            transition: all 0.2s;
        }
        .stButton button:hover {
            opacity: 0.9;
            transform: scale(1.01);
        }
    </style>
    """, unsafe_allow_html=True)

# --- CÁC HÀM COMPONENT CẦN THIẾT ---

def card_container(title, value, delta=None):
    """Hiển thị thẻ chỉ số (Metric)"""
    delta_html = f"<span style='color: #10b981; font-size: 0.8em; font-weight:bold; margin-left: 8px;'>▲ {delta}</span>" if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value} {delta_html}</div>
    </div>
    """, unsafe_allow_html=True)

def render_hero_section(name):
    """Banner chào mừng"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(59,130,246,0.1) 0%, rgba(139,92,246,0.1) 100%); 
        padding: 30px; 
        border-radius: 20px; 
        border: 1px solid rgba(255,255,255,0.1); 
        margin-bottom: 30px; 
        text-align:center;">
        <h1 style="margin:0; font-size: 2.5em; background: linear-gradient(to right, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Xin chào, {name}!
        </h1>
        <p style="color: var(--text-sub); margin-top: 10px;">
            Hệ thống quản lý năng lượng thông minh đang hoạt động ổn định.
        </p>
    </div>
    """, unsafe_allow_html=True)

def custom_spinner():
    """Vòng xoay loading giả lập"""
    return st.empty()