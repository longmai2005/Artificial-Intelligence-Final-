import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import numpy as np
from src.backend.auth import load_users, USER_DB_PATH
from src.utils.style import card_container

def delete_user(username_to_delete):
    users = load_users()
    if username_to_delete in users:
        if users[username_to_delete]['role'] == 'admin':
            return False, "Không thể xóa Admin gốc!"
        del users[username_to_delete]
        with open(USER_DB_PATH, "w") as f:
            json.dump(users, f)
        return True, "Đã xóa thành công!"
    return False, "User không tồn tại."

def render_admin_page():
    st.markdown("## 🛡️ Admin Control Center")
    st.markdown("---")

    users_db = load_users()
    total_users = len(users_db)
    regular_users = len([u for u in users_db.values() if u['role'] == 'user'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: card_container("Tổng Tài khoản", f"{total_users}")
    with col2: card_container("User Active", f"{regular_users}")
    with col3: card_container("Server Status", "Online")
    with col4: card_container("AI Accuracy", "94%")

    st.markdown("---")

    tab1, tab2 = st.tabs(["👥 Quản Lý Người Dùng", "📊 Thống Kê Hệ Thống"])

    with tab1:
        st.subheader("Danh sách người dùng")
        
        user_list = []
        for u, data in users_db.items():
            user_list.append({
                "Username": u,
                "Họ Tên": data.get("name", "N/A"),
                "Email": data.get("email", "N/A"),
                "Role": data.get("role", "user")
            })
        df = pd.DataFrame(user_list)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("### 🗑️ Xóa Người Dùng")
        with st.expander("Mở công cụ xóa"):
            user_options = [u for u in users_db.keys() if u != 'admin']
            if user_options:
                col_del, col_btn = st.columns([3, 1])
                with col_del:
                    user_to_del = st.selectbox("Chọn user:", user_options)
                with col_btn:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Xóa vĩnh viễn ❌", type="primary"):
                        success, msg = delete_user(user_to_del)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            else:
                st.info("Chưa có user nào để xóa.")

    with tab2:
        st.subheader("🔥 Heatmap: Mật độ tiêu thụ điện")
        days = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
        hours = [f"{i}h" for i in range(24)]
        z_data = np.random.rand(7, 24) * 5
        z_data[:, 18:22] += 5 
        
        fig = go.Figure(data=go.Heatmap(z=z_data, x=hours, y=days, colorscale='Magma'))
        fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          font=dict(color='white'), margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)