import streamlit as st

def apply_custom_style():
    st.markdown("""
    <style>
        /* =================================================================================
           1. HỆ THỐNG MÀU SẮC ĐỘNG (ADAPTIVE THEME)
           Tự động thay đổi theo giao diện Sáng/Tối của thiết bị người dùng
           ================================================================================= */
        :root {
            /* Mặc định là Dark Mode (Giao diện tối) */
            --bg-gradient: radial-gradient(circle at 10% 20%, #1a1c29 0%, #0d1117 90%);
            --card-bg: rgba(255, 255, 255, 0.05);
            --text-color: #ffffff;
            --sub-text-color: #bbbbbb;
            --input-bg: rgba(255, 255, 255, 0.05);
            --border-color: rgba(255, 255, 255, 0.1);
            --primary-gradient: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
            --shadow-color: rgba(0, 0, 0, 0.2);
        }

        /* Khi thiết bị người dùng đang bật Light Mode (Giao diện sáng) */
        @media (prefers-color-scheme: light) {
            :root {
                --bg-gradient: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                --card-bg: rgba(255, 255, 255, 0.65); /* Kính mờ sáng hơn */
                --text-color: #1a1a1a;
                --sub-text-color: #555555;
                --input-bg: rgba(255, 255, 255, 0.8);
                --border-color: rgba(0, 0, 0, 0.08);
                --shadow-color: rgba(0, 0, 0, 0.05);
            }
            /* Điều chỉnh màu chữ riêng cho Light mode để dễ đọc hơn */
            h1, h2, h3, h4, strong { color: #000 !important; }
            p, span, div, label { color: var(--text-color) !important; }
            .stApp { color: var(--text-color); }
        }

        /* Áp dụng nền tảng */
        .stApp {
            background: var(--bg-gradient);
            transition: background 0.5s ease; /* Hiệu ứng chuyển màu mượt mà */
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }

        /* =================================================================================
           2. RESPONSIVE LAYOUT (TƯƠNG THÍCH ĐA THIẾT BỊ)
           ================================================================================= */
        
        /* Mặc định cho PC (Desktop) */
        .metric-card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 30px var(--shadow-color);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            height: 100%; /* Đảm bảo các thẻ bằng nhau */
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            border-color: #00C9FF;
            box-shadow: 0 10px 40px rgba(0, 201, 255, 0.2);
        }

        .hero-container {
            background: linear-gradient(135deg, rgba(0,201,255,0.1) 0%, rgba(146,254,157,0.1) 100%);
            border-radius: 24px;
            padding: 40px;
            margin-bottom: 30px;
            border: 1px solid var(--border-color);
            text-align: center;
        }

        /* --- TỐI ƯU CHO ĐIỆN THOẠI (Mobile - Màn hình < 768px) --- */
        @media only screen and (max-width: 768px) {
            /* Giảm kích thước banner */
            .hero-container {
                padding: 20px;
                border-radius: 16px;
                margin-bottom: 20px;
            }
            .hero-title {
                font-size: 2em !important; /* Chữ nhỏ lại */
            }
            
            /* Thẻ chỉ số (Metric Card) gọn hơn */
            .metric-card {
                padding: 15px;
                margin-bottom: 10px;
            }
            .metric-card h3 {
                font-size: 20px !important;
            }
            
            /* Nút bấm to hơn để dễ chạm ngón tay */
            .stButton>button {
                height: 50px !important;
                font-size: 16px !important;
            }
            
            /* Ẩn bớt padding thừa của Streamlit */
            .block-container {
                padding-top: 2rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
        }

        /* =================================================================================
           3. UI COMPONENTS (Thành phần giao diện đẹp)
           ================================================================================= */
        
        /* Input Fields (Ô nhập liệu) */
        .stTextInput>div>div>input, 
        .stNumberInput>div>div>input, 
        .stSelectbox>div>div>div {
            background-color: var(--input-bg) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            height: 45px; /* Cao hơn để dễ bấm */
        }
        
        /* Hiệu ứng Focus khi nhập liệu */
        .stTextInput>div>div>input:focus {
            border-color: #00C9FF !important;
            box-shadow: 0 0 0 2px rgba(0, 201, 255, 0.2) !important;
        }

        /* Buttons (Nút bấm Neon Gradient) */
        .stButton>button {
            border-radius: 30px;
            background: var(--primary-gradient);
            color: #000 !important;
            font-weight: 700;
            border: none;
            height: 48px;
            width: 100%;
            box-shadow: 0 4px 15px rgba(0,201,255,0.3);
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            transform: scale(1.02);
            box-shadow: 0 6px 25px rgba(0,201,255,0.5);
            opacity: 0.9;
        }
        .stButton>button:active {
            transform: scale(0.98);
        }

        /* Tabs (Thanh chuyển tab) */
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--card-bg);
            padding: 8px;
            border-radius: 30px;
            border: 1px solid var(--border-color);
            gap: 10px;
            display: flex;
            flex-wrap: wrap; /* Tự xuống dòng trên mobile */
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 20px;
            border: none;
            color: var(--sub-text-color);
            padding: 8px 20px;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #00C9FF !important;
            color: #fff !important;
            box-shadow: 0 4px 10px rgba(0,201,255,0.3);
        }

        /* Custom Loader (Vòng xoay) */
        .custom-loader {
            border: 4px solid rgba(128, 128, 128, 0.2);
            border-left-color: #00C9FF;
            border-radius: 50%;
            width: 45px;
            height: 45px;
            animation: spin 0.8s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin { 100% { transform: rotate(360deg); } }

    </style>
    """, unsafe_allow_html=True)

# --- CÁC HÀM UI HELPERS (Giữ nguyên logic, chỉ cập nhật style) ---

def card_container(title, value, delta=None):
    """Hiển thị thẻ chỉ số (Metric Card)"""
    delta_html = f"<span style='color: #4CAF50; font-size: 0.9em; font-weight:bold; margin-left: 8px;'>▲ {delta}</span>" if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: var(--sub-text-color);">{title}</p>
        <h3 style="margin:8px 0 0 0; font-size: 28px; font-weight: 700; color: var(--text-color);">{value} {delta_html}</h3>
    </div>
    """, unsafe_allow_html=True)

def render_hero_section(name):
    """Hiển thị Banner chào mừng"""
    st.markdown(f"""
    <div class="hero-container">
        <h1 class="hero-title" style="
            background: -webkit-linear-gradient(0deg, #00C9FF, #92FE9D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3em; font-weight: 800; margin: 0; line-height: 1.2;">Xin chào, {name}!</h1>
        <p style="font-size: 1.1em; margin-top: 15px; opacity: 0.9; color: var(--text-color);">
            Hệ thống quản lý năng lượng thông minh 4.0
        </p>
    </div>
    """, unsafe_allow_html=True)

def custom_spinner():
    """Hiển thị vòng xoay loading đẹp"""
    placeholder = st.empty()
    placeholder.markdown("""
        <div style="text-align: center; padding: 30px;">
            <div class="custom-loader"></div>
            <p style="color: #00C9FF; margin-top: 15px; font-weight: 500; letter-spacing: 0.5px;">
                🤖 AI đang phân tích dữ liệu...
            </p>
        </div>
    """, unsafe_allow_html=True)
    return placeholder