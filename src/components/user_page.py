import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
from src.backend.history import save_history, load_history
from src.backend.logic_engine import calculate_evn_bill
from src.backend.predictor import EnergyPredictor
from src.utils.style import card_container, render_hero_section
# IMPORT LOGGER
from src.backend.logger import log_info

# Khởi tạo predictor (cache để không load lại nhiều lần)
@st.cache_resource
def get_predictor():
    return EnergyPredictor()

def generate_ai_insights(total_kwh, breakdown, user_inputs):
    """Tạo phân tích AI từ dữ liệu dự đoán"""
    insights = []
    
    # 1. Phân tích tổng quan
    if total_kwh > 400:
        level = "🔴 RẤT CAO"
        status = "critical"
    elif total_kwh > 300:
        level = "🟡 CAO"
        status = "warning"
    elif total_kwh > 200:
        level = "🟢 TRUNG BÌNH"
        status = "normal"
    else:
        level = "✅ THẤP"
        status = "good"
    
    insights.append({
        "title": "📊 Đánh giá Tổng quan",
        "content": f"Mức tiêu thụ điện của bạn: **{level}** ({total_kwh:.0f} kWh/tháng)",
        "type": status
    })
    
    # 2. Phân tích thiết bị tiêu thụ nhiều nhất
    max_device = max(breakdown.items(), key=lambda x: x[1])
    insights.append({
        "title": "⚡ Thiết bị tiêu thụ nhiều nhất",
        "content": f"**{max_device[0]}** chiếm {max_device[1]/total_kwh*100:.1f}% ({max_device[1]:.0f} kWh/tháng)",
        "type": "info"
    })
    
    # 3. So sánh với trung bình
    avg_household = 250  # kWh trung bình
    diff_percent = ((total_kwh - avg_household) / avg_household) * 100
    
    if diff_percent > 0:
        insights.append({
            "title": "📈 So sánh với Hộ gia đình Trung bình",
            "content": f"Bạn đang tiêu thụ **cao hơn {diff_percent:.0f}%** so với hộ gia đình trung bình ({avg_household} kWh/tháng)",
            "type": "warning"
        })
    else:
        insights.append({
            "title": "📉 So sánh với Hộ gia đình Trung bình",
            "content": f"Tuyệt vời! Bạn đang tiết kiệm **{abs(diff_percent):.0f}%** so với trung bình ({avg_household} kWh/tháng)",
            "type": "success"
        })
    
    return insights

def generate_saving_recommendations(breakdown, user_inputs, total_kwh):
    """Tạo đề xuất tiết kiệm dựa trên phân tích"""
    recommendations = []
    
    # Phân tích từng thiết bị
    for device, kwh in breakdown.items():
        percent = (kwh / total_kwh) * 100
        
        if device == "Máy lạnh" and percent > 40:
            saving_kwh = kwh * 0.2  # Tiết kiệm 20%
            saving_money = saving_kwh * 2500
            recommendations.append({
                "device": "❄️ Máy lạnh",
                "current": f"{kwh:.0f} kWh ({percent:.0f}%)",
                "issue": "Tiêu thụ quá cao - chiếm gần nửa hóa đơn",
                "actions": [
                    "Đặt nhiệt độ 26-27°C thay vì 22-24°C",
                    "Bật chế độ tiết kiệm điện (Eco mode)",
                    "Vệ sinh lưới lọc gió mỗi 2 tuần",
                    "Tắt máy khi ra ngoài >30 phút"
                ],
                "potential_saving": f"Tiết kiệm: ~{saving_kwh:.0f} kWh ≈ {saving_money:,.0f}đ/tháng",
                "priority": "high"
            })
        
        elif device == "Tủ lạnh" and percent > 15:
            saving_kwh = kwh * 0.15
            saving_money = saving_kwh * 2500
            recommendations.append({
                "device": "🧊 Tủ lạnh",
                "current": f"{kwh:.0f} kWh ({percent:.0f}%)",
                "issue": "Hoạt động không tối ưu",
                "actions": [
                    "Không để thức ăn nóng vào tủ",
                    "Kiểm tra gioăng cao su cửa",
                    "Để tủ cách tường 10cm để thoát nhiệt",
                    "Rã đông định kỳ (nếu không có tự động)"
                ],
                "potential_saving": f"Tiết kiệm: ~{saving_kwh:.0f} kWh ≈ {saving_money:,.0f}đ/tháng",
                "priority": "medium"
            })
        
        elif device == "Chiếu sáng" and percent > 10:
            saving_kwh = kwh * 0.3
            saving_money = saving_kwh * 2500
            recommendations.append({
                "device": "💡 Chiếu sáng",
                "current": f"{kwh:.0f} kWh ({percent:.0f}%)",
                "issue": "Có thể tối ưu hơn",
                "actions": [
                    "Thay bóng LED tiết kiệm năng lượng",
                    "Tắt đèn khi không dùng",
                    "Sử dụng ánh sáng tự nhiên ban ngày",
                    "Lắp cảm biến chuyển động cho hành lang"
                ],
                "potential_saving": f"Tiết kiệm: ~{saving_kwh:.0f} kWh ≈ {saving_money:,.0f}đ/tháng",
                "priority": "low"
            })
    
    # Đề xuất chung
    if user_inputs['hours_per_day'] > 12:
        recommendations.append({
            "device": "🏠 Thói quen chung",
            "current": f"{user_inputs['hours_per_day']} giờ/ngày",
            "issue": "Thời gian sử dụng thiết bị quá dài",
            "actions": [
                "Tắt thiết bị khi không sử dụng",
                "Rút phích cắm các thiết bị chờ (standby)",
                "Sử dụng ổ cắm thông minh có hẹn giờ",
                "Tập trung sinh hoạt vào 1-2 phòng buổi tối"
            ],
            "potential_saving": "Có thể tiết kiệm 10-15% tổng hóa đơn",
            "priority": "high"
        })
    
    # Đề xuất dựa trên diện tích
    if user_inputs['area_m2'] > 80 and user_inputs['num_ac'] < 2:
        recommendations.append({
            "device": "📐 Diện tích nhà",
            "current": f"{user_inputs['area_m2']}m² - {user_inputs['num_ac']} máy lạnh",
            "issue": "Máy lạnh có thể phải hoạt động quá tải",
            "actions": [
                "Cân nhắc thêm 1 máy lạnh công suất nhỏ",
                "Cách nhiệt tốt hơn (rèm, cửa)",
                "Đóng cửa phòng đang làm mát"
            ],
            "potential_saving": "Tối ưu hiệu quả, giảm hao mòn máy",
            "priority": "medium"
        })
    
    return recommendations

def render_user_page(username, name):
    render_hero_section(name)
    tab1, tab2, tab3 = st.tabs(["🚀 Điều Khiển", "📊 Xếp Hạng", "📜 Lịch Sử"])
    
    with tab1:
        st.markdown("### 🏠 Nhập Thông tin Hộ Gia đình")
        
        col_input, col_result = st.columns([1, 1.2])
        
        with col_input:
            with st.container(border=True):
                st.markdown("#### 📝 Thông tin cơ bản")
                
                num_people = st.number_input(
                    "👥 Số người trong gia đình",
                    min_value=1, max_value=10, value=3,
                    help="Số người sinh sống thường xuyên"
                )
                
                area_m2 = st.number_input(
                    "📐 Diện tích nhà (m²)",
                    min_value=20, max_value=300, value=60,
                    help="Tổng diện tích sàn"
                )
                
                house_type = st.selectbox(
                    "🏘️ Loại nhà",
                    ["Chung cư", "Nhà phố", "Biệt thự"],
                    help="Loại hình nhà ở"
                )
            
            with st.container(border=True):
                s_ac = st.toggle("❄️ Máy lạnh", True)
                s_li = st.toggle("💡 Đèn", True)
                s_wa = st.toggle("🔥 Nước nóng", True)
                st.divider()
                st.caption("Thông số nhà")
                house = st.selectbox("Loại nhà", ["Chung cư", "Nhà phố", "Biệt thự"])
                ac_n = st.number_input("Số AC", 0, 5, 1)
                fr_n = st.number_input("Số Tủ lạnh", 0, 3, 1)
                mem = st.slider("Người", 1, 10, 2)
                if st.button("🔄 Chạy Dự Báo", type="primary", use_container_width=True):
                    with st.spinner("AI Computing..."): time.sleep(0.5)
                    hourly, total = calculate_forecast(ac_n, fr_n, mem, house, {'ac': s_ac, 'lights': s_li, 'water': s_wa})
                    bill, _ = calculate_evn_bill(total * 30)
                    st.session_state['res'] = {'h': hourly, 't': total, 'b': bill}
                    save_history(username, f"{house}", total, bill/30)

        with c1:
            if 'res' in st.session_state:
                r = st.session_state['res']
                k1, k2, k3 = st.columns(3)
                with k1: card_container("Tiêu thụ ngày", f"{r['t']:.1f} kWh")
                with k2: card_container("Chi phí ngày", f"{int(r['b']/30):,} đ")
                with k3: card_container("Dự báo tháng", f"{int(r['b']):,} đ")
                fig = go.Figure(go.Scatter(x=np.arange(24), y=r['h'], fill='tozeroy', line=dict(color='#3b82f6')))
                fig.update_layout(title="Biểu đồ tải 24h", height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=30,b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("👈 Nhập thông tin và bấm Chạy Dự Báo.")

    with tab2:
        st.dataframe(pd.DataFrame([["🥇", "User A", 950], ["🥈", "User B", 890], ["🥉", name, 850]], columns=["Rank", "User", "Score"]), use_container_width=True)

    with tab3:
        st.markdown("### 📜 Lịch sử Dự đoán")
        
        history = load_history(username)
        
        if history:
            df_history = pd.DataFrame(history)
            
            # Thống kê tổng quan
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tổng lần dự đoán", len(history))
            with col2:
                avg_kwh = df_history['kwh'].mean()
                st.metric("TB Tiêu thụ", f"{avg_kwh:.0f} kWh")
            with col3:
                avg_cost = df_history['cost'].mean()
                st.metric("TB Chi phí", f"{avg_cost:,.0f} đ")
            
            # Bảng lịch sử
            st.dataframe(
                df_history,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "timestamp": "Thời gian",
                    "inputs": "Thông tin",
                    "kwh": st.column_config.NumberColumn("kWh/tháng", format="%.1f"),
                    "cost": st.column_config.NumberColumn("Chi phí/tháng", format="%d đ")
                }
            )
            
            # Biểu đồ xu hướng
            if len(history) > 1:
                st.markdown("#### 📈 Xu hướng Tiêu thụ")
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=list(range(1, len(history)+1)),
                    y=df_history['kwh'],
                    mode='lines+markers',
                    name='kWh',
                    line=dict(color='#3b82f6', width=2)
                ))
                fig_trend.update_layout(
                    height=300,
                    xaxis_title="Lần dự đoán",
                    yaxis_title="kWh/tháng",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("📭 Chưa có lịch sử dự đoán. Hãy thử dự đoán lần đầu!")
    
    # ==================== TAB 4: THỐNG KÊ ====================
    with tab4:
        st.markdown("### 🏆 Thống kê & Xếp hạng")
        
        if 'prediction_result' in st.session_state:
            result = st.session_state['prediction_result']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎯 Mức độ Tiết kiệm")
                
                # Tính điểm tiết kiệm
                score = 100
                kwh = result['total_kwh']
                
                if kwh > 400:
                    score = 40
                    rank = "🥉 Cần cải thiện"
                elif kwh > 300:
                    score = 60
                    rank = "🥈 Khá tốt"
                elif kwh > 200:
                    score = 80
                    rank = "🥇 Tốt"
                else:
                    score = 95
                    rank = "🏆 Xuất sắc"
                
                # Progress bar
                st.progress(score / 100)
                st.markdown(f"### {rank}")
                st.caption(f"Điểm: {score}/100")
            
            with col2:
                st.markdown("#### 🌍 So với Trung bình")
                
                avg_household = 250
                diff = kwh - avg_household
                diff_percent = (diff / avg_household) * 100
                
                if diff > 0:
                    st.error(f"Cao hơn {diff_percent:.0f}% 📈")
                else:
                    st.success(f"Thấp hơn {abs(diff_percent):.0f}% 📉")
                
                st.metric("Hộ TB", f"{avg_household} kWh")
                st.metric("Bạn", f"{kwh:.0f} kWh")
        else:
            st.info("Thực hiện dự đoán để xem thống kê!")