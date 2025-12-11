import streamlit as st

def apply_custom_style():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        :root {
            --bg-dark: #0f172a;
            --primary: #3b82f6;
            --glass: rgba(255, 255, 255, 0.05);
            --border: rgba(255, 255, 255, 0.1);
            --text-main: #ffffff;
            --text-sub: #94a3b8;
        }

        .stApp {
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(at 0% 0%, hsla(253,16%,7%,0.5) 0, transparent 50%), 
                radial-gradient(at 50% 0%, hsla(225,39%,30%,0.5) 0, transparent 50%);
            font-family: 'Inter', sans-serif;
            color: var(--text-main);
        }

        /* --- 1. LOGIN CARD FIX (Quan trọng) --- */
        /* Biến khung container mặc định của Streamlit thành thẻ kính */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }
        
        /* Căn giữa tiêu đề trong Login */
        .login-header {
            text-align: center;
            margin-bottom: 20px;
        }
        .brand-text {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }

        /* --- 2. HOMEPAGE STYLES --- */
        .hero-container {
            text-align: center;
            padding: 60px 20px;
            max-width: 900px;
            margin: 0 auto;
        }
        .hero-title {
            font-size: 4rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 20px;
            background: linear-gradient(to right, #fff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero-desc {
            font-size: 1.2rem;
            color: var(--text-sub);
            max-width: 700px;
            margin: 0 auto 40px;
        }
        
        .feature-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            height: 100%;
            transition: transform 0.3s;
        }
        .feature-card:hover {
            transform: translateY(-5px);
            border-color: var(--primary);
        }
        .feature-icon { font-size: 2.5rem; margin-bottom: 15px; display: block; }
        .feature-title { font-size: 1.2rem; font-weight: 700; margin-bottom: 10px; color: white; }

        /* --- 3. INPUTS & BUTTONS --- */
        .stTextInput input {
            background: rgba(0, 0, 0, 0.2) !important;
            border: 1px solid var(--border) !important;
            color: white !important;
            border-radius: 12px !important;
            padding: 12px 15px !important;
        }
        .stTextInput input:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
        }
        
        .stButton button {
            width: 100%;
            background: linear-gradient(90deg, #3b82f6, #2563eb);
            color: white !important;
            border: none;
            border-radius: 12px;
            height: 48px;
            font-weight: 600;
            transition: 0.3s;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(59, 130, 246, 0.4);
        }

        /* --- 4. METRIC CARD --- */
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
    <div style="text-align: center; margin-bottom: 30px; padding: 25px; background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(168,85,247,0.1)); border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);">
        <h1 style="margin:0; font-size: 2.2rem; color: #60a5fa;">Xin chào, {name}!</h1>
    </div>
    """, unsafe_allow_html=True)

def custom_spinner(): return st.empty()