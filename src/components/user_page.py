# File: src/components/user_page.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.backend.history import save_history, load_history
from src.backend.logic_engine import calculate_evn_bill
from src.utils.style import card_container

def calculate_personal_forecast(ac_count, fridge_count, member_count, house_type):
    # Logic giả lập AI dự báo
    base_load = 2.0
    ac_load = ac_count * 1.2 * 8 # Giả sử chạy 8h
    fridge_load = fridge_count * 1.5 
    member_load = member_count * 0.5 
    
    total_daily = base_load + ac_load + fridge_load + member_load
    
    # Tạo biểu đồ hình sin
    hours = np.arange(24)
    pattern = np.exp(-((hours - 20)**2) / 10) 
    hourly_load = (total_daily / 24) * (0.5 + pattern) 
    hourly_load += np.random.normal(0, 0.05, 24)
    
    return hourly_load, total_daily

def render_user_page(username, name):
    st.markdown(f"## 👋 Xin chào, **{name}**")
    
    tab1, tab2, tab3 = st.tabs(["🚀 Dự Báo & Tính Tiền", "📊 So Sánh Hàng Xóm", "📜 Lịch Sử"])
    
    # --- TAB 1: DỰ BÁO ---
    with tab1:
        col_input, col_result = st.columns([1, 2], gap="large")
        
        with col_input:
            st.markdown("### 🏠 Nhập thông tin")
            with st.container(border=True):
                house_type = st.selectbox("Loại nhà:", ["Chung cư", "Nhà phố", "Biệt thự"])
                area = st.slider("Diện tích (m2):", 20, 200, 60)
                member_count = st.number_input("Thành viên:", 1, 10, 2)
                st.markdown("---")
                ac_count = st.number_input("Số máy lạnh:", 0, 5, 1)
                fridge_count = st.number_input("Số tủ lạnh:", 0, 3, 1)
                submitted = st.button("✨ Phân Tích Ngay", use_container_width=True)

        with col_result:
            if submitted:
                # 1. Tính toán kWh
                hourly_data, total_day = calculate_personal_forecast(ac_count, fridge_count, member_count, house_type)
                
                # 2. TÍNH TIỀN THEO BẬC THANG EVN (Tính cho 30 ngày để ra bậc chuẩn)
                monthly_kwh = total_day * 30 
                monthly_bill, breakdown = calculate_evn_bill(monthly_kwh)
                daily_bill = monthly_bill / 30
                
                # Lưu lịch sử
                input_data = f"{house_type}, {ac_count} AC"
                save_history(username, input_data, total_day, daily_bill)

                # 3. Hiển thị Card
                c1, c2, c3 = st.columns(3)
                with c1: card_container("Tiêu thụ ngày", f"{total_day:.1f} kWh")
                with c2: card_container("Tiền điện/ngày", f"{int(daily_bill):,} đ")
                with c3: card_container("Dự báo tháng", f"{int(monthly_bill):,} đ")
                
                # 4. Hiển thị chi tiết bậc thang (Dropdown)
                with st.expander("📄 Xem chi tiết cách tính tiền (Bậc thang EVN)"):
                    st.write(f"Tổng tiêu thụ tháng dự kiến: **{monthly_kwh:.1f} kWh**")
                    for line in breakdown:
                        st.text(line)
                    st.caption("*Đã bao gồm thuế GTGT giả định trong đơn giá")

                # 5. Biểu đồ 24h
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=np.arange(24), y=hourly_data, fill='tozeroy', mode='lines', line=dict(color='#00C9FF', width=3), name='Tiêu thụ'))
                fig.update_layout(height=250, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), xaxis_title="Giờ trong ngày", yaxis_title="kW")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("👈 Nhập thông tin để xem tiền điện dự báo.")

    # --- TAB 2: SO SÁNH HÀNG XÓM (Social Benchmarking) ---
    with tab2:
        st.subheader("🏆 Bạn đang ở đâu so với hàng xóm?")
        
        # Lấy dữ liệu gần nhất từ history, nếu không có thì lấy random
        history = load_history(username)
        my_kwh = history[0]['kwh'] if history else 15.5
        
        neighbor_efficient = my_kwh * 0.7 # Hàng xóm tiết kiệm
        neighbor_avg = my_kwh * 1.1        # Hàng xóm trung bình
        
        # Vẽ biểu đồ cột so sánh
        fig_bench = go.Figure()
        
        fig_bench.add_trace(go.Bar(
            x=['Hàng xóm Tiết kiệm', 'BẠN', 'Hàng xóm Trung bình'],
            y=[neighbor_efficient, my_kwh, neighbor_avg],
            marker_color=['#4CAF50', '#FF9800', '#9E9E9E'],
            text=[f"{neighbor_efficient:.1f}", f"{my_kwh:.1f}", f"{neighbor_avg:.1f}"],
            textposition='auto'
        ))
        
        fig_bench.update_layout(
            title="So sánh mức tiêu thụ điện (kWh/ngày)",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            yaxis=dict(showgrid=True, gridcolor='#333'),
            height=400
        )
        st.plotly_chart(fig_bench, use_container_width=True)
        
        if my_kwh < neighbor_avg:
            st.success(f"🎉 Tuyệt vời! Bạn đang dùng ít điện hơn mức trung bình của khu vực ({neighbor_avg:.1f} kWh).")
        else:
            st.warning(f"⚠️ Chú ý: Bạn đang dùng nhiều hơn mức trung bình. Hãy kiểm tra lại các thiết bị làm mát.")

    # --- TAB 3: LỊCH SỬ ---
    with tab3:
        history = load_history(username)
        if history:
            df_hist = pd.DataFrame(history)
            
            # Đổi tên cột hiển thị
            df_hist = df_hist.rename(columns={
                "timestamp": "Thời gian",
                "inputs": "Thiết bị",
                "kwh": "Tiêu thụ (kWh)",
                "cost": "Chi phí (VNĐ)"
            })
            
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.write("Chưa có dữ liệu.")