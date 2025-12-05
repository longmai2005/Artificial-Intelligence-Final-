# File: src/components/admin_page.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.backend.data_loader import load_dataset
from src.backend.predictor import EnergyPredictor
from src.components.dashboard import render_dashboard
from src.utils.style import card_container

def render_admin_page():
    st.markdown("## 🛠️ Trung tâm Kiểm soát Hệ thống (Admin Center)")
    st.markdown("---")
    
    # PHẦN 1: GIẢI THÍCH MỤC ĐÍCH (Để admin hiểu trang này làm gì)
    with st.expander("ℹ️ Hướng dẫn trang Quản trị (Bấm để xem)", expanded=True):
        st.info("""
        **Chào mừng Quản trị viên! Đây là nơi bạn giám sát "Sức khỏe" của toàn hệ thống:**
        1.  **Simulator Control:** Điều chỉnh dữ liệu giả lập đầu vào (thời gian, tải trọng) để test độ nhạy của AI.
        2.  **Model Monitor:** Theo dõi xem mô hình AI có dự báo chính xác không (So sánh đường Dự báo vs Thực tế).
        3.  **System Health:** Giám sát các thông số kỹ thuật (CPU giả lập, trạng thái server).
        """)

    # PHẦN 2: KPI METRICS (Chỉ số quan trọng)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        card_container("Trạng thái Server", "🟢 Online", "Stable")
    with col2:
        card_container("Tổng User", "12", "+2 hôm nay")
    with col3:
        card_container("Độ chính xác AI", "94.5%", "RMSE: 0.21")
    with col4:
        card_container("Tải hệ thống", "Low", "CPU: 12%")

    st.markdown("---")

    # PHẦN 3: BẢNG ĐIỀU KHIỂN & BIỂU ĐỒ
    # Dùng Tabs để chia nhỏ nội dung cho đỡ rối
    tab_sim, tab_model, tab_users = st.tabs(["🎛️ Điều khiển Giả lập", "🧠 Giám sát Model AI", "👥 Quản lý User"])

    # --- TAB 1: SIMULATOR ---
    with tab_sim:
        col_control, col_view = st.columns([1, 3])
        
        with col_control:
            st.markdown("### ⚙️ Cấu hình")
            st.caption("Chỉnh thời gian để 'tua' dữ liệu nhanh/chậm.")
            
            # Load Data (Logic cũ nhưng gom gọn lại)
            DATA_PATH = "data/household_power_consumption.txt"
            df = load_dataset(DATA_PATH, nrows=20000)
            
            selected_date = st.date_input("Ngày mô phỏng:", df.index.min())
            selected_hour = st.slider("Giờ trong ngày:", 0, 23, 19)
            
            if st.button("🔄 Cập nhật tham số"):
                st.toast("Đã cập nhật cấu hình giả lập!")

        with col_view:
            st.markdown("### 📡 Luồng dữ liệu thời gian thực (Live Stream)")
            try:
                current_ts = pd.Timestamp(f"{selected_date} {selected_hour}:00:00")
                idx = df.index.get_indexer([current_ts], method='nearest')[0]
                current_time = df.index[idx]
                current_data = df.iloc[idx]
                
                # Gọi lại Dashboard component cũ nhưng hiển thị gọn
                render_dashboard(current_data, current_time)
            except Exception as e:
                st.error(f"Lỗi Simulator: {e}")

    # --- TAB 2: MODEL MONITOR ---
    with tab_model:
        st.markdown("### 📉 So sánh Thực tế vs Dự báo (Model Performance)")
        st.caption("Đường màu cam (AI) phải bám sát đường màu xanh (Thực tế) thì model mới tốt.")
        
        # Logic vẽ biểu đồ AI
        predictor = EnergyPredictor()
        past_24h = df.loc[current_time - pd.Timedelta(hours=24):current_time]
        input_data = past_24h['Global_active_power'].values
        forecast_vals = predictor.predict_next_24h(input_data)
        future_time = [current_time + pd.Timedelta(hours=i) for i in range(1, 25)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=past_24h.index, y=past_24h['Global_active_power'], name="Thực tế (Past)", line=dict(color='#00C9FF')))
        fig.add_trace(go.Scatter(x=future_time, y=forecast_vals, name="AI Dự báo (Future)", line=dict(color='#FFA500', dash='dash')))
        fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        st.plotly_chart(fig, use_container_width=True)

    # --- TAB 3: USER MANAGEMENT ---
    with tab_users:
        st.warning("🔒 Khu vực nhạy cảm. Chỉ Admin mới thấy.")
        st.dataframe(pd.DataFrame({
            "Username": ["admin", "longmai", "guest1"],
            "Role": ["Admin", "User", "User"],
            "Last Login": ["Just now", "2 hours ago", "Yesterday"],
            "Status": ["Active", "Active", "Inactive"]
        }), use_container_width=True)