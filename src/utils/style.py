# File: src/utils/style.py
import streamlit as st

def apply_custom_style():
    st.markdown("""
    <style>
        /* --- 1. GLOBAL THEME (Nền tối hiện đại) --- */
        .stApp {
            background: radial-gradient(circle at 10% 20%, #1a1c29 0%, #0d1117 90%);
            font-family: 'Segoe UI', sans-serif;
        }

        /* --- 2. CUSTOM LOADING SPINNER (Hiệu ứng Loading) --- */
        /* Tạo hiệu ứng vòng xoay gradient xinh xắn */
        .custom-loader {
            border: 5px solid #f3f3f3; /* Màu viền nhạt */
            border-top: 5px solid #00C9FF; /* Màu chính xanh dương */
            border-bottom: 5px solid #92FE9D; /* Màu phụ xanh lá */
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .loading-text {
            text-align: center;
            color: #00C9FF;
            font-weight: bold;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }

        /* --- 3. GLASSMORPHISM CARDS (Thẻ trong suốt) --- */
        .metric-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            border-color: #00C9FF;
            box-shadow: 0 0 15px rgba(0, 201, 255, 0.3);
        }

        /* --- 4. SIDEBAR --- */
        [data-testid="stSidebar"] {
            background-color: #0d1117;
            border-right: 1px solid #2b2f3b;
        }

        /* --- 5. BUTTONS (Nút bấm Neon) --- */
        .stButton>button {
            border-radius: 30px;
            background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
            color: #000;
            font-weight: 700;
            border: none;
            height: 45px;
            box-shadow: 0 4px 15px rgba(0,201,255,0.3);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 25px rgba(0,201,255,0.6);
            color: #000;
        }

        /* --- 6. INPUT FIELDS --- */
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border-radius: 10px !important;
        }

        /* --- 7. TABS --- */
        .stTabs [data-baseweb="tab-list"] button {
            background-color: transparent;
            border-radius: 20px;
            color: #aaa;
        }
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background-color: rgba(0, 201, 255, 0.2);
            color: #00C9FF;
            border: 1px solid #00C9FF;
        }
    </style>
    """, unsafe_allow_html=True)

def card_container(title, value, delta=None):
    """Component vẽ thẻ chỉ số (Metric Card)"""
    delta_html = f"<span style='color: #4CAF50; font-size: 0.8em; margin-left: 5px;'>▲ {delta}</span>" if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; color: #bbb; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">{title}</p>
        <h3 style="margin:5px 0 0 0; color: #fff; font-size: 26px; font-weight: 600;">{value} {delta_html}</h3>
    </div>
    """, unsafe_allow_html=True)

def custom_spinner():
    """Hàm hiển thị loader xoay tròn"""
    placeholder = st.empty()
    placeholder.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 150px;">
            <div class="custom-loader"></div>
            <p class="loading-text">⚡ AI đang phân tích dữ liệu...</p>
        </div>
    """, unsafe_allow_html=True)
    return placeholder