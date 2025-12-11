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
    
    # Tabs chính
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔮 Dự đoán Điện năng", 
        "💡 Đề xuất Tiết kiệm",
        "📜 Lịch sử Dự đoán",
        "🏆 Thống kê"
    ])
    
    # ==================== TAB 1: DỰ ĐOÁN ====================
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
                st.markdown("#### 🔌 Thiết bị điện")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    num_ac = st.number_input("❄️ Máy lạnh", 0, 5, 1)
                    num_tv = st.number_input("📺 TV", 0, 5, 1)
                    
                with col_b:
                    num_fridge = st.number_input("🧊 Tủ lạnh", 0, 3, 1)
                    num_washer = st.number_input("🌀 Máy giặt", 0, 2, 1)
                
                hours_per_day = st.slider(
                    "⏰ Thời gian sử dụng thiết bị (giờ/ngày)",
                    min_value=4, max_value=16, value=8,
                    help="Thời gian trung bình các thiết bị hoạt động"
                )
            
            # Nút Dự đoán
            st.markdown("<br>", unsafe_allow_html=True)
            predict_btn = st.button(
                "🚀 Dự đoán với AI",
                type="primary",
                use_container_width=True
            )
        
        with col_result:
            if predict_btn:
                with st.spinner("🤖 AI đang phân tích dữ liệu..."):
                    time.sleep(1.5)
                    
                    # Load predictor
                    predictor = get_predictor()
                    
                    # Dự đoán
                    total_kwh, breakdown = predictor.predict_monthly_consumption(
                        num_people=num_people,
                        area_m2=area_m2,
                        num_ac=num_ac,
                        num_fridge=num_fridge,
                        num_tv=num_tv,
                        hours_per_day=hours_per_day
                    )
                    
                    # Tính tiền điện EVN
                    total_cost, cost_breakdown = calculate_evn_bill(total_kwh)
                    
                    # Lưu vào session state
                    st.session_state['prediction_result'] = {
                        'total_kwh': total_kwh,
                        'breakdown': breakdown,
                        'total_cost': total_cost,
                        'cost_breakdown': cost_breakdown,
                        'user_inputs': {
                            'num_people': num_people,
                            'area_m2': area_m2,
                            'num_ac': num_ac,
                            'num_fridge': num_fridge,
                            'num_tv': num_tv,
                            'hours_per_day': hours_per_day,
                            'house_type': house_type
                        },
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Lưu lịch sử
                    save_history(
                        username,
                        input_data=f"{house_type} - {num_people} người - {area_m2}m²",
                        result_kwh=total_kwh,
                        total_cost=total_cost
                    )
                    
                    st.success("✅ Dự đoán hoàn tất!")
                    st.rerun()
            
            # Hiển thị kết quả
            if 'prediction_result' in st.session_state:
                result = st.session_state['prediction_result']
                
                # KPI Cards
                st.markdown("#### 📊 Kết quả Dự đoán")
                k1, k2, k3 = st.columns(3)
                
                with k1:
                    st.metric(
                        "⚡ Tổng tiêu thụ",
                        f"{result['total_kwh']:.0f} kWh",
                        delta=f"{(result['total_kwh']-250):.0f} vs TB",
                        delta_color="inverse"
                    )
                
                with k2:
                    daily_cost = result['total_cost'] / 30
                    st.metric(
                        "💵 Chi phí/ngày",
                        f"{daily_cost:,.0f} đ"
                    )
                
                with k3:
                    st.metric(
                        "📅 Chi phí/tháng",
                        f"{result['total_cost']:,.0f} đ"
                    )
                
                # Biểu đồ Pie - Phân bổ thiết bị
                st.markdown("#### 📊 Phân bổ Tiêu thụ theo Thiết bị")
                
                df_pie = pd.DataFrame({
                    'Thiết bị': list(result['breakdown'].keys()),
                    'kWh': list(result['breakdown'].values())
                })
                
                fig_pie = px.pie(
                    df_pie,
                    values='kWh',
                    names='Thiết bị',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>%{value:.0f} kWh<br>%{percent}<extra></extra>'
                )
                fig_pie.update_layout(
                    height=350,
                    showlegend=True,
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
                # Chi tiết bậc thang điện
                with st.expander("💰 Chi tiết Bậc thang Điện (EVN)"):
                    for line in result['cost_breakdown']:
                        st.text(line)
                
                # AI Insights
                st.markdown("#### 🤖 Phân tích từ AI")
                insights = generate_ai_insights(
                    result['total_kwh'],
                    result['breakdown'],
                    result['user_inputs']
                )
                
                for insight in insights:
                    if insight['type'] == 'critical':
                        st.error(f"**{insight['title']}**\n\n{insight['content']}")
                    elif insight['type'] == 'warning':
                        st.warning(f"**{insight['title']}**\n\n{insight['content']}")
                    elif insight['type'] == 'success':
                        st.success(f"**{insight['title']}**\n\n{insight['content']}")
                    else:
                        st.info(f"**{insight['title']}**\n\n{insight['content']}")
            
            else:
                st.info("👈 **Hướng dẫn sử dụng:**\n\n1. Nhập thông tin hộ gia đình bên trái\n2. Nhập số lượng thiết bị điện\n3. Chọn thời gian sử dụng\n4. Bấm 'Dự đoán với AI' để xem kết quả")
    
    # ==================== TAB 2: ĐỀ XUẤT TIẾT KIỆM ====================
    with tab2:
        st.markdown("### 💡 Đề xuất Phương án Tiết kiệm Điện")
        
        if 'prediction_result' not in st.session_state:
            st.warning("⚠️ Vui lòng thực hiện dự đoán ở Tab 'Dự đoán Điện năng' trước!")
        else:
            result = st.session_state['prediction_result']
            
            # Tổng quan tiết kiệm
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### 📋 Danh sách Đề xuất")
                
                recommendations = generate_saving_recommendations(
                    result['breakdown'],
                    result['user_inputs'],
                    result['total_kwh']
                )
                
                # Hiển thị từng đề xuất
                for idx, rec in enumerate(recommendations, 1):
                    with st.container(border=True):
                        # Header với priority
                        priority_color = {
                            'high': '🔴',
                            'medium': '🟡',
                            'low': '🟢'
                        }
                        
                        st.markdown(f"### {priority_color.get(rec['priority'], '⚪')} {rec['device']}")
                        
                        # Thông tin hiện tại
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.caption("**Hiện tại:**")
                            st.write(rec['current'])
                        with col_b:
                            st.caption("**Vấn đề:**")
                            st.write(rec['issue'])
                        
                        # Hành động đề xuất
                        st.markdown("**🎯 Giải pháp:**")
                        for action in rec['actions']:
                            st.markdown(f"- {action}")
                        
                        # Tiết kiệm ước tính
                        st.success(f"✨ **{rec['potential_saving']}**")
            
            with col2:
                # Tính tổng tiết kiệm
                st.markdown("#### 💰 Tổng Tiết kiệm Ước tính")
                
                total_saving_kwh = result['total_kwh'] * 0.15  # 15%
                total_saving_money = total_saving_kwh * 2500
                
                with st.container(border=True):
                    st.metric(
                        "Tiết kiệm/tháng",
                        f"{total_saving_money:,.0f} đ",
                        delta=f"-{total_saving_kwh:.0f} kWh"
                    )
                    
                    st.metric(
                        "Tiết kiệm/năm",
                        f"{total_saving_money*12:,.0f} đ"
                    )
                    
                    st.markdown("---")
                    st.caption("*Nếu áp dụng đầy đủ các đề xuất*")
                
                # Biểu đồ so sánh
                st.markdown("#### 📊 Trước - Sau khi tiết kiệm")
                
                current = result['total_kwh']
                after_saving = current - total_saving_kwh
                
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    x=['Hiện tại', 'Sau tiết kiệm'],
                    y=[current, after_saving],
                    text=[f'{current:.0f} kWh', f'{after_saving:.0f} kWh'],
                    textposition='auto',
                    marker_color=['#ef4444', '#22c55e']
                ))
                fig_bar.update_layout(
                    height=300,
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    yaxis=dict(title='kWh/tháng')
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Tips nhanh
                with st.expander("⚡ Tips Tiết kiệm Nhanh"):
                    st.markdown("""
                    - 🌡️ Mỗi độ tăng nhiệt độ máy lạnh tiết kiệm 5-10%
                    - 💡 Bóng LED tiết kiệm 80% so với bóng sợi đốt
                    - 🔌 Rút phích thiết bị chờ tiết kiệm 10% hóa đơn
                    - 🕐 Tránh dùng điện giờ cao điểm (18h-22h)
                    - ❄️ Không mở tủ lạnh quá lâu
                    """)
    
    # ==================== TAB 3: LỊCH SỬ ====================
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