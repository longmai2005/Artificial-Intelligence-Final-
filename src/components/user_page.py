import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from src.backend.history import save_history, load_history
from src.backend.logic_engine import calculate_evn_bill
from src.utils.style import card_container, render_hero_section

def calculate_forecast(ac, fridge, mem, house, settings):
    base = 1.5
    total = base + (ac * 1.2 * 8 if settings['ac'] else 0) + (fridge * 1.5) + (mem * 0.5)
    if settings['lights']: total += 0.5
    if settings['water']: total += 2.5
    hours = np.arange(24)
    hourly = (total / 24) * (0.5 + np.exp(-((hours - 20)**2) / 10)) + np.random.normal(0, 0.05, 24)
    return hourly, total

def render_user_page(username, name):
    render_hero_section(name)
    tab1, tab2, tab3 = st.tabs(["🚀 Điều Khiển", "📊 Xếp Hạng", "📜 Lịch Sử"])
    
    with tab1:
        c1, c2 = st.columns([2, 1])
        with c2:
            st.markdown("### 🎛️ Thiết Bị")
            with st.container(border=True):
                s_ac = st.toggle("❄️ Máy lạnh", True)
                s_li = st.toggle("💡 Đèn", True)
                s_wa = st.toggle("🔥 Nước nóng", True)
                st.divider()
                st.caption("Thông số nhà")
                house = st.selectbox("Loại nhà", ["Chung cư", "Nhà phố", "Biệt thự"])
                ac_n = st.number_input("Số AC", 0, 5, 1)
                fr_n = st.number_input("Số Tủ lạnh", 0, 3, 1)
                mem = st.slider("Người", 1, 10, 2)
                if st.button("🔄 Chạy Dự Báo", type="primary", use_container_width=True):
                    with st.spinner("AI Computing..."): time.sleep(0.5)
                    hourly, total = calculate_forecast(ac_n, fr_n, mem, house, {'ac': s_ac, 'lights': s_li, 'water': s_wa})
                    bill, _ = calculate_evn_bill(total * 30)
                    st.session_state['res'] = {'h': hourly, 't': total, 'b': bill}
                    save_history(username, f"{house}", total, bill/30)

        with c1:
            if 'res' in st.session_state:
                r = st.session_state['res']
                k1, k2, k3 = st.columns(3)
                with k1: card_container("Tiêu thụ ngày", f"{r['t']:.1f} kWh")
                with k2: card_container("Chi phí ngày", f"{int(r['b']/30):,} đ")
                with k3: card_container("Dự báo tháng", f"{int(r['b']):,} đ")
                fig = go.Figure(go.Scatter(x=np.arange(24), y=r['h'], fill='tozeroy', line=dict(color='#3b82f6')))
                fig.update_layout(title="Biểu đồ tải 24h", height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=30,b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("👈 Nhập thông tin và bấm Chạy Dự Báo.")

    with tab2:
        st.dataframe(pd.DataFrame([["🥇", "User A", 950], ["🥈", "User B", 890], ["🥉", name, 850]], columns=["Rank", "User", "Score"]), use_container_width=True)

    with tab3:
        hist = load_history(username)
        if hist: st.dataframe(pd.DataFrame(hist), use_container_width=True)
        else: st.info("Chưa có lịch sử.")