import streamlit as st

def apply_custom_style():
    st.markdown("""
    <style>
        /* Chỉnh font và màu nền tổng thể */
        .stApp {
            background-color: #0E1117;
        }
        
        /* Làm đẹp các Metrics (Các ô số liệu) */
        [data-testid="stMetricValue"] {
            font-size: 24px;
            color: #4CAF50;
        }
        
        /* Card Style cho các khung container */
        .css-1r6slb0, .css-12oz5g7 {
            border-radius: 15px;
            border: 1px solid #303030;
            padding: 20px;
            background-color: #262730;
        }
        
        /* Nút bấm đẹp hơn */
        .stButton>button {
            border-radius: 20px;
            background-image: linear-gradient(to right, #00C6FF 0%, #0072FF  51%, #00C6FF  100%);
            color: white;
            border: none;
            transition: 0.5s;
        }
        .stButton>button:hover {
            background-position: right center;
            transform: scale(1.02);
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #16181D;
            border-right: 1px solid #303030;
        }
    </style>
    """, unsafe_allow_html=True)