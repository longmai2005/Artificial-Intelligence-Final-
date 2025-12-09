import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from src.backend.history import save_history, load_history
from src.backend.logic_engine import calculate_evn_bill
from src.utils.style import card_container, custom_spinner, render_hero_section

def calculate_personal_forecast(ac_count, fridge_count, member_count, house_type, smart_settings=None):
    if smart_settings is None:
        smart_settings = {"ac": True, "lights": True, "water": True}

    base_load = 1.5
    ac_load = (ac_count * 1.2 * 8) if smart_settings["ac"] else 0
    fridge_load = fridge_count * 1.5 
    member_load = member_count * 0.5 
    lights_load = 0.5 if smart_settings["lights"] else 0.1
    water_load = 2.5 if smart_settings["water"] else 0

    total_daily = base_load + ac_load + fridge_load + member_load + lights_load + water_load
    
    hours = np.arange(24)
    pattern = np.exp(-((hours - 20)**2) / 10) 
    hourly_load = (total_daily / 24) * (0.5 + pattern) 
    hourly_load += np.random.normal(0, 0.05, 24)
    
    return hourly_load, total_daily

def render_user_page(username, name):
    render_hero_section(name)
    
    # CSS Custom cho trang User
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
            background: transparent;
        }
        .stToggle {
            background-color: rgba(255,255,255,0.05);
            padding: 10px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🚀 Smart Control & Dự Báo", "📊 Xếp Hạng Cộng Đồng", "📜 Lịch Sử"])
    
    # --- TAB 1 ---
    with tab1:
        col_main, col_control = st.columns([2, 1], gap="medium")
        
        with col_control:
            st.markdown("### 🎛️ Bảng Điều Khiển")
            with st.container(border=True):
                st.caption("Trạng thái thiết bị:")
                sw_ac = st.toggle("❄️ Máy lạnh", value=True)
                sw_lights = st.toggle("💡 Đèn hệ thống", value=True)
                sw_water = st.toggle("🔥 Bình nóng lạnh", value=True)
                
                st.markdown("---")
                st.caption("Thông số nhà:")
                house_type = st.selectbox("Loại nhà", ["Chung cư", "Nhà phố", "Biệt thự"], label_visibility="collapsed")
                c1, c2 = st.columns(2)
                with c1: ac_count = st.number_input("Máy lạnh", 0, 5, 1)
                with c2: fridge_count = st.number_input("Tủ lạnh", 0, 3, 1)
                member_count = st.slider("Thành viên", 1, 10, 2)
                
                btn_run = st.button("🔄 Cập nhật AI", use_container_width=True)

        with col_main:
            if btn_run:
                with st.spinner("AI đang tính toán..."):
                    time.sleep(0.8)
            
            smart_settings = {"ac": sw_ac, "lights": sw_lights, "water": sw_water}
            hourly_data, total_day = calculate_personal_forecast(
                ac_count, fridge_count, member_count, house_type, smart_settings
            )
            
            monthly_kwh = total_day * 30 
            monthly_bill, breakdown = calculate_evn_bill(monthly_kwh)
            daily_bill = monthly_bill / 30
            
            # Cards
            c1, c2, c3 = st.columns(3)
            with c1: card_container("Tiêu thụ hôm nay", f"{total_day:.1f} kWh")
            with c2: card_container("Tiền điện / ngày", f"{int(daily_bill):,} đ")
            with c3: card_container("Dự báo tháng", f"{int(monthly_bill):,} đ")

            # Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=np.arange(24), y=hourly_data, fill='tozeroy', 
                                   mode='lines', line=dict(color='#00C9FF', width=3), name='Real-time Load'))
            fig.update_layout(
                title="Biểu đồ phụ tải 24h",
                height=350, 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font=dict(color='white'),
                margin=dict(l=0,r=0,t=40,b=0),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            if btn_run:
                save_history(username, f"{house_type} (Smart)", total_day, daily_bill)

    # --- TAB 2 ---
    with tab2:
        st.subheader("🏆 Bảng Xếp Hạng Khu Vực")
        leaderboard = pd.DataFrame({
            "Hạng": ["🥇", "🥈", "🥉", "4", "5"],
            "Người dùng": ["Nguyễn Văn A", "Trần Thị B", name, "Lê Văn C", "Phạm D"],
            "Điểm Xanh": [950, 890, 850, 820, 780],
            "Tiết kiệm": ["-20%", "-15%", "-12%", "-10%", "-8%"]
        })
        st.dataframe(leaderboard, use_container_width=True, hide_index=True)

    # --- TAB 3 ---
    with tab3:
        history = load_history(username)
        if history:
            df_hist = pd.DataFrame(history)
            st.dataframe(
                df_hist.rename(columns={"timestamp": "Thời gian", "cost": "Chi phí (VNĐ)", "kwh": "Tiêu thụ (kWh)"}), 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("Chưa có dữ liệu lịch sử.")