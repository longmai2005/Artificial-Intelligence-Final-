"""
Component hiển thị báo cáo phân tích AI
"""

import streamlit as st
from src.backend.ai_analyzer import analyze_with_gemini, get_quick_tips_by_device

def render_ai_report(total_kwh, breakdown, user_inputs):
    """
    Hiển thị báo cáo phân tích AI với giao diện đẹp
    """
    
    st.markdown("### 🤖 Báo cáo Phân tích Từ AI Expert")
    
    # Button để tạo báo cáo chi tiết
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("✨ Tạo Báo cáo Chi tiết từ AI", type="primary", width='stretch'):
            with st.spinner("🤖 AI Expert đang phân tích sâu..."):
                # Gọi Gemini AI
                analysis = analyze_with_gemini(total_kwh, breakdown, user_inputs)
                st.session_state['ai_analysis'] = analysis
    
    with col2:
        if st.button("📥 Xuất PDF", width='stretch'):
            st.info("Tính năng đang phát triển!")
    
    with col3:
        if st.button("📧 Gửi Email", width='stretch'):
            st.info("Tính năng đang phát triển!")
    
    st.markdown("---")
    
    # Hiển thị báo cáo nếu có
    if 'ai_analysis' in st.session_state:
        # Container với border đẹp
        with st.container(border=True):
            st.markdown(st.session_state['ai_analysis'])
        
        # Phần Quick Tips cho từng thiết bị
        st.markdown("### ⚡ Quick Tips cho Từng thiết bị")
        
        cols = st.columns(2)
        
        for idx, (device, kwh) in enumerate(breakdown.items()):
            percent = (kwh / total_kwh) * 100
            
            with cols[idx % 2]:
                with st.expander(f"{device} - {kwh:.0f} kWh ({percent:.0f}%)"):
                    tips = get_quick_tips_by_device(device, kwh, percent)
                    for tip in tips:
                        st.markdown(f"- {tip}")
    else:
        # Hiển thị thông tin giới thiệu
        st.info("""
        **🎯 Báo cáo AI Expert bao gồm:**
        
        ✅ Phân tích chi tiết tình hình tiêu thụ  
        ✅ Đề xuất 5 hành động cụ thể ngay lập tức  
        ✅ Ước tính tiết kiệm (kWh + tiền)  
        ✅ Lộ trình 30 ngày dễ thực hiện  
        ✅ So sánh với hộ gia đình trung bình  
        
        👆 **Nhấn nút phía trên để bắt đầu!**
        """)


def render_comparison_chart(user_kwh):
    """
    Vẽ biểu đồ so sánh với các mức tiêu thụ
    """
    import plotly.graph_objects as go
    
    categories = ['Tiết kiệm\n(< 150 kWh)', 'Trung bình\n(150-250 kWh)', 
                  'Cao\n(250-350 kWh)', 'Rất cao\n(> 350 kWh)', f'Bạn\n({user_kwh:.0f} kWh)']
    
    values = [125, 200, 300, 450, user_kwh]
    colors = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6']
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f'{v:.0f} kWh' for v in values],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="So sánh Mức tiêu thụ",
        yaxis_title="kWh/tháng",
        height=350,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def render_saving_calculator():
    """
    Máy tính tiết kiệm tương tác
    """
    st.markdown("### 🧮 Máy tính Tiết kiệm")
    
    with st.container(border=True):
        st.markdown("**Nếu bạn giảm thiết bị này, sẽ tiết kiệm bao nhiêu?**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            device_type = st.selectbox(
                "Chọn thiết bị",
                ["Máy lạnh", "Tủ lạnh", "TV", "Đèn", "Máy giặt"]
            )
            
            current_hours = st.slider("Giờ sử dụng hiện tại/ngày", 0, 24, 8)
            target_hours = st.slider("Giảm xuống còn (giờ/ngày)", 0, 24, 6)
        
        with col2:
            # Công suất thiết bị (kW)
            power_map = {
                "Máy lạnh": 1.5,
                "Tủ lạnh": 0.15,
                "TV": 0.1,
                "Đèn": 0.05,
                "Máy giặt": 0.5
            }
            
            power = power_map[device_type]
            
            # Tính toán
            current_kwh = power * current_hours * 30
            target_kwh = power * target_hours * 30
            saving_kwh = current_kwh - target_kwh
            saving_money = saving_kwh * 2500
            
            st.metric("Tiết kiệm/tháng", f"{saving_money:,.0f} đ", 
                     delta=f"-{saving_kwh:.0f} kWh")
            st.metric("Tiết kiệm/năm", f"{saving_money*12:,.0f} đ")
            
            st.success(f"💡 Giảm {current_hours - target_hours} giờ/ngày = Tiết kiệm {saving_money:,.0f}đ/tháng!")