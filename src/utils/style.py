import streamlit as st

def apply_custom_style():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        :root {
            --bg-dark: #0f172a;
            --glass: rgba(255, 255, 255, 0.05);
            --border: rgba(255, 255, 255, 0.1);
            --text-main: #ffffff;
            --text-sub: #94a3b8;
            --primary: #3b82f6;
        }

        /* Light Mode */
        @media (prefers-color-scheme: light) {
            :root {
                --bg-dark: #f8fafc;
                --glass: #ffffff;
                --border: #e2e8f0;
                --text-main: #0f172a;
                --text-sub: #64748b;
            }
        }

        .stApp {
            background-color: var(--bg-dark);
            background-image: radial-gradient(at 0% 0%, hsla(253,16%,7%,0.5) 0, transparent 50%), 
                              radial-gradient(at 50% 0%, hsla(225,39%,30%,0.5) 0, transparent 50%);
            font-family: 'Inter', sans-serif;
            color: var(--text-main);
        }

        /* --- LOGIN CARD --- */
        .login-card {
            background: var(--glass);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            text-align: center;
            margin-bottom: 20px;
        }
        
        .brand-text {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #60a5fa 0%, #c084fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }

        /* --- INPUT FIELDS --- */
        .stTextInput input {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid var(--border) !important;
            color: var(--text-main) !important;
            border-radius: 12px !important;
            padding: 10px 15px !important;
        }
        .stTextInput input:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
        }

        /* --- BUTTONS --- */
        .stButton button {
            width: 100%;
            background: linear-gradient(90deg, #3b82f6, #2563eb);
            color: white !important;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            height: 48px;
            transition: 0.3s;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        /* --- METRIC CARDS --- */
        .metric-card {
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
        }
        .metric-title { font-size: 0.85rem; color: var(--text-sub); text-transform: uppercase; letter-spacing: 1px; }
        .metric-value { font-size: 1.8rem; font-weight: 700; color: var(--text-main); margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- CÁC HÀM COMPONENT (Phải có đủ 3 hàm này) ---

def card_container(title, value, delta=None):
    delta_html = f"<span style='color:#4ade80; font-size:0.8em; font-weight:bold'>▲ {delta}</span>" if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value} {delta_html}</div>
    </div>
    """, unsafe_allow_html=True)

def render_hero_section(name):
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(168,85,247,0.1)); padding: 30px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 30px; text-align: center;">
        <h1 style="margin:0; font-size: 2.2rem; color: #60a5fa;">Xin chào, {name}!</h1>
        <p style="margin-top:10px; color:#94a3b8;">Hệ thống quản lý năng lượng thông minh đang hoạt động.</p>
    </div>
    """, unsafe_allow_html=True)

def custom_spinner(): 
    return st.empty()