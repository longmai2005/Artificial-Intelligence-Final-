import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def calculate_personal_forecast(ac_count, fridge_count, member_count, house_type):
    """
    Thuật toán đơn giản hóa để giả lập AI dự báo cho cá nhân
    dựa trên thiết bị họ nhập vào.
    """
    # Hệ số cơ bản (kWh/ngày)
    base_load = 2.0  # Đèn, quạt cơ bản
    ac_load = ac_count * 1.2 * 8 # Giả sử chạy 8h/ngày, 1.2kW
    fridge_load = fridge_count * 1.5 # Tủ lạnh chạy 24h
    member_load = member_count * 0.5 # Laptop, sạc đt...
    
    total_daily = base_load + ac_load + fridge_load + member_load
    
    # Tạo biểu đồ giả lập 24h dạng hình sin (cao điểm tối)
    hours = np.arange(24)
    # Đỉnh lúc 20h
    pattern = np.exp(-((hours - 20)**2) / 10) 
    
    hourly_load = (total_daily / 24) * (0.5 + pattern) 
    # Thêm nhiễu cho tự nhiên
    hourly_load += np.random.normal(0, 0.05, 24)
    
    return hourly_load, total_daily

def render_user_page(username, name):
    st.markdown(f"## 👋 Xin chào, {name}!")
    st.markdown("Hãy nhập thông tin ngôi nhà của bạn để AI tính toán phương án tiết kiệm.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info("🏠 **Thông tin Căn hộ**")
        with st.form("user_input_form"):
            house_type = st.selectbox("Loại nhà:", ["Chung cư", "Nhà phố", "Biệt thự"])
            area = st.slider("Diện tích (m2):", 20, 200, 60)
            member_count = st.number_input("Số thành viên:", 1, 10, 2)
            st.markdown("---")
            st.write("🔌 **Thiết bị chính**")
            ac_count = st.number_input("Số máy lạnh:", 0, 5, 1)
            fridge_count = st.number_input("Số tủ lạnh:", 0, 3, 1)
            ev_car = st.checkbox("Có sạc xe điện tại nhà?")
            
            submitted = st.form_submit_button("🚀 Chạy Dự Báo AI")
    
    with col2:
        if submitted:
            # Gọi hàm tính toán
            hourly_data, total_day = calculate_personal_forecast(ac_count, fridge_count, member_count, house_type)
            
            # Nếu có xe điện, tăng tải ban đêm
            if ev_car:
                hourly_data[22:] += 2.0 # Sạc đêm
                total_day += 4.0
            
            st.success(f"✅ Đã phân tích xong! Dự báo tiêu thụ ngày mai: **{total_day:.2f} kWh**")
            
            # Vẽ biểu đồ
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=np.arange(24), y=hourly_data, fill='tozeroy', 
                                     mode='lines', name='Dự báo Tiêu thụ', line=dict(color='#00CC96')))
            fig.update_layout(title="Biểu đồ Tiêu thụ Điện Cá nhân hóa (24h tới)", 
                              xaxis_title="Giờ trong ngày", yaxis_title="Công suất (kW)",
                              height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Thẻ khuyên dùng
            cost_est = total_day * 2500 # Giá điện TB
            st.warning(f"💰 Chi phí dự kiến: **{int(cost_est):,} VNĐ/ngày**")
            
            if ac_count > 1:
                st.info("💡 **Gợi ý:** Bạn có nhiều máy lạnh. Hãy bật chế độ Eco và hẹn giờ tắt lúc 4h sáng để tiết kiệm 15%.")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 50px; background-color: #262730; border-radius: 10px;">
                <h3>🤖 AI đang chờ dữ liệu...</h3>
                <p>Vui lòng nhập thông tin bên trái và bấm nút 'Chạy Dự Báo'.</p>
            </div>
            """, unsafe_allow_html=True)