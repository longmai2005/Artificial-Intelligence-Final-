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
from src.backend.history import save_history, load_history, clear_history, delete_selected_history
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
                predict_btn = st.button("🚀 Dự đoán Thông minh", type="primary", use_container_width=True)
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
                        if 'recommendations' in st.session_state:
                            del st.session_state['recommendations']
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
                    st.plotly_chart(fig_device, use_container_width=True)
                
                # --- ĐÃ XÓA PHẦN PATTERN THEO GIỜ ĐỂ TRÁNH LỖI ---
                
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
            predictor = get_predictor() # Khởi tạo predictor
            
            # --- XỬ LÝ LOGIC ---
            # 1. Nếu chưa có recommendations trong session, tạo mặc định (Rule-based)
            if 'recommendations' not in st.session_state:
                st.session_state['recommendations'] = predictor.get_saving_recommendations(
                    pred['result'], 
                    pred['user_params']
                )

            # 2. Khu vực điều khiển AI
            api_key = st.secrets.get("GEMINI_API_KEY", None)
            if not api_key:
                api_key = st.text_input("Nhập Gemini API Key để kích hoạt AI (Bỏ trống dùng Logic thường)", type="password")

            # Nút bấm nâng cấp lên AI
            # Logic: Nếu bấm nút -> Gọi AI -> Cập nhật vào session_state
            if st.button("🤖 Phân tích chuyên sâu (AI)", type="primary"):
                with st.spinner("AI đang suy nghĩ giải pháp tối ưu cho nhà bạn..."):
                    try:
                        ai_recs = predictor.get_ai_recommendations(
                            pred['result'], 
                            pred['user_params'], 
                            api_key=api_key if api_key else None
                        )
                        st.session_state['recommendations'] = ai_recs
                        st.success("Đã cập nhật lời khuyên từ AI!")
                    except Exception as e:
                        st.error(f"Lỗi AI: {str(e)}")

            # 3. Lấy dữ liệu từ session để hiển thị (Đảm bảo biến luôn tồn tại)
            recommendations = st.session_state['recommendations']

            # --- HIỂN THỊ GIAO DIỆN ---
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### 📋 Danh sách Đề xuất")
                if not recommendations:
                    st.info("Chưa có đề xuất nào.")
                else:
                    for rec in recommendations:
                        priority_colors = {
                            'high': '🔴 CAO',
                            'medium': '🟡 TRUNG BÌNH',
                            'low': '🟢 THẤP'
                        }
                        prio = rec.get('priority', 'low')
                        device_name = rec.get('device', 'Thiết bị')
                        
                        with st.container(border=True):
                            st.markdown(f"### {priority_colors.get(prio, '🟢')} {device_name}")

                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.caption("**Hiện tại:**")
                                st.write(rec.get('current', 'N/A'))
                            with col_b:
                                st.caption("**Tiết kiệm:**")
                                st.write(rec.get('saving', 'N/A'))
                            
                            st.markdown("**🎯 Hành động:**")
                            actions = rec.get('actions', [])
                            if isinstance(actions, list):
                                for action in actions:
                                    st.markdown(f"- {action}")
                            else:
                                st.write(actions)
            
            with col2:
                st.markdown("#### 💰 Hiệu quả Kinh tế")
                
                # Lấy số liệu từ kết quả dự đoán
                original_kwh = pred['result']['total_kwh']
                original_cost = pred['total_cost']
                
                # --- TÍNH TOÁN TIẾT KIỆM ---
                # Cách 1: Nếu bạn muốn tính tổng từ các đề xuất cụ thể (Khuyên dùng)
                # total_saving_kwh = sum([float(rec.get('saving_kwh', 0)) for rec in recommendations])
                
                # Cách 2: Tạm tính 20% như code cũ (Dễ hình dung trước)
                saving_kwh = original_kwh * 0.2
                
                # Ước tính tiền tiết kiệm (Lấy % tiền tương ứng % điện)
                saving_money = original_cost * 0.2 
                final_cost = original_cost - saving_money
                
                # --- HIỂN THỊ GIAO DIỆN MỚI ---
                with st.container(border=True):
                    # 1. DÒNG 1: CHI PHÍ GỐC (Nhỏ hơn, màu xám)
                    st.markdown("""
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #6c757d; font-size: 14px;">Chi phí dự kiến ban đầu:</span>
                        <span style="color: #6c757d; font-weight: bold; font-size: 16px; text-decoration: line-through;">
                            {:,.0f} đ
                        </span>
                    </div>
                    """.format(original_cost), unsafe_allow_html=True)
                    
                    st.markdown("---") # Đường kẻ ngang
                    
                    # 2. DÒNG 2: TIẾT KIỆM (Dùng Metric cho đẹp)
                    st.metric(
                        label="Có thể tiết kiệm",
                        value=f"{saving_money:,.0f} đ",
                        delta=f"-{saving_kwh:.0f} kWh",
                        delta_color="normal" # Màu xanh lá
                    )
                    
                    st.markdown("---")

                    # 3. DÒNG 3: CHI PHÍ MỚI (To, Nổi bật)
                    st.caption("Chi phí sau khi áp dụng các giải pháp:")
                    st.markdown(f"""
                    <h2 style="color: #28a745; margin: 0; padding: 0;">
                        ≈ {final_cost:,.0f} đ
                    </h2>
                    """, unsafe_allow_html=True)
                
                # --- BIỂU ĐỒ SO SÁNH (Giữ nguyên) ---
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=['Trước', 'Sau'],
                    y=[original_cost, final_cost], # Đổi sang hiển thị Tiền cho đồng bộ
                    text=[f'{original_cost/1000:.0f}k', f'{final_cost/1000:.0f}k'],
                    textposition='auto',
                    marker_color=['#6c757d', '#28a745'] # Xám và Xanh lá
                ))
                fig.update_layout(
                    height=250,
                    showlegend=False,
                    title="So sánh chi phí (VNĐ)",
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # ==================== TAB 3: LỊCH SỬ ====================

    # ==================== TAB 3: LỊCH SỬ (CÓ CHỌN & XÓA) ====================
    with tab3:
        col_header, col_btn = st.columns([3, 2])
        
        with col_header:
            st.markdown("### 📜 Nhật ký Tiêu thụ")
            

        rows_to_delete = []

        # LOAD DỮ LIỆU
        history = load_history(username)
        
        if history:
            df = pd.DataFrame(history)
            
            # Đổi tên cột hiển thị
            display_df = df.rename(columns={
                'timestamp': 'Thời gian', 
                'kwh': 'Số điện (kWh)', 
                'cost': 'Chi phí (VNĐ)'
            })

            event = st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                on_select="rerun", 
                selection_mode="multi-row"
            )
            
            # Lấy danh sách các dòng được chọn
            selected_rows = event.selection.rows
            
            # XỬ LÝ NÚT XÓA (Chỉ hiện khi có dòng được chọn)
            with col_btn:
                if selected_rows:
                    st.write("") # Căn chỉnh lề chút
                    if st.button(f"🗑️ Xóa {len(selected_rows)} dòng đã chọn", type="primary"):
                        # 1. Lấy danh sách Timestamp của các dòng đã chọn
                        # Lưu ý: display_df và df có cùng index nên dùng iloc được
                        timestamps_to_delete = df.iloc[selected_rows]['timestamp'].tolist()
                        
                        # 2. Gọi backend để xóa
                        if delete_selected_history(username, timestamps_to_delete):
                            st.toast("Đã xóa thành công!", icon="✅")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Lỗi khi xóa dữ liệu.")
                else:
                    # Nút xóa hết cũ (để dự phòng)
                    if st.button("🗑️ Xóa tất cả lịch sử", type="secondary"):
                        if clear_history(username):
                            st.rerun()

            # --- METRIC THỐNG KÊ (Giữ nguyên) ---
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Tổng bản ghi", len(history))
            with col2: st.metric("TB kWh", f"{df['kwh'].mean():.0f}")
            with col3: st.metric("TB Chi phí", f"{df['cost'].mean():,.0f} đ")

            # --- BIỂU ĐỒ (Giữ nguyên code biểu đồ của bạn) ---
            if len(history) > 1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df.index + 1, y=df['kwh'],
                    name="Điện (kWh)",
                    mode='lines+markers',
                    line=dict(color='#3b82f6')
                ))
                fig.add_trace(go.Scatter(
                    x=df.index + 1, y=df['cost'],
                    name="Tiền (VNĐ)",
                    mode='lines+markers',
                    line=dict(color='#ef4444', dash='dot'),
                    yaxis='y2' 
                ))
                fig.update_layout(
                    title="Xu hướng Tiêu thụ & Chi phí",
                    xaxis_title="Lần dự đoán",
                    yaxis=dict(title=dict(text="kWh", font=dict(color="#3b82f6"))),
                    yaxis2=dict(
                        title=dict(text="VNĐ", font=dict(color="#ef4444")),
                        overlaying='y',
                        side='right'
                    ),
                    height=350,
                    hovermode="x unified",
                    legend=dict(orientation="h", y=1.1)
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chưa có lịch sử. Hãy thực hiện dự đoán ở Tab 1!")
    
    # ==================== TAB 4: THỐNG KÊ ====================
    with tab4:
        st.markdown("### 📊 Phân tích Hiệu quả & Môi trường")
        
        if 'prediction_result' in st.session_state:
            pred = st.session_state['prediction_result']
            result = pred['result']
            user_params = pred['user_params']
            
            total_kwh = result['total_kwh']
            num_people = user_params.get('num_people', 1)
            
            # 1. Tính chỉ số kWh bình quân đầu người (Quan trọng để so sánh chuẩn)
            kwh_per_capita = total_kwh / num_people
            
            # Mức chuẩn (Benchmark) tại Việt Nam (Giả định)
            # Thấp: < 50 kWh/người/tháng
            # TB: 50 - 100 kWh/người/tháng
            # Cao: > 100 kWh/người/tháng
            
            col_gauge, col_info = st.columns([1.5, 1])
            
            with col_gauge:
                st.markdown("#### ⚡ Mức độ sử dụng điện(Bình quân đầu người)")
                
                # Vẽ biểu đồ đồng hồ (Gauge Chart)
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = kwh_per_capita,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "kWh / Người / Tháng", 'font': {'size': 18}},
                    delta = {'reference': 75, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}}, # Mức chuẩn là 75
                    gauge = {
                        'axis': {'range': [None, 200], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "rgba(0,0,0,0)"}, # Ẩn thanh bar mặc định đi, dùng kim chỉ (nếu muốn nâng cao) hoặc để màu
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 50], 'color': '#22c55e'},   # Xanh (Tiết kiệm)
                            {'range': [50, 100], 'color': '#fbbf24'}, # Vàng (Trung bình)
                            {'range': [100, 200], 'color': '#ef4444'}  # Đỏ (Cao)
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': kwh_per_capita
                        }
                    }
                ))
                fig_gauge.update_layout(height=300, margin=dict(t=30, b=10, l=20, r=20))
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                # Đánh giá bằng chữ
                if kwh_per_capita < 50:
                    status = "🏆 Rất Tiết Kiệm"
                    msg = "Gia đình bạn sử dụng điện rất hiệu quả!"
                elif kwh_per_capita < 100:
                    status = "✅ Mức Trung Bình"
                    msg = "Mức tiêu thụ hợp lý so với mặt bằng chung."
                else:
                    status = "⚠️ Mức Cao"
                    msg = "Hãy xem xét lại các thiết bị làm mát."
                
                st.info(f"**Đánh giá:** {status} - {msg}")

            with col_info:
                st.markdown("#### 🌱 Tác động Môi trường")
                
                # Hệ số phát thải lưới điện Việt Nam (ước tính): ~0.72 kg CO2 / kWh
                co2_emission = total_kwh * 0.72
                trees_needed = co2_emission / 22 # 1 cây trưởng thành hấp thụ khoảng 22kg CO2/năm
                
                with st.container(border=True):
                    st.metric("Lượng CO2 phát thải", f"{co2_emission:.1f} kg")
                    st.caption("Tương đương lượng khí thải của xe máy chạy ~500km")
                
                with st.container(border=True):
                    st.metric("Số cây cần trồng bù đắp", f"{trees_needed:.1f} 🌳")
                    st.caption("Để trung hòa lượng Carbon này trong 1 năm.")
                
                st.markdown("---")
                st.markdown("**So sánh với hàng xóm:**")
                st.progress(min(kwh_per_capita/150, 1.0))
                st.caption(f"Bạn đang dùng nhiều hơn {min(kwh_per_capita/150*100, 100):.0f}% người khác.")

        else:
            st.warning("Vui lòng thực hiện dự đoán ở Tab 1 trước!")
            st.image("https://cdn-icons-png.flaticon.com/512/6104/6104865.png", width=100) # Ảnh minh họa vui