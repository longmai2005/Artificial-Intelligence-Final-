import streamlit as st

def apply_custom_style():
    st.markdown("""
    <style>
        /* --- 1. ADAPTIVE BACKGROUND (Nền linh hoạt) --- */
        /* Mặc định là Dark Mode (giao diện gốc của bạn) */
        :root {
            --bg-gradient: radial-gradient(circle at 10% 20%, #1a1c29 0%, #0d1117 90%);
            --card-bg: rgba(255, 255, 255, 0.05);
            --text-color: #ffffff;
            --input-bg: rgba(255, 255, 255, 0.05);
        }

        /* Khi thiết bị người dùng là Light Mode */
        @media (prefers-color-scheme: light) {
            :root {
                --bg-gradient: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                --card-bg: rgba(255, 255, 255, 0.6);
                --text-color: #333333;
                --input-bg: rgba(0, 0, 0, 0.05);
            }
            /* Ghi đè màu chữ cho Light Mode */
            h1, h2, h3, p, span, div {
                color: var(--text-color);
            }
            .stApp {
                color: #333;
            }
        }

        .stApp {
            background: var(--bg-gradient);
            font-family: 'Segoe UI', sans-serif;
            transition: background 0.5s ease;
        }

        /* --- 2. GLASS CARDS (Thẻ kính) --- */
        .metric-card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            color: var(--text-color);
        }
        
        /* Chỉnh màu chữ tiêu đề trong thẻ */
        .metric-card p {
            color: var(--text-color) !important;
            opacity: 0.8;
        }
        .metric-card h3 {
            color: var(--text-color) !important;
        }

        /* --- 3. INPUT FIELDS --- */
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
            background-color: var(--input-bg) !important;
            color: var(--text-color) !important;
            border: 1px solid rgba(128, 128, 128, 0.2) !important;
        }

        /* --- 4. BUTTONS (Giữ nguyên Gradient vì nó đẹp trên cả 2 nền) --- */
        .stButton>button {
            border-radius: 30px;
            background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
            color: #000 !important; /* Chữ nút luôn đen cho dễ đọc */
            font-weight: 700;
            border: none;
            height: 45px;
            box-shadow: 0 4px 15px rgba(0,201,255,0.3);
        }

        /* --- 5. SIDEBAR --- */
        [data-testid="stSidebar"] {
            background-color: rgba(0,0,0,0.2); /* Bán trong suốt để ăn theo nền chính */
            border-right: 1px solid rgba(255,255,255,0.1);
        }
    </style>
    """, unsafe_allow_html=True)

def card_container(title, value, delta=None):
    delta_html = f"<span style='color: #4CAF50; font-size: 0.8em; margin-left: 5px;'>▲ {delta}</span>" if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">{title}</p>
        <h3 style="margin:5px 0 0 0; font-size: 24px; font-weight: 700;">{value} {delta_html}</h3>
    </div>
    """, unsafe_allow_html=True)

def render_hero_section(name):
    # Banner dùng màu gradient nhẹ, tương thích cả 2 nền
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(0,201,255,0.1) 0%, rgba(146,254,157,0.1) 100%);
        border-radius: 20px; padding: 30px; margin-bottom: 30px; border: 1px solid rgba(255,255,255,0.2); text-align: center;">
        <h1 style="
            background: -webkit-linear-gradient(0deg, #00C9FF, #92FE9D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3em; font-weight: 800; margin: 0;">Xin chào, {name}!</h1>
        <p style="font-size: 1.2em; margin-top: 10px; opacity: 0.8;">Hệ thống đã sẵn sàng tối ưu năng lượng cho bạn.</p>
    </div>
    """, unsafe_allow_html=True)

def custom_spinner():
    placeholder = st.empty()
    placeholder.markdown("""<div style="text-align:center">⏳ Đang xử lý...</div>""", unsafe_allow_html=True)
    return placeholder