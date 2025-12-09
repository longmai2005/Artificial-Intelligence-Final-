import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import time
from src.backend.data_loader import load_dataset
from src.backend.predictor import EnergyPredictor
from src.backend.auth import load_users, USER_DB_PATH
from src.utils.style import card_container, custom_spinner

def delete_user(username_to_delete):
    """Hàm xóa user khỏi database"""
    users = load_users()
    if username_to_delete in users:
        # Không cho phép xóa admin gốc
        if users[username_to_delete]['role'] == 'admin':
            return False, "Không thể xóa tài khoản Admin gốc!"
        
        del users[username_to_delete]
        with open(USER_DB_PATH, "w") as f:
            json.dump(users, f)
        return True, "Đã xóa thành công!"
    return False, "User không tồn tại."

def render_admin_page():
    # --- HEADER ---
    st.markdown("## 🛡️ Trung Tâm Quản Trị Hệ Thống (Admin Hub)")
    st.markdown("---")

    # --- 1. LOGIC: LẤY DỮ LIỆU USER THỰC TẾ ---
    users_db = load_users()
    total_users = len(users_db)
    # Lọc ra số lượng user thường (trừ admin)
    regular_users = len([u for u in users_db.values() if u['role'] == 'user'])
    
    # --- 2. KPI CARDS (Dữ liệu thật) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        card_container("Tổng Tài khoản", f"{total_users}", "All Roles")
    with col2:
        card_container("Khách hàng (User)", f"{regular_users}", "Active")
    with col3:
        # Giả lập trạng thái server
        card_container("Server Status", "Online", "Latency: 24ms")
    with col4:
        card_container("AI Model", "v1.2.0", "Accuracy: 94%")

    st.markdown("---")

    # --- 3. TABS CHỨC NĂNG CHÍNH ---
    tab_overview, tab_users, tab_system = st.tabs(["📊 Phân Tích Dữ Liệu", "👥 Quản Lý Người Dùng", "⚙️ Cấu Hình Hệ Thống"])

    # === TAB 1: PHÂN TÍCH (ANALYTICS) ===
    with tab_overview:
        st.subheader("🔥 Bản đồ nhiệt: Mật độ tiêu thụ năng lượng")
        st.caption("Biểu đồ thể hiện giờ cao điểm tiêu thụ của toàn bộ hệ thống user.")
        
        # Giả lập Heatmap đẹp mắt
        days = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'CN']
        hours = [f"{i}h" for i in range(24)]
        # Tạo dữ liệu giả lập có logic (Cao điểm tối)
        z_data = np.random.rand(7, 24) * 5
        z_data[:, 18:22] += 5 # Tăng nhiệt vào giờ tối
        
        fig = go.Figure(data=go.Heatmap(
            z=z_data, x=hours, y=days,
            colorscale='Magma', showscale=True
        ))
        fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          font=dict(color='white'), margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 📉 Phân bố Loại nhà")
            # Fake data thống kê
            df_house = pd.DataFrame({'Type': ['Chung cư', 'Nhà phố', 'Biệt thự'], 'Count': [45, 30, 15]})
            fig_pie = px.pie(df_house, values='Count', names='Type', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=300)
            st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            st.markdown("#### ⚡ Tải đỉnh dự báo (7 ngày tới)")
            fig_line = go.Figure(go.Scatter(y=np.random.randint(100, 200, 7), mode='lines+markers', line=dict(color='#00C9FF', width=3)))
            fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                   font=dict(color='white'), height=300, xaxis_title="Ngày tới")
            st.plotly_chart(fig_line, use_container_width=True)

    # === TAB 2: QUẢN LÝ USER (USER MANAGEMENT) ===
    with tab_users:
        st.subheader("Danh sách người dùng đăng ký")
        
        # Chuyển đổi dữ liệu JSON sang DataFrame
        user_list = []
        for username, data in users_db.items():
            user_list.append({
                "Username": username,
                "Họ và Tên": data.get("name", "N/A"),
                "Email": data.get("email", "N/A"),
                "Vai trò": "👑 Admin" if data.get("role") == "admin" else "👤 User",
                "Trạng thái": "🟢 Active"
            })
        
        df_users = pd.DataFrame(user_list)
        
        # Hiển thị bảng đẹp
        st.dataframe(
            df_users,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Vai trò": st.column_config.TextColumn(
                    "Vai trò",
                    help="Quyền hạn trong hệ thống",
                    width="medium",
                ),
            }
        )
        
        # Nút tải xuống
        st.download_button(
            label="📥 Xuất danh sách Excel (.csv)",
            data=df_users.to_csv(index=False).encode('utf-8'),
            file_name='ds_nguoi_dung.csv',
            mime='text/csv',
        )
        
        st.subheader("Danh sách người dùng")
        
        st.markdown("### 🗑️ Xóa Người Dùng")
        with st.expander("Mở công cụ xóa"):
            col_del, col_btn = st.columns([3, 1])
            with col_del:
                user_to_del = st.selectbox("Chọn user để xóa:", 
                                         [u for u in users_db.keys() if u != 'admin'])
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Xóa vĩnh viễn ❌", type="primary"):
                    success, msg = delete_user(user_to_del)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # === TAB 3: CẤU HÌNH HỆ THỐNG (SYSTEM CONFIG) ===
    with tab_system:
        st.markdown("### 🎛️ Control Center & Simulation")
        st.info("Khu vực dành cho Nhà phát triển để kiểm thử các kịch bản dự báo (Scenario Testing).")
        
        col_ctrl, col_display = st.columns([1, 2])
        
        with col_ctrl:
            with st.container(border=True):
                st.markdown("**1. Chọn Kịch bản Test:**")
                scenario = st.selectbox("Scenario:", ["Mặc định (Default)", "Sóng nhiệt (Heatwave)", "Tiết kiệm tối đa"])
                
                st.markdown("**2. Điều chỉnh Thời gian giả lập:**")
                # Load dữ liệu để lấy min/max date
                DATA_PATH = "data/household_power_consumption.txt"
                df_source = load_dataset(DATA_PATH, nrows=5000) # Load ít để nhanh
                
                sim_date = st.date_input("Ngày:", df_source.index.min())
                sim_hour = st.slider("Giờ:", 0, 23, 19)
                
                st.markdown("**3. Stress Test:**")
                inject_anomaly = st.checkbox("🔥 Giả lập sự cố (Spike Load)")
                
                btn_sim = st.button("Chạy Giả lập", type="primary", use_container_width=True)

        with col_display:
            st.markdown("#### 📡 Kết quả Monitor thời gian thực")
            
            if btn_sim:
                with st.spinner("Đang khởi tạo môi trường giả lập..."):
                    time.sleep(1) # Fake loading
                    
                    # Logic lấy data
                    try:
                        current_ts = pd.Timestamp(f"{sim_date} {sim_hour}:00:00")
                        idx = df_source.index.get_indexer([current_ts], method='nearest')[0]
                        current_data = df_source.iloc[idx].copy()
                        
                        # Xử lý kịch bản
                        load_val = current_data['Global_active_power']
                        if scenario == "Sóng nhiệt (Heatwave)":
                            load_val *= 1.5 # Tăng tải 50%
                            st.toast("⚠️ Đã kích hoạt kịch bản Sóng nhiệt!", icon="🔥")
                        elif inject_anomaly:
                            load_val *= 3.0 # Tăng đột biến
                            st.error("🚨 PHÁT HIỆN SỰ CỐ: Tải tăng đột biến!")
                            
                        # Vẽ biểu đồ nhanh
                        fig_sim = go.Figure(go.Indicator(
                            mode = "gauge+number+delta",
                            value = load_val,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Tải hệ thống (kW)"},
                            delta = {'reference': 2.0, 'increasing': {'color': "red"}},
                            gauge = {'axis': {'range': [None, 10]}, 'bar': {'color': "#00C9FF"}}
                        ))
                        fig_sim.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                        st.plotly_chart(fig_sim, use_container_width=True)
                        
                        st.success(f"Dữ liệu tại {sim_hour}:00 đang được xử lý ổn định.")
                        
                    except Exception as e:
                        st.warning("Vui lòng chọn ngày khác trong phạm vi dữ liệu demo.")
            else:
                st.info("👈 Nhấn 'Chạy Giả lập' để xem kết quả monitor.")