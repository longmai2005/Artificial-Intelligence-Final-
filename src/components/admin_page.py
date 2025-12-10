import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import time
from src.backend.auth import load_users, USER_DB_PATH
from src.utils.style import card_container

# --- HÀM HỖ TRỢ LOGIC ADMIN ---
def delete_user(username_to_delete):
    """Xóa user khỏi CSDL"""
    users = load_users()
    if username_to_delete in users:
        if users[username_to_delete]['role'] == 'admin':
            return False, "⚠️ Không thể xóa tài khoản Admin quản trị!"
        
        del users[username_to_delete]
        with open(USER_DB_PATH, "w") as f:
            json.dump(users, f)
        return True, f"✅ Đã xóa người dùng {username_to_delete} thành công!"
    return False, "❌ Người dùng không tồn tại."

def get_system_metrics(users):
    """Tính toán các chỉ số hệ thống giả lập"""
    total_users = len(users)
    active_users = len([u for u in users.values() if u['role'] == 'user'])
    # Giả lập tải hệ thống (Total Load)
    system_load = np.random.randint(120, 150) 
    server_status = "🟢 Ổn định"
    return total_users, active_users, system_load, server_status

# --- GIAO DIỆN CHÍNH ---
def render_admin_page():
    # 1. HEADER
    st.markdown("## 🛡️ Trung Tâm Quản Trị (Admin Hub)")
    st.markdown("---")

    # 2. KPI CARDS (Hiển thị số liệu tổng quan)
    users = load_users()
    total, active, load, status = get_system_metrics(users)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: card_container("Tổng Tài khoản", f"{total}")
    with col2: card_container("Khách hàng (Active)", f"{active}")
    with col3: card_container("Tải Hệ thống", f"{load} kW", "Low")
    with col4: card_container("Trạng thái Server", "Online", "99.9%")

    st.markdown("---")

    # 3. TABS CHỨC NĂNG
    tab_dashboard, tab_users, tab_settings = st.tabs(["📊 Phân Tích Dữ Liệu", "👥 Quản Lý Người Dùng", "⚙️ Cấu Hình"])

    # === TAB 1: DASHBOARD ANALYTICS ===
    with tab_dashboard:
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.markdown("#### 📈 Xu hướng tiêu thụ toàn hệ thống (7 ngày)")
            # Giả lập dữ liệu Line Chart
            days = pd.date_range(start="2025-12-01", periods=7).strftime("%d/%m")
            loads = np.random.randint(800, 1200, 7)
            
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=days, y=loads, mode='lines+markers', 
                                        line=dict(color='#00C9FF', width=4), name='Tổng tải'))
            fig_line.add_trace(go.Scatter(x=days, y=[1000]*7, mode='lines', 
                                        line=dict(color='red', dash='dash'), name='Ngưỡng cảnh báo'))
            
            fig_line.update_layout(
                height=350, 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font=dict(color='white'),
                margin=dict(l=0,r=0,t=20,b=0),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig_line, use_container_width=True)

        with c2:
            st.markdown("#### 🏠 Phân bố loại nhà")
            # Giả lập Pie Chart
            data_pie = pd.DataFrame({
                'Type': ['Chung cư', 'Nhà phố', 'Biệt thự'],
                'Count': [45, 30, 25]
            })
            fig_pie = px.pie(data_pie, values='Count', names='Type', hole=0.5, 
                           color_discrete_sequence=['#3b82f6', '#8b5cf6', '#06b6d4'])
            fig_pie.update_layout(
                height=350, 
                paper_bgcolor='rgba(0,0,0,0)', 
                font=dict(color='white'),
                margin=dict(l=0,r=0,t=20,b=0),
                showlegend=True,
                legend=dict(orientation="h", y=-0.1)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # Heatmap toàn rộng
        st.markdown("#### 🔥 Bản đồ nhiệt: Giờ cao điểm trong tuần")
        hm_z = np.random.rand(7, 24) * 10
        hm_z[:, 18:22] += 5 # Tăng tải giờ tối
        
        fig_hm = go.Figure(data=go.Heatmap(
            z=hm_z,
            x=[f"{i}h" for i in range(24)],
            y=['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
            colorscale='Viridis'
        ))
        fig_hm.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(t=0,b=0))
        st.plotly_chart(fig_hm, use_container_width=True)

    # === TAB 2: QUẢN LÝ USER ===
    with tab_users:
        c_search, c_action = st.columns([3, 1])
        with c_search:
            st.markdown("### 📋 Danh sách người dùng")
        with c_action:
            # Chức năng Xuất CSV
            user_data_csv = pd.DataFrame(users).T.to_csv().encode('utf-8')
            st.download_button(
                label="📥 Xuất Excel (CSV)",
                data=user_data_csv,
                file_name='ds_nguoi_dung.csv',
                mime='text/csv',
            )

        # Hiển thị bảng User đẹp
        user_list = []
        for u, data in users.items():
            user_list.append({
                "Username": u,
                "Họ Tên": data.get("name", "N/A"),
                "Email": data.get("email", "Chưa cập nhật"),
                "Vai trò": "👑 Admin" if data.get("role") == "admin" else "👤 User",
                "Trạng thái": "🟢 Active"
            })
        
        df_users = pd.DataFrame(user_list)
        st.dataframe(
            df_users, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Vai trò": st.column_config.TextColumn("Vai trò", width="small"),
                "Email": st.column_config.TextColumn("Email", width="medium"),
            }
        )

        st.divider()
        st.markdown("### ⚠️ Vùng Nguy Hiểm")
        with st.container(border=True):
            col_del_1, col_del_2 = st.columns([3, 1])
            with col_del_1:
                u_del = st.selectbox("Chọn người dùng cần xóa:", 
                                   [u for u in users.keys() if u != 'admin'])
            with col_del_2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Xóa Vĩnh Viễn 🗑️", type="primary"):
                    success, msg = delete_user(u_del)
                    if success:
                        st.toast(msg, icon="✅")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)

    # === TAB 3: CẤU HÌNH HỆ THỐNG ===
    with tab_settings:
        st.info("🔧 Các cài đặt này ảnh hưởng đến mô hình dự báo của toàn bộ người dùng.")
        
        c_set_1, c_set_2 = st.columns(2)
        with c_set_1:
            st.markdown("#### 🎛️ Tham số Dự báo")
            st.slider("Ngưỡng cảnh báo tải cao (kW)", 0, 10, 5)
            st.slider("Độ nhạy của AI (%)", 0, 100, 85)
            st.toggle("Bật chế độ Tiết kiệm năng lượng khẩn cấp")
        
        with c_set_2:
            st.markdown("#### 📅 Chu kỳ cập nhật")
            st.selectbox("Tần suất cập nhật dữ liệu", ["Real-time (5s)", "1 Phút", "1 Giờ", "Hàng ngày"])
            st.checkbox("Tự động sao lưu lịch sử (Auto-backup)", value=True)
            
            if st.button("♻️ Khởi động lại Server Giả lập"):
                with st.spinner("Đang khởi động lại..."):
                    time.sleep(2)
                st.success("Hệ thống đã khởi động lại!")