import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import time
from datetime import datetime, timedelta
from src.backend.auth import load_users, USER_DB_PATH
from src.backend.history import load_history
from src.utils.style import card_container

try:
    from src.backend.logger import get_recent_logs, log_info
except ImportError:
    # Hàm giả lập nếu chưa có logger
    def get_recent_logs(limit=10): return []
    def log_info(msg): pass

def get_visit_stats():
    """
    Hàm lấy dữ liệu truy cập thực tế từ logs thay vì dùng random
    """
    raw_logs = get_recent_logs(limit=1000) # Lấy lượng log đủ lớn để thống kê
    
    # Tạo danh sách 7 ngày gần nhất
    now = datetime.now()
    dates = [(now - timedelta(days=i)).strftime("%d/%m") for i in range(6, -1, -1)]
    visit_counts = {date: 0 for date in dates}
    
    for line in raw_logs:
        try:
            # Giả định log có định dạng: [INFO] YYYY-MM-DD HH:MM:SS - Message
            if " - " in line:
                timestamp_str = line.split("] ")[1].split(" - ")[0]
                dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                date_key = dt.strftime("%d/%m")
                if date_key in visit_counts:
                    visit_counts[date_key] += 1
        except:
            continue
            
    return list(visit_counts.keys()), list(visit_counts.values())

def delete_user(username):
    """Xóa user và ghi log"""
    users = load_users()
    if username in users:
        if users[username]['role'] == 'admin': 
            return False, "⚠️ Không thể xóa Admin!"
        
        del users[username]
        with open(USER_DB_PATH, "w") as f: 
            json.dump(users, f, indent=4)
            
        log_info(f"Admin đã xóa user: {username}")
        return True, "✅ Đã xóa thành công!"
    return False, "❌ Lỗi: User không tồn tại."

def analyze_data(users):
    """Phân tích dữ liệu user active/inactive"""
    total = len(users)
    active_now = 0
    now = datetime.now()
    table_data = []
    
    for u, data in users.items():
        last_login = data.get('last_login', '')
        status = "⚪ Offline"
        
        # Logic Active: Đăng nhập trong 24h qua
        if last_login and last_login != "Chưa đăng nhập":
            try:
                dt = datetime.strptime(last_login, "%Y-%m-%d %H:%M:%S")
                if (now - dt).total_seconds() < 86400:
                    active_now += 1
                    status = "🟢 Online"
                elif (now - dt).days < 7:
                    status = "🟡 Vắng"
            except: pass
            
        table_data.append({
            "Tài khoản": u,
            "Vai trò": "👑 Admin" if data.get('role') == 'admin' else "👤 User",
            "Tên hiển thị": data.get('name', 'N/A'),
            "Đăng nhập cuối": last_login,
            "Trạng thái": status
        })
    return total, active_now, table_data

def render_admin_page():
    # Header & Nút Làm mới
    c_head, c_ref = st.columns([5, 1])
    with c_head:
        st.markdown("## 🛡️ Quản Trị Hệ Thống")
    with c_ref:
        if st.button("🔄 Làm mới", width='stretch'):
            st.rerun()

    # Load dữ liệu
    users = load_users()
    total, active, table_data = analyze_data(users)

    # KPI Cards (Giao diện kính)
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1: card_container("Tổng User", f"{total}")
        with c2: card_container("Đang Online", f"{active}", delta="24h qua")
        with c3: card_container("Server", "Good", delta="CPU 15%")
        with c4: card_container("AI Model", "94%", delta="Accuracy")

    st.markdown("<br>", unsafe_allow_html=True)
    tabs = st.tabs(["📊 Tổng Quan", "👥 Quản Lý User", "📜 Nhật Ký Hoạt Động"])

    # --- TAB 1: DASHBOARD ---
    with tabs[0]:
        c_left, c_right = st.columns([2, 1])
        with c_left:
            with st.container(border=True):
                st.markdown("##### 📈 Truy cập tuần qua")
                dates, visits = get_visit_stats()
                fig = go.Figure(go.Scatter(x=dates, y=visits, fill='tozeroy', line=dict(color='#8b5cf6')))
                fig.update_layout(
                    height=300, 
                    margin=dict(l=20,r=20,t=20,b=20), 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)', 
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
                )
                st.plotly_chart(fig, width='stretch')
        
        with c_right:
            with st.container(border=True):
                st.markdown("##### 🍰 Thiết bị")
                fig_pie = px.pie(values=[40, 20, 20, 20], names=['Máy lạnh', 'Tủ lạnh', 'Đèn', 'Khác'],
                            color_discrete_sequence=['#3b82f6', '#06b6d4', '#8b5cf6', '#64748b'])
                fig_pie.update_layout(height=300, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", y=-0.2))
                st.plotly_chart(fig_pie, width='stretch')

    # --- TAB 2: USER MANAGEMENT ---
    with tabs[1]:
        with st.container(border=True):
            # Bảng danh sách user
            st.dataframe(
                pd.DataFrame(table_data), 
                width='stretch', 
                hide_index=True,
                column_config={
                    "Trạng thái": st.column_config.TextColumn("Status", width="small"),
                    "Đăng nhập cuối": st.column_config.TextColumn("Last Login", width="medium"),
                }
            )
            
            st.divider()
            st.markdown("##### 🗑️ Xóa Tài Khoản")
            c_del, c_btn = st.columns([3, 1])
            with c_del:
                # Lọc bỏ admin ra khỏi danh sách xóa
                u_del = st.selectbox("Chọn user:", [u for u in users if u != 'admin'], label_visibility="collapsed")
            with c_btn:
                if st.button("Xóa User", type="primary", width='stretch'):
                    if u_del:
                        ok, msg = delete_user(u_del)
                        if ok:
                            st.success(msg)
                            time.sleep(1.5) # Dừng 1.5s để hiện thông báo rồi mới reload
                            st.rerun()
                        else: st.error(msg)
                    else:
                        st.warning("Không có user nào để xóa.")

    # --- TAB 3: SYSTEM LOGS ---
    with tabs[2]:
        st.info("Nhật ký ghi lại mọi hoạt động Đăng nhập, Đăng ký và Dự báo AI.")
        
        raw_logs = get_recent_logs(limit=50)
        log_data = []
        
        for line in raw_logs:
            try:
                # Parse log: "[INFO] 2025... - Message"
                if " - " in line:
                    parts = line.strip().split(" - ", 1)
                    meta = parts[0].split("] ", 1)
                    level = meta[0].replace("[", "")
                    timestamp = meta[1]
                    message = parts[1]
                    log_data.append({"Thời gian": timestamp, "Cấp độ": level, "Nội dung": message})
            except: continue
                
        if log_data:
            st.dataframe(pd.DataFrame(log_data), width='stretch', hide_index=True, column_config={
                "Cấp độ": st.column_config.TextColumn("Loại", width="small"),
                "Nội dung": st.column_config.TextColumn("Chi tiết hành động", width="large"),
            })
        else:
            st.warning("Chưa có dữ liệu nhật ký nào.")