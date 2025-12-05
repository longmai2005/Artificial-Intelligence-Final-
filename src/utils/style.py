import streamlit as st

def apply_custom_style():
    st.markdown("""
    <style>
        /* 1. NỀN & FONT CHỮ */
        .stApp {
            background: linear-gradient(to bottom right, #0e1117, #131720);
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }
        
        /* 2. SIDEBAR ĐẸP HƠN */
        [data-testid="stSidebar"] {
            background-color: #11131a;
            border-right: 1px solid #2b2f3b;
        }
        
        /* 3. CARD CONTAINER (Hiệu ứng thẻ bài) */
        div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
            /* Đây là trick để target các container con */
        }
        
        /* Class tùy chỉnh để bọc các khối nội dung */
        .metric-card {
            background-color: #1e212b;
            border: 1px solid #2b2f3b;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            border-color: #4CAF50;
        }

        /* 4. NÚT BẤM GRADIENT */
        .stButton>button {
            border-radius: 25px;
            background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
            color: #000;
            font-weight: bold;
            border: none;
            height: 50px;
            box-shadow: 0 4px 15px rgba(0,201,255,0.4);
        }
        .stButton>button:hover {
            box-shadow: 0 6px 20px rgba(0,201,255,0.6);
            transform: scale(1.02);
        }
        
        /* 5. INPUT FIELDS */
        .stTextInput>div>div>input, .stNumberInput>div>div>input {
            border-radius: 10px;
            background-color: #1e212b;
            border: 1px solid #2b2f3b;
            color: white;
        }
        
        /* 6. TAB STYLE */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #1e212b;
            border-radius: 10px;
            padding: 10px 20px;
            color: white;
        }
        .stTabs [aria-selected="true"] {
            background-color: #4CAF50 !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)

def card_container(title, value, delta=None):
    """Hàm Python để vẽ Card Metric đẹp"""
    delta_html = f"<span style='color: #4CAF50; font-size: 0.8em;'>▲ {delta}</span>" if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <h4 style="margin:0; color: #aaa; font-size: 14px;">{title}</h4>
        <h2 style="margin:0; color: #fff; font-size: 28px;">{value} {delta_html}</h2>
    </div>
    """, unsafe_allow_html=True)