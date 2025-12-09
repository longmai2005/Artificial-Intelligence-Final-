import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from src.backend.history import save_history, load_history
from src.backend.logic_engine import calculate_evn_bill
from src.utils.style import card_container, render_hero_section

def calculate_personal_forecast(ac_count, fridge_count, member_count, house_type, smart_settings=None):
    if smart_settings is None: smart_settings = {"ac": True, "lights": True, "water": True}
    base = 1.5
    ac = (ac_count * 1.2 * 8) if smart_settings["ac"] else 0
    fridge = fridge_count * 1.5 
    mem = member_count * 0.5 
    light = 0.5 if smart_settings["lights"] else 0.1
    water = 2.5 if smart_settings["water"] else 0
    total = base + ac + fridge + mem + light + water
    
    hours = np.arange(24)
    pattern = np.exp(-((hours - 20)**2) / 10) 
    hourly = (total / 24) * (0.5 + pattern) + np.random.normal(0, 0.05, 24)
    return hourly, total

def render_user_page(username, name):
    render_hero_section(name)
    
    tab1, tab2, tab3 = st.tabs(["🚀 Dự Báo & Smart Control", "📊 Xếp Hạng", "📜 Lịch Sử"])
    
    with tab1:
        c_main, c_ctrl = st.columns([2, 1])
        with c_ctrl:
            st.markdown("### 🎛️ Điều Khiển")
            with st.container(border=True):
                ac_on = st.toggle("❄️ Máy lạnh", True)
                li_on = st.toggle("💡 Đèn", True)
                wa_on = st.toggle("🔥 Nước nóng", True)
                st.divider()
                st.caption("Thông số nhà:")
                house = st.selectbox("Loại nhà", ["Chung cư", "Nhà phố", "Biệt thự"])
                ac_num = st.number_input("Số máy lạnh", 0, 5, 1)
                fr_num = st.number_input("Số tủ lạnh", 0, 3, 1)
                mem_num = st.slider("Thành viên", 1, 10, 2)
                btn = st.button("🔄 Cập nhật AI", use_container_width=True)

        with c_main:
            if btn:
                with st.spinner("AI đang tính toán..."): time.sleep(0.5)
            
            settings = {"ac": ac_on, "lights": li_on, "water": wa_on}
            hourly, total = calculate_personal_forecast(ac_num, fr_num, mem_num, house, settings)
            m_kwh = total * 30
            m_bill, _ = calculate_evn_bill(m_kwh)
            
            k1, k2, k3 = st.columns(3)
            with k1: card_container("Tiêu thụ ngày", f"{total:.1f} kWh")
            with k2: card_container("Chi phí ngày", f"{int(m_bill/30):,} đ")
            with k3: card_container("Dự báo tháng", f"{int(m_bill):,} đ")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=np.arange(24), y=hourly, fill='tozeroy', 
                                   mode='lines', line=dict(color='#00C9FF', width=3), name='Load'))
            fig.update_layout(title="Biểu đồ phụ tải 24h", height=300, paper_bgcolor='rgba(0,0,0,0)', 
                              plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=0,r=0,t=40,b=0))
            st.plotly_chart(fig, use_container_width=True)
            
            if btn: save_history(username, f"{house} (Smart)", total, m_bill/30)

    with tab2:
        st.subheader("🏆 Bảng Xếp Hạng")
        df = pd.DataFrame({
            "Hạng": ["🥇", "🥈", "🥉", "4"],
            "User": ["Nguyễn A", "Trần B", name, "Lê C"],
            "Điểm": [950, 890, 850, 800]
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab3:
        hist = load_history(username)
        if hist:
            st.dataframe(pd.DataFrame(hist), use_container_width=True)
        else:
            st.info("Chưa có lịch sử.")