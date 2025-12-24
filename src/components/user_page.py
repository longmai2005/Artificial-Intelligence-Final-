"""
User Page - Smart User Input với Improved Predictor
Hiển thị confidence, blend methodology, device breakdown
"""

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
from src.backend.data_loader import load_dataset
from src.utils.style import render_hero_section

@st.cache_resource
def get_predictor():
    return EnergyPredictor()

@st.cache_data
def get_historical_data():
    """Load dữ liệu lịch sử - lấy sample lớn hơn để có pattern tốt"""
    return load_dataset(nrows=200000)  # 200k điểm ≈ 138 ngày


def render_confidence_indicator(confidence):
    """Hiển thị độ tin cậy bằng color-coded badge"""
    
    if confidence >= 0.7:
        color = "🟢"
        text = "CAO"
        style = "success"
    elif confidence >= 0.5:
        color = "🟡"
        text = "TRUNG BÌNH"
        style = "warning"
    else:
        color = "🔴"
        text = "THẤP"
        style = "error"
    
    st.markdown(f"""
    <div style="
        background: {'#d4edda' if style=='success' else '#fff3cd' if style=='warning' else '#f8d7da'};
        border: 1px solid {'#c3e6cb' if style=='success' else '#ffeeba' if style=='warning' else '#f5c6cb'};
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    ">
        <strong>{color} Độ tin cậy: {text}</strong><br>
        <span style="font-size: 24px; font-weight: bold;">{confidence*100:.0f}%</span>
    </div>
    """, unsafe_allow_html=True)


def render_methodology_explanation():
    """Giải thích phương pháp dự đoán"""
    
    with st.expander("📚 Phương pháp Dự đoán (Nhấn để xem chi tiết)"):
        st.markdown("""
        ### 🧠 Phương pháp Kết hợp Thông minh (Hybrid Approach)
        
        Hệ thống sử dụng **2 phương pháp bổ trợ** để đưa ra dự đoán chính xác nhất:
        
        #### 1️⃣ Pattern Thời gian (Time-based Pattern) - R² = 99.91%
        - ✅ **Chính xác cao**: Học từ 4 năm dữ liệu thực tế
        - ✅ Phản ánh đúng: Giờ cao điểm, thấp điểm
        - ✅ Có mùa (seasonal): Mùa hè, đông khác nhau
        
        #### 2️⃣ Ước tính Thiết bị (Device-based Estimation)
        - 📊 Dựa trên nghiên cứu thực tế của EVN
        - 🔌 Tính toán từng thiết bị cụ thể
        - 🏠 Điều chỉnh theo đặc điểm hộ gia đình
        
        #### 🎯 Kết hợp (Blend)
        
        Hệ thống **tự động cân trọng số** giữa 2 phương pháp:
        
        - Nếu bạn **gần mức trung bình** → Tin **Pattern** nhiều hơn (70%)
        - Nếu bạn **khác biệt** → Tin **Thiết bị** nhiều hơn (60%)
        
        #### ⚙️ Calibration
        
        - Điều chỉnh dựa trên kinh nghiệm thực tế
        - Giảm 10% vì ước tính thường cao hơn
        
        #### 🎯 Confidence (Độ tin cậy)
        
        Cao khi:
        - ✅ Số người: 2-4 (phổ biến)
        - ✅ Diện tích: 40-80m²
        - ✅ Có đủ thiết bị thông dụng
        
        Thấp khi:
        - ⚠️ Số người < 1 hoặc > 6
        - ⚠️ Diện tích < 20m² hoặc > 150m²
        - ⚠️ Thiếu thông tin thiết bị
        
        → **Kết quả cuối cùng**: Prediction ± Margin (dựa trên confidence)
        """)

def render_user_page(username, name):
    render_hero_section(name)

    # Hiển thị disclaimer ngay đầu
    st.info("""
    **💡 Lưu ý quan trọng**
    
    Hệ thống sử dụng **phương pháp kết hợp thông minh**:
    - ✅ Pattern thời gian (chính xác 99.91%)
    - ✅ Ước tính thiết bị (dựa trên nghiên cứu EVN)
    
    Kết quả có **độ tin cậy cao** với hộ gia đình thông thường, nhưng vẫn là **ước tính** chứ không phải đo lường thực tế.
    """)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔮 Dự đoán", 
        "💡 Tiết kiệm",
        "📜 Lịch sử",
        "📊 Thống kê"
    ])
    
    # ==================== TAB 1: DỰ ĐOÁN ====================
    with tab1:
        st.markdown("### 🏠 Dự đoán Tiêu thụ Điện")
        
        render_methodology_explanation()

        col_input, col_result = st.columns([1, 1.2])
        
        with col_input:
            with st.container(border=True):

                st.markdown("#### 📋 Thông tin Hộ gia đình")
                
                num_people = st.number_input(
                    "👥 Số người",
                    min_value=1, max_value=10, value=3,
                    help="Số người sinh sống thường xuyên"
                )
                
                area_m2 = st.number_input(
                    "📐 Diện tích (m²)",
                    min_value=20, max_value=300, value=60,
                    help="Tổng diện tích sàn"
                )
                
                house_type = st.selectbox(
                    "🏘️ Loại nhà",
                    ["Chung cư", "Nhà phố", "Biệt thự"],
                    index=1,
                    help="Chung cư: Cách nhiệt tốt, Biệt thự: Diện tích lớn"
                )
            
            with st.container(border=True):
                st.markdown("#### 🔌 Thiết bị Điện")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    num_ac = st.number_input("❄️ Máy lạnh", 0, 5, 1)
                    num_tv = st.number_input("📺 TV", 0, 5, 1)
                    num_fridge = st.number_input("🧊 Tủ lạnh", 0, 3, 1)
                
                with col_b:
                    num_washer = st.number_input("🌀 Máy giặt", 0, 2, 1)
                    num_water_heater = st.number_input("🚿 Bình nóng lạnh", 0, 2, 0)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            predict_btn = st.button(
                "🚀 Dự đoán Thông minh",
                type="primary",
                use_container_width=True
            )
        
        with col_result:
            if predict_btn:
                with st.spinner("🤖 AI đang phân tích..."):
                    time.sleep(1.5)
                    
                    try:
                        predictor = get_predictor()
                        history_df = get_historical_data()
                        
                        # Lấy 1440 điểm gần nhất (24h)
                        input_df = history_df.tail(1440)
                        
                        user_params = {
                            'num_people': num_people,
                            'area_m2': area_m2,
                            'house_type': house_type,
                            'num_ac': num_ac,
                            'num_fridge': num_fridge,
                            'num_tv': num_tv,
                            'num_washer': num_washer,
                            'num_water_heater': num_water_heater
                        }
                        
                        # Dự đoán
                        result = predictor.predict_user_consumption(
                            input_df,
                            user_params,
                            days=30
                        )
                        
                        total_kwh = result['total_kwh']
                        total_cost, cost_breakdown = calculate_evn_bill(total_kwh)
                        
                        # Lưu session
                        st.session_state['prediction_result'] = {
                            'result': result,
                            'user_params': user_params,
                            'total_cost': total_cost,
                            'cost_breakdown': cost_breakdown,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Lưu history
                        save_history(
                            username,
                            input_data=f"{house_type} - {num_people} người - {area_m2}m²",
                            result_kwh=total_kwh,
                            total_cost=total_cost
                        )
                        
                        st.success("✅ Dự đoán hoàn tất!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Lỗi: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
            
            # Hiển thị kết quả
            if 'prediction_result' in st.session_state:
                pred = st.session_state['prediction_result']
                result = pred['result']
                
                # Confidence indicator
                st.markdown("#### 🎯 Độ Tin cậy")
                render_confidence_indicator(result['confidence'])
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # KPI với confidence interval
                st.markdown("#### 📊 Kết quả Dự đoán")
                
                k1, k2 = st.columns(2)
                
                with k1:
                    st.metric(
                        "⚡ Dự đoán chính",
                        f"{result['total_kwh']:.0f} kWh",
                        delta=f"±{(result['upper_bound']-result['total_kwh']):.0f} kWh"
                    )
                    st.caption(f"Khoảng: {result['lower_bound']:.0f} - {result['upper_bound']:.0f} kWh")
                
                with k2:
                    st.metric(
                        "💵 Chi phí dự kiến",
                        f"{pred['total_cost']:,.0f} đ",
                        delta=f"{pred['total_cost']/30:,.0f} đ/ngày"
                    )
                
                # Methodology breakdown
                st.markdown("#### 🔬 Phân tích Phương pháp")
                
                col_m1, col_m2 = st.columns(2)
                
                with col_m1:
                    st.markdown("**⚖️ Trọng số Blend:**")
                    pattern_weight = result['blend_weights']['pattern']
                    device_weight = result['blend_weights']['device']
                    
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=['Pattern (Time)', 'Device (Estimate)'],
                        values=[pattern_weight, device_weight],
                        marker_colors=['#3b82f6', '#f59e0b'],
                        hole=.4
                    )])
                    fig_pie.update_layout(
                        height=250,
                        showlegend=True,
                        margin=dict(t=20, b=20, l=20, r=20)
                    )
                    st.plotly_chart(fig_pie, width='stretch')
                
                with col_m2:
                    st.markdown("**📊 So sánh 2 Phương pháp:**")
                    
                    comparison_df = pd.DataFrame({
                        'Phương pháp': ['Pattern (Time)', 'Device (Estimate)', 'Kết quả (Blend)'],
                        'kWh': [
                            result['baseline_kwh'],
                            result['device_kwh'],
                            result['total_kwh']
                        ]
                    })
                    
                    fig_bar = go.Figure(data=[
                        go.Bar(
                            x=comparison_df['Phương pháp'],
                            y=comparison_df['kWh'],
                            text=comparison_df['kWh'].apply(lambda x: f'{x:.0f}'),
                            textposition='auto',
                            marker_color=['#3b82f6', '#f59e0b', '#10b981']
                        )
                    ])
                    fig_bar.update_layout(
                        height=250,
                        showlegend=False,
                        yaxis_title='kWh/tháng',
                        margin=dict(t=20, b=20, l=20, r=20)
                    )
                    st.plotly_chart(fig_bar, width='stretch')
                
                # Device breakdown
                st.markdown("#### 🔌 Phân bố Thiết bị")
                
                device_kwh = result['adjustment_details']['device_kwh']
                
                if device_kwh:
                    # Tạo dataframe
                    device_df = pd.DataFrame([
                        {
                            'Thiết bị': name.replace('_', ' ').title(),
                            'kWh': kwh,
                            'Tỷ lệ': f"{(kwh/result['total_kwh']*100):.1f}%"
                        }
                        for name, kwh in sorted(device_kwh.items(), key=lambda x: x[1], reverse=True)
                    ])
                    
                    fig_device = px.bar(
                        device_df,
                        x='Thiết bị',
                        y='kWh',
                        text='Tỷ lệ',
                        color='kWh',
                        color_continuous_scale='Blues'
                    )
                    fig_device.update_layout(
                        height=300,
                        showlegend=False,
                        xaxis_title='',
                        yaxis_title='kWh/tháng'
                    )
                    st.plotly_chart(fig_device, width='stretch')
                
                # Pattern theo giờ
                st.markdown("#### 📈 Pattern Tiêu thụ trong Ngày")
                
                hourly_pattern = result['hourly_pattern']
                
                fig_pattern = go.Figure()
                
                fig_pattern.add_trace(go.Scatter(
                    x=list(range(24)),
                    y=hourly_pattern,
                    mode='lines+markers',
                    name='kWh/giờ',
                    line=dict(color='#3b82f6', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(59, 130, 246, 0.1)'
                ))
                
                # Peak hours
                peak_hours = result['peak_hours']
                if peak_hours:
                    fig_pattern.add_trace(go.Scatter(
                        x=peak_hours,
                        y=[hourly_pattern[h] for h in peak_hours],
                        mode='markers',
                        name='Cao điểm',
                        marker=dict(color='red', size=12, symbol='star')
                    ))
                
                fig_pattern.update_layout(
                    height=350,
                    xaxis_title="Giờ trong ngày",
                    yaxis_title="kWh",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_pattern, width='stretch')
                
                # Chi tiết EVN
                with st.expander("💰 Chi tiết Bậc thang EVN"):
                    for line in pred['cost_breakdown']:
                        st.text(line)
                
            else:
                st.info("""
                👈 **Hướng dẫn:**
                
                1. Nhập thông tin hộ gia đình
                2. Nhập thiết bị điện
                3. Bấm "Dự đoán Thông minh"
                
                💡 Hệ thống sẽ:
                - Phân tích pattern thời gian (chính xác)
                - Ước tính từ thiết bị (dựa EVN)
                - Kết hợp thông minh với trọng số tự động
                - Hiển thị độ tin cậy và khoảng dự đoán
                """)
    
    # ==================== TAB 2: TIẾT KIỆM ====================
    with tab2:
        st.markdown("### 💡 Đề xuất Tiết kiệm")
        
        if 'prediction_result' not in st.session_state:
            st.warning("⚠️ Vui lòng dự đoán trước!")
        else:
            pred = st.session_state['prediction_result']
            result = pred['result']
            user_params = pred['user_params']
            
            predictor = get_predictor()
            recommendations = predictor.get_saving_recommendations(result, user_params)

            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### 📋 Danh sách Đề xuất")
                for rec in recommendations:
                    priority_colors = {
                        'high': '🔴 CAO',
                        'medium': '🟡 TRUNG BÌNH',
                        'low': '🟢 THẤP'
                    }
                    
                    with st.container(border=True):
                        st.markdown(f"### {priority_colors.get(rec['priority'], '')} {rec['device']}")

                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.caption("**Hiện tại:**")
                            st.write(rec['current'])
                        with col_b:
                            st.caption("**Tiết kiệm:**")
                            st.write(rec['saving'])
                        
                        st.markdown("**🎯 Hành động:**")
                        for action in rec['actions']:
                            st.markdown(f"- {action}")
            
            with col2:
                st.markdown("#### 💰 Tổng Tiết kiệm")
                
                total_kwh = result['total_kwh']
                saving_kwh = total_kwh * 0.2  # Tiết kiệm 20% với đầy đủ biện pháp
                saving_money = saving_kwh * 2500
                
                with st.container(border=True):
                    st.metric(
                        "Tiết kiệm/tháng",
                        f"{saving_money:,.0f} đ",
                        delta=f"-{saving_kwh:.0f} kWh"
                    )
                    
                    st.metric(
                        "Tiết kiệm/năm",
                        f"{saving_money*12:,.0f} đ"
                    )
                    
                    st.caption("*Nếu áp dụng đầy đủ*")
                
                # Chart
                current = total_kwh
                after = total_kwh - saving_kwh
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=['Hiện tại', 'Sau tiết kiệm'],
                    y=[current, after],
                    text=[f'{current:.0f}', f'{after:.0f}'],
                    textposition='auto',
                    marker_color=['#ef4444', '#22c55e']
                ))
                fig.update_layout(
                    height=300,
                    showlegend=False,
                    yaxis_title='kWh/tháng'
                )
                st.plotly_chart(fig, width='stretch')
    
    # ==================== TAB 3: LỊCH SỬ ====================

    with tab3:
        st.markdown("### 📜 Lịch sử Dự đoán")
        
        history = load_history(username)
        
        if history:
            df = pd.DataFrame(history)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Số lần", len(history))
            with col2:
                st.metric("TB kWh", f"{df['kwh'].mean():.0f}")
            with col3:
                st.metric("TB Chi phí", f"{df['cost'].mean():,.0f} đ")
            
            st.dataframe(df, width='stretch', hide_index=True)
            
            if len(history) > 1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=list(range(1, len(history)+1)),
                    y=df['kwh'],
                    mode='lines+markers'
                ))
                fig.update_layout(
                    title="Xu hướng",
                    xaxis_title="Lần",
                    yaxis_title="kWh",
                    height=300
                )
                st.plotly_chart(fig, width='stretch')
        else:
            st.info("Chưa có lịch sử")
    
    # ==================== TAB 4: THỐNG KÊ ====================
    with tab4:
        st.markdown("### 📊 Thống kê")
        
        if 'prediction_result' in st.session_state:
            pred = st.session_state['prediction_result']
            result = pred['result']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎯 Đánh giá")
                
                kwh = result['total_kwh']
                confidence = result['confidence']

                
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
                # Điều chỉnh score theo confidence
                adjusted_score = score * confidence
                
                st.progress(adjusted_score / 100)
                st.markdown(f"### {rank}")
                st.caption(f"Điểm: {adjusted_score:.0f}/100")
                st.caption(f"(Có tính độ tin cậy: {confidence*100:.0f}%)")
            
            with col2:
                st.markdown("#### 🌍 So sánh")
                
                avg = 250
                diff = kwh - avg
                diff_pct = (diff / avg) * 100
                
                if diff > 0:
                    st.error(f"Cao hơn {diff_pct:.0f}% 📈")
                else:
                    st.success(f"Thấp hơn {abs(diff_pct):.0f}% 📉")
                
                st.metric("Hộ TB", f"{avg} kWh")
                st.metric("Bạn", f"{kwh:.0f} kWh")
        else:
            st.info("Thực hiện dự đoán để xem thống kê!")