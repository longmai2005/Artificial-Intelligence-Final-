import streamlit as st
from src.backend.logic_engine import generate_insights

def render_recommendations(current_time, current_data):
    st.subheader("💡 Đề xuất Tiết kiệm Năng lượng")
    
    sub_meters = [current_data['Sub_metering_1'], 
                  current_data['Sub_metering_2'], 
                  current_data['Sub_metering_3']]
    
    insights = generate_insights(current_time.hour, current_data['Global_active_power'], sub_meters)
    
    for item in insights:
        if item['type'] == 'warning':
            st.error(f"**CẢNH BÁO:** {item['msg']}\n\n👉 *{item['action']}*")
        elif item['type'] == 'info':
            st.info(f"**LƯU Ý:** {item['msg']}\n\n👉 *{item['action']}*")
        else:
            st.success(f"**TỐT:** {item['msg']}")
            
    # Phần Simulator (Giả lập)
    st.markdown("---")
    st.write("🛠 **Công cụ Giả lập Tiết kiệm**")
    temp_reduce = st.slider("Nếu giảm điều hòa (độ C):", 0, 5, 1)
    if temp_reduce > 0:
        saved = temp_reduce * 4000 # Giả định 1 độ = 4000đ
        st.caption(f"Bạn sẽ tiết kiệm được khoảng: **{saved} VNĐ / giờ**")