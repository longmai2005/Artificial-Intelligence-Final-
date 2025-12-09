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

        /* Light Mode */
        @media (prefers-color-scheme: light) {
            :root {
                --bg-dark: #f0f2f5;
                --glass: #ffffff;
                --border: #e5e7eb;
                --text-main: #111827;
                --text-sub: #6b7280;
            }
        }

        .stApp {
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(at 0% 0%, hsla(253,16%,7%,0.5) 0, transparent 50%), 
                radial-gradient(at 50% 0%, hsla(225,39%,30%,0.5) 0, transparent 50%);
            font-family: 'Inter', sans-serif;
            color: var(--text-main);
        }

        /* --- LOGIN CARD (Căn giữa đẹp) --- */
        .login-card {
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 40px 30px;
            box-shadow: 0 10px 40px -10px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 400px;
            margin: 0 auto; /* Căn giữa */
        }
        
        .brand-text {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }

        .slogan-text {
            color: var(--text-sub);
            font-size: 0.9rem;
            margin-bottom: 30px;
        }

        /* --- INPUTS --- */
        .stTextInput input {
            background: var(--glass) !important;
            border: 1px solid var(--border) !important;
            color: var(--text-main) !important;
            border-radius: 12px !important;
            padding: 12px !important;
        }
        .stTextInput input:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }

        /* --- BUTTONS --- */
        .stButton button {
            width: 100%;
            border-radius: 12px;
            height: 48px;
            font-weight: 600;
            border: none;
            background: linear-gradient(90deg, #3b82f6, #2563eb);
            color: white !important;
            transition: all 0.2s;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
        }
        
        /* Secondary Button (Nút phụ nhỏ hơn) */
        .secondary-btn button {
            background: transparent !important;
            border: 1px solid var(--border) !important;
            color: var(--text-sub) !important;
            height: 35px !important;
            font-size: 0.8rem !important;
        }
        .secondary-btn button:hover {
            border-color: var(--primary) !important;
            color: var(--primary) !important;
        }

        /* --- METRIC CARD --- */
        .metric-card {
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
        }
        .metric-title { font-size: 0.8rem; color: var(--text-sub); text-transform: uppercase; letter-spacing: 1px; }
        .metric-value { font-size: 1.6rem; font-weight: 700; color: var(--text-main); margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- CÁC HÀM COMPONENT (Đã bổ sung đầy đủ để không bị lỗi Import) ---

def card_container(title, value, delta=None):
    """Hiển thị thẻ chỉ số"""
    delta_html = f"<span style='color: #10b981; font-size: 0.8em; margin-left: 5px;'>▲ {delta}</span>" if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value} {delta_html}</div>
    </div>
    """, unsafe_allow_html=True)

def render_hero_section(name):
    """Banner chào mừng"""
    st.markdown(f"""
    <div style="text-align:center; margin-bottom: 30px; padding: 30px; background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.1)); border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);">
        <h1 style="margin:0; font-size: 2.2rem; color: #60a5fa;">Xin chào, {name}!</h1>
        <p style="color: #94a3b8; margin-top: 5px;">Hệ thống năng lượng thông minh đang hoạt động.</p>
    </div>
    """, unsafe_allow_html=True)

def custom_spinner():
    return st.empty()