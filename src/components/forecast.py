import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_forecast(predictor, history_df, current_time):
    st.subheader("📈 Dự báo Phụ tải (AI Prediction)")
    
    # 1. Lấy dữ liệu 24h quá khứ (Dùng pd.Timedelta để xác định phạm vi)
    # Chúng ta lấy từ (current_time - 23h) đến current_time để có đủ 24 điểm dữ liệu
    past_24h = history_df.loc[current_time - pd.Timedelta(hours=23):current_time]
    
    # Kiểm tra điều kiện đủ dữ liệu để dự báo
    if len(past_24h) < 20:
        st.warning("Chưa đủ dữ liệu lịch sử (cần ít nhất 24 giờ) để AI dự báo chính xác.")
        return
    
    # 2. Chuẩn bị dữ liệu đầu vào (Input data)
    # Lấy chính xác 24 giá trị 'Global_active_power' gần nhất
    input_data = past_24h['Global_active_power'].values[-24:] 
    
    # 3. Thực hiện dự báo thông qua Predictor (Chỉ gọi 1 lần duy nhất)
    # Sử dụng spinner để thông báo cho người dùng khi AI đang xử lý
    with st.spinner('AI đang tính toán dựa trên mô hình RandomForest...'):
        forecast_vals = predictor.predict_next_24h(input_data)
        
    # 4. Tạo trục thời gian cho 24 giờ tiếp theo trong tương lai
    future_time = [current_time + pd.Timedelta(hours=i) for i in range(1, 25)]
    
    # 5. Vẽ biểu đồ so sánh Thực tế (Quá khứ) và Dự báo (Tương lai)
    fig = go.Figure()
    
    # Đường dữ liệu thực tế trong quá khứ
    fig.add_trace(go.Scatter(
        x=past_24h.index, 
        y=past_24h['Global_active_power'], 
        name="Quá khứ (Thực tế)", 
        line=dict(color='blue')
    ))
    
    # Đường dữ liệu dự báo bởi AI
    fig.add_trace(go.Scatter(
        x=future_time, 
        y=forecast_vals, 
        name="Dự báo (AI RandomForest)", 
        line=dict(color='orange', dash='dash')
    ))
    
    # Cấu hình giao diện biểu đồ
    fig.update_layout(
        title="Biểu đồ phụ tải: Thực tế vs Dự báo (Mô hình ML)",
        xaxis_title="Thời gian",
        yaxis_title="Công suất (kW)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, width='stretch')