import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from src.backend.history import save_history, load_history
from src.backend.logic_engine import calculate_evn_bill
from src.utils.style import card_container, render_hero_section

def calculate_forecast(ac, fridge, mem, house, settings):
    base = 2.0
    ac_load = (ac * 1.2 * 8) if settings['ac'] else 0
    total = base + ac_load + (fridge * 1.5) + (mem * 0.5)
    if settings['lights']: total += 0.5
    if settings['water']: total += 2.5
    
    hours = np.arange(24)
    hourly = (total / 24) * (0.5 + np.exp(-((hours - 20)**2) / 10))
    return hourly, total

def render_user_page(username, name):
    render_hero_section(name)
    
    tab1, tab2, tab3 = st.tabs(["🚀 Bảng Điều Khiển", "📊 Xếp Hạng", "📜 Lịch Sử"])
    
    with tab1:
        c1, c2 = st.columns([2, 1])
        with c2:
            st.markdown("### 🎛️ Thiết Bị")
            with st.container(border=True):
                s_ac = st.toggle("Máy lạnh", True)
                s_li = st.toggle("Đèn", True)
                s_wa = st.toggle("Nước nóng", True)
                st.divider()
                st.caption("Thông số nhà")
                house = st.selectbox("Loại nhà", ["Chung cư", "Nhà phố"])
                ac_n = st.number_input("Số AC", 0, 5, 1)
                fr_n = st.number_input("Số Tủ lạnh", 0, 3, 1)
                mem = st.slider("Người", 1, 10, 2)
                
                if st.button("🔄 Chạy AI", type="primary", use_container_width=True):
                    with st.spinner("Đang tính toán..."): time.sleep(0.5)
                    hourly, total = calculate_forecast(ac_n, fr_n, mem, house, {'ac': s_ac, 'lights': s_li, 'water': s_wa})
                    bill, _ = calculate_evn_bill(total * 30)
                    
                    st.session_state['last_calc'] = {'h': hourly, 't': total, 'b': bill}
                    save_history(username, f"{house}", total, bill/30)

        with c1:
            if 'last_calc' in st.session_state:
                res = st.session_state['last_calc']
                k1, k2, k3 = st.columns(3)
                with k1: card_container("Tiêu thụ", f"{res['t']:.1f} kWh")
                with k2: card_container("Ngày", f"{int(res['b']/30):,} đ")
                with k3: card_container("Tháng", f"{int(res['b']):,} đ")
                
                fig = go.Figure(go.Scatter(y=res['h'], fill='tozeroy', line=dict(color='#00C9FF')))
                fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("👈 Hãy nhập thông tin và bấm 'Chạy AI' để xem dự báo.")

    with tab2:
        hist = load_history(username)
        if hist: st.dataframe(pd.DataFrame(hist), use_container_width=True)
        else: st.warning("Chưa có dữ liệu.")