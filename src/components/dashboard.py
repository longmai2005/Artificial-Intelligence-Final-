import streamlit as st
import plotly.express as px
from src.backend.logic_engine import calculate_cost
from src.utils.helpers import format_currency

def render_dashboard(current_data, current_time):
    st.subheader("📊 Giám sát Thời gian thực")
    
    # 1. Metrics Row
    power = current_data['Global_active_power']
    volt = current_data['Voltage']
    cost = calculate_cost(power, current_time.hour)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Công suất Tổng", f"{power:.3f} kW", delta_color="inverse", delta=f"{power-1.0:.2f}")
    c2.metric("Điện áp", f"{volt:.1f} V")
    c3.metric("Chi phí ước tính/giờ", format_currency(cost))
    
    # 2. Charts Row
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        # Gauge Chart 
        st.info(f"Thời gian hệ thống: **{current_time.strftime('%H:%M - %d/%m/%Y')}**")
        if 17 <= current_time.hour <= 20:
             st.error("⚡ ĐANG LÀ GIỜ CAO ĐIỂM (Giá điện x1.8)")
        else:
             st.success("✅ Giờ bình thường/Thấp điểm")

    with c_right:
        # Pie Chart phân bổ
        sub1 = current_data['Sub_metering_1']
        sub2 = current_data['Sub_metering_2']
        sub3 = current_data['Sub_metering_3']
        df_pie = {"Device": ["Bếp", "Giặt là", "Điều hòa/Nóng lạnh"], "Value": [sub1, sub2, sub3]}
        fig = px.pie(df_pie, values='Value', names='Device', title="Phân bổ thiết bị chính")
        fig.update_layout(height=300, margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig, width='stretch')