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
            background-image: 
                radial-gradient(at 0% 0%, hsla(253,16%,7%,0.5) 0, transparent 50%), 
                radial-gradient(at 50% 0%, hsla(225,39%,30%,0.5) 0, transparent 50%);
            font-family: 'Inter', sans-serif;
            color: var(--text-main);
        }

        /* LOGIN CARD */
        .login-container {
            background: var(--glass);
            backdrop-filter: blur(24px);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            text-align: center;
            margin-bottom: 20px;
        }
        .brand-text {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }

        /* METRIC CARD */
        .metric-card {
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            border-color: var(--primary);
        }
        .metric-title {
            color: var(--text-sub);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .metric-value {
            color: var(--text-main);
            font-size: 1.5rem;
            font-weight: 700;
            margin-top: 5px;
        }

        /* INPUTS & BUTTONS */
        .stTextInput input {
            border-radius: 10px !important;
            border: 1px solid var(--border) !important;
            background: rgba(255,255,255,0.05) !important;
            color: var(--text-main) !important;
        }
        .stButton button {
            background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
            color: white !important;
            border-radius: 10px;
            font-weight: 600;
            border: none;
            height: 45px;
        }
    </style>
    """, unsafe_allow_html=True)

# --- ĐÂY LÀ HÀM BẠN ĐANG THIẾU ---
def card_container(title, value, delta=None):
    """Hiển thị thẻ chỉ số đẹp"""
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
    <div style="text-align: center; margin-bottom: 30px; padding: 20px; background: rgba(59, 130, 246, 0.1); border-radius: 20px; border: 1px solid rgba(59, 130, 246, 0.2);">
        <h1 style="margin:0; font-size: 2.2rem; color: #60a5fa;">Xin chào, {name}!</h1>
        <p style="color: #94a3b8; margin-top: 5px;">Hệ thống quản lý năng lượng đang hoạt động tối ưu.</p>
    </div>
    """, unsafe_allow_html=True)

def custom_spinner():
    return st.empty()