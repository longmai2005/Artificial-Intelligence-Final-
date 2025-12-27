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

# Import module
from src.backend.history import save_history, load_history
from src.backend.logic_engine import calculate_evn_bill
from src.backend.predictor import EnergyPredictor
from src.backend.data_loader import load_dataset
from src.utils.style import render_hero_section

@st.cache_resource(show_spinner=False)
def get_predictor():
    return EnergyPredictor()

@st.cache_data(show_spinner=False)
def get_historical_data():
    """Load dữ liệu lịch sử - lấy sample lớn hơn để có pattern tốt"""
    # 200k điểm ≈ 138 ngày
    return load_dataset(nrows=200000)


def render_confidence_indicator(confidence):
    """Hiển thị độ tin cậy bằng color-coded badge"""
    if confidence >= 0.7:
        color_icon, text, bg_color, border_color, text_color = "🟢", "CAO", "#d4edda", "#c3e6cb", "#155724"
    elif confidence >= 0.5:
        color_icon, text, bg_color, border_color, text_color = "🟡", "TRUNG BÌNH", "#fff3cd", "#ffeeba", "#856404"
    else:
        color_icon, text, bg_color, border_color, text_color = "🔴", "THẤP", "#f8d7da", "#f5c6cb", "#721c24"
    
    st.markdown(f"""
    <div style="background-color: {bg_color}; border: 1px solid {border_color}; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <strong style="color: {text_color}; font-size: 16px;">{color_icon} Độ tin cậy: {text}</strong><br>
        <span style="font-size: 32px; font-weight: 800; color: {text_color};">{confidence*100:.0f}%</span>
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
        
        #### 2️⃣ Ước tính Thiết bị (Device-based Estimation)
        - 📊 Dựa trên nghiên cứu thực tế của EVN
        - 🏠 Điều chỉnh theo đặc điểm hộ gia đình
        
        #### 🎯 Kết hợp & Calibration
        - Hệ thống **tự động cân trọng số** giữa 2 phương pháp.
        - Điều chỉnh (Calibrate) giảm 10% để sát thực tế hơn.
        
        → **Kết quả cuối cùng**: Prediction ± Margin (dựa trên confidence)
        """)

def render_user_page(username, name):
    render_hero_section(name)

    st.info("""
    **💡 Lưu ý quan trọng:** Hệ thống sử dụng **phương pháp kết hợp thông minh** (AI Pattern + Ước tính thiết bị).
    Kết quả có **độ tin cậy cao** nhưng vẫn là ước tính tham khảo.
    """)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔮 Dự đoán", "💡 Tiết kiệm", "📜 Lịch sử", "📊 Thống kê"])
    
    # ==================== TAB 1: DỰ ĐOÁN ====================
    with tab1:
        st.markdown("### 🏠 Dự đoán Tiêu thụ Điện")
        render_methodology_explanation()

        col_input, col_result = st.columns([1, 1.2])
        
        with col_input:
            with st.container(border=True):
                st.markdown("#### 📋 Thông tin Hộ gia đình")
                num_people = st.number_input("👥 Số người", 1, 10, 3, help="Số người sinh sống thường xuyên")
                area_m2 = st.number_input("📐 Diện tích (m²)", 20, 300, 60, help="Tổng diện tích sàn")
                house_type = st.selectbox("🏘️ Loại nhà", ["Chung cư", "Nhà phố", "Biệt thự"], index=1)
            
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
            
            # Button (Sửa lại cú pháp cho an toàn)
            try:
                predict_btn = st.button("🚀 Dự đoán Thông minh", type="primary", width='stretch')
            except TypeError:
                predict_btn = st.button("🚀 Dự đoán Thông minh", type="primary")
        
        with col_result:
            if predict_btn:
                with st.spinner("🤖 AI đang phân tích..."):
                    time.sleep(1.0)
                    try:
                        predictor = get_predictor()
                        history_df = get_historical_data()
                        input_df = history_df.tail(1440) # Lấy 24h gần nhất
                        
                        user_params = {
                            'num_people': num_people, 'area_m2': area_m2, 'house_type': house_type,
                            'num_ac': num_ac, 'num_fridge': num_fridge, 'num_tv': num_tv,
                            'num_washer': num_washer, 'num_water_heater': num_water_heater
                        }
                        
                        # Dự đoán
                        result = predictor.predict_user_consumption(input_df, user_params, days=30)
                        
                        total_kwh = result['total_kwh']
                        total_cost, cost_breakdown = calculate_evn_bill(total_kwh)
                        
                        # Lưu session
                        st.session_state['prediction_result'] = {
                            'result': result, 'user_params': user_params,
                            'total_cost': total_cost, 'cost_breakdown': cost_breakdown,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Lưu history
                        save_history(username, f"{house_type} - {num_people} người - {area_m2}m²", total_kwh, total_cost)
                        
                        st.success("✅ Dự đoán hoàn tất!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Lỗi: {str(e)}")
            
            # Hiển thị kết quả
            if 'prediction_result' in st.session_state:
                pred = st.session_state['prediction_result']
                result = pred['result']
                
                # Confidence
                st.markdown("#### 🎯 Độ Tin cậy")
                render_confidence_indicator(result['confidence'])
                st.markdown("<br>", unsafe_allow_html=True)
                
                # KPI
                st.markdown("#### 📊 Kết quả Dự đoán")
                k1, k2 = st.columns(2)
                with k1:
                    st.metric("⚡ Dự đoán chính", f"{result['total_kwh']:.0f} kWh", 
                            delta=f"±{(result['upper_bound']-result['total_kwh']):.0f} kWh")
                    st.caption(f"Khoảng: {result['lower_bound']:.0f} - {result['upper_bound']:.0f} kWh")
                with k2:
                    st.metric("💵 Chi phí dự kiến", f"{pred['total_cost']:,.0f} đ", 
                            delta=f"{pred['total_cost']/30:,.0f} đ/ngày")
                
                # Device breakdown
                st.markdown("#### 🔌 Phân bố Thiết bị")
                # Xử lý lấy data an toàn hơn
                device_kwh_dict = result.get('adjustment_details', {}).get('device_kwh', {})
                if not device_kwh_dict:
                    # Fallback nếu key khác
                    device_kwh_dict = result.get('device_breakdown', {})
                
                if device_kwh_dict:
                    device_df = pd.DataFrame([
                        {'Thiết bị': k, 'kWh': v, 'Tỷ lệ': f"{(v/result['total_kwh']*100):.1f}%"}
                        for k, v in sorted(device_kwh_dict.items(), key=lambda x: x[1], reverse=True)
                    ])
                    
                    fig_device = px.bar(device_df, x='Thiết bị', y='kWh', text='Tỷ lệ', color='kWh', color_continuous_scale='Viridis')
                    fig_device.update_layout(height=350, showlegend=False, xaxis_title='', yaxis_title='kWh/tháng', margin=dict(t=20, b=20, l=20, r=20))
                    st.plotly_chart(fig_device, width='stretch')
                                
                # Chi tiết EVN
                with st.expander("💰 Chi tiết Bậc thang EVN"):
                    for line in pred['cost_breakdown']:
                        st.text(line)
                
            else:
                st.info("👈 Vui lòng nhập thông tin và bấm nút Dự đoán.")
    
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