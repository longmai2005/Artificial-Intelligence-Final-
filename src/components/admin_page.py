import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import numpy as np
from src.backend.auth import load_users, USER_DB_PATH
from src.utils.style import card_container

def render_admin_page():
    st.markdown("## 🛡️ Admin Dashboard")
    users = load_users()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: card_container("Tổng User", f"{len(users)}")
    with c2: card_container("Active", f"{len(users)-1}")
    with c3: card_container("Server", "Online")
    with c4: card_container("AI", "94%")
    
    st.markdown("---")
    t1, t2 = st.tabs(["👥 User", "📊 Analytics"])
    
    with t1:
        st.dataframe(pd.DataFrame(users).T, use_container_width=True)
        
        st.markdown("### 🗑️ Xóa User")
        u_del = st.selectbox("Chọn user", [u for u in users if u != 'admin'])
        if st.button(f"Xóa {u_del}"):
            del users[u_del]
            with open(USER_DB_PATH, 'w') as f: json.dump(users, f)
            st.success("Đã xóa!")
            st.rerun()

    with t2:
        fig = go.Figure(go.Heatmap(z=np.random.rand(7, 24), colorscale='Viridis'))
        fig.update_layout(height=350, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)