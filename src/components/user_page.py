# File: src/components/user_page.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from src.backend.history import save_history, load_history
from src.backend.logic_engine import calculate_evn_bill
from src.utils.style import card_container, custom_spinner

def calculate_personal_forecast(ac_count, fridge_count, member_count, house_type):
    # Logic giả lập (giữ nguyên)
    base_load = 2.0
    ac_load = ac_count * 1.2 * 8 
    fridge_load = fridge_count * 1.5 
    member_load = member_count * 0.5 
    total_daily = base_load + ac_load + fridge_load + member_load
    
    hours = np.arange(24)
    pattern = np.exp(-((hours - 20)**2) / 10) 
    hourly_load = (total_daily / 24) * (0.5 + pattern) 
    hourly_load += np.random.normal(0, 0.05, 24)
    return hourly_load, total_daily

def render_user_page(username, name):
    st.markdown(f"## 👋 Xin chào, **{name}**")
    
    tab1, tab2, tab3 = st.tabs(["🚀 Dự Báo & Ngân Sách", "📊 So Sánh Cộng Đồng", "📜 Lịch Sử"])
    
    # --- TAB 1: DỰ BÁO ---
    with tab1:
        col_input, col_result = st.columns([1.2, 2], gap="large")
        
        with col_input:
            st.markdown("### 🏠 Cấu hình Nhà")
            with st.container(border=True):
                house_type = st.selectbox("Loại nhà:", ["Chung cư", "Nhà phố", "Biệt thự"])
                area = st.slider("Diện tích (m2):", 20, 200, 60)
                member_count = st.number_input("Thành viên:", 1, 10, 2)
                st.markdown("---")
                ac_count = st.number_input("Số máy lạnh:", 0, 5, 1)
                fridge_count = st.number_input("Số tủ lạnh:", 0, 3, 1)
                
                # FEATURE MỚI: NGÂN SÁCH
                st.markdown("---")
                budget = st.number_input("🎯 Ngân sách điện/tháng (VNĐ):", 
                                        min_value=200000, value=1000000, step=100000)
                
                analyze_btn = st.button("✨ Phân Tích Ngay", use_container_width=True)

        with col_result:
            if analyze_btn:
                # 1. HIỆN LOADER XINH XẮN (Thay thế spinner mặc định)
                loader = custom_spinner()
                time.sleep(1.5) # Giả vờ đợi AI tính toán
                loader.empty() # Xóa loader sau khi xong

                # 2. Tính toán
                hourly_data, total_day = calculate_personal_forecast(ac_count, fridge_count, member_count, house_type)
                monthly_kwh = total_day * 30 
                monthly_bill, breakdown = calculate_evn_bill(monthly_kwh)
                daily_bill = monthly_bill / 30
                
                # Lưu lịch sử
                input_data = f"{house_type}, {ac_count} AC"
                save_history(username, input_data, total_day, daily_bill)

                # 3. Hiển thị Card (Glassmorphism)
                c1, c2, c3 = st.columns(3)
                with c1: card_container("Tiêu thụ ngày", f"{total_day:.1f} kWh")
                with c2: card_container("Tiền điện/ngày", f"{int(daily_bill):,} đ")
                with c3: card_container("Dự báo tháng", f"{int(monthly_bill):,} đ")
                
                # 4. FEATURE MỚI: THANH TIẾN ĐỘ NGÂN SÁCH (Budget Tracker)
                st.markdown("### 💸 Quản lý Ngân sách")
                percent_used = (monthly_bill / budget)
                
                if percent_used > 1.0:
                    bar_color = "red"
                    msg = f"⚠️ CẢNH BÁO: Bạn dự kiến vượt ngân sách **{int(monthly_bill - budget):,} đ**!"
                elif percent_used > 0.8:
                    bar_color = "orange"
                    msg = "⚠️ Chú ý: Bạn sắp chạm trần ngân sách."
                else:
                    bar_color = "green"
                    msg = "✅ Tuyệt vời: Bạn đang chi tiêu trong tầm kiểm soát."
                
                st.progress(min(percent_used, 1.0))
                st.caption(f"{msg} ({int(monthly_bill):,} / {int(budget):,} VNĐ)")

                # 5. Biểu đồ
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=np.arange(24), y=hourly_data, fill='tozeroy', mode='lines', 
                                         line=dict(color='#00C9FF', width=3), name='Tiêu thụ'))
                fig.update_layout(height=250, margin=dict(l=0,r=0,t=10,b=0), 
                                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                  font=dict(color='white'))
                st.plotly_chart(fig, use_container_width=True)

                # 6. FEATURE MỚI: XUẤT BÁO CÁO (Download Button)
                report_text = f"""BÁO CÁO TIÊU THỤ ĐIỆN NĂNG
--------------------------------
Khách hàng: {name}
Loại nhà: {house_type}
Ngày xuất: {pd.Timestamp.now().strftime('%d/%m/%Y')}
--------------------------------
Dự báo tiêu thụ ngày: {total_day:.2f} kWh
Dự báo hóa đơn tháng: {int(monthly_bill):,} VNĐ
Trạng thái ngân sách: {'Vượt mức' if percent_used > 1 else 'An toàn'}
--------------------------------
Cảm ơn bạn đã sử dụng Smart Energy Saver!
"""
                st.download_button(
                    label="📥 Tải Báo Cáo Chi Tiết (.txt)",
                    data=report_text,
                    file_name=f"Energy_Report_{username}.txt",
                    mime="text/plain"
                )

            else:
                st.info("👈 Nhập thông tin bên trái để bắt đầu.")

    # --- TAB 2: SO SÁNH ---
    with tab2:
        st.subheader("🏆 Xếp hạng Tiết kiệm")
        history = load_history(username)
        my_kwh = history[0]['kwh'] if history else 15.5
        
        # Vẽ lại biểu đồ cho đẹp hơn
        neighbor_data = [my_kwh * 0.7, my_kwh, my_kwh * 1.1]
        fig_bench = go.Figure(data=[go.Bar(
            x=['Hàng xóm Tiết kiệm', 'BẠN', 'Hàng xóm Trung bình'],
            y=neighbor_data,
            marker_color=['#92FE9D', '#00C9FF', '#6c757d'], # Màu neon
            text=[f"{x:.1f}" for x in neighbor_data],
            textposition='auto'
        )])
        fig_bench.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'), height=350
        )
        st.plotly_chart(fig_bench, use_container_width=True)

    # --- TAB 3: LỊCH SỬ ---
    with tab3:
        history = load_history(username)
        if history:
            df_hist = pd.DataFrame(history)
            st.dataframe(df_hist.rename(columns={"timestamp": "Thời gian", "cost": "Chi phí"}), 
                         use_container_width=True, hide_index=True)
        else:
            st.write("Chưa có dữ liệu.")