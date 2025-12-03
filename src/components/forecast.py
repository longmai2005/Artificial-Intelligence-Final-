import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_forecast(predictor, history_df, current_time):
    st.subheader("📈 Dự báo Phụ tải (AI Prediction)")
    
    # Lấy dữ liệu 24h quá khứ
    past_24h = history_df.loc[current_time - pd.Timedelta(hours=24):current_time]
    
    if len(past_24h) < 24:
        st.warning("Chưa đủ dữ liệu lịch sử để dự báo.")
        return

    # Dự báo tương lai
    input_data = past_24h['Global_active_power'].values
    forecast_vals = predictor.predict_next_24h(input_data)
    
    # Tạo trục thời gian tương lai
    future_time = [current_time + pd.Timedelta(hours=i) for i in range(1, 25)]
    
    # Vẽ biểu đồ
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=past_24h.index, y=past_24h['Global_active_power'], name="Quá khứ", line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=future_time, y=forecast_vals, name="Dự báo (AI)", line=dict(color='orange', dash='dash')))
    
    fig.update_layout(title="Biểu đồ phụ tải: Thực tế vs Dự báo", xaxis_title="Thời gian", yaxis_title="Công suất (kW)")
    st.plotly_chart(fig, use_container_width=True)