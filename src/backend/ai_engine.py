import google.generativeai as genai
import streamlit as st
import os

def get_api_key():
    # Ưu tiên lấy từ secrets.toml
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return os.getenv("GEMINI_API_KEY")

def ask_gemini(question):
    api_key = get_api_key()
    if not api_key:
        return "⚠️ Chưa có API Key. Kiểm tra .streamlit/secrets.toml"

    try:
        genai.configure(api_key=api_key)
        
        system_instruction = "Bạn là Trợ lý Năng lượng. Trả lời ngắn gọn, tập trung vào tiết kiệm điện."
        full_prompt = f"{system_instruction}\n\nUser: {question}"

        # --- DANH SÁCH MODEL CẬP NHẬT TỪ TÀI KHOẢN CỦA BẠN ---
        # Hệ thống sẽ thử lần lượt từ trên xuống dưới
        candidate_models = [
            'models/gemini-2.0-flash',       # Ưu tiên số 1: Nhanh, thông minh, bản 2.0
            'models/gemini-2.5-flash',       # Ưu tiên số 2: Bản 2.5 mới hơn
            'models/gemini-flash-latest',    # Alias luôn trỏ về bản Flash mới nhất
            'models/gemini-2.0-flash-lite',  # Bản nhẹ, siêu tốc độ
            'models/gemini-pro-latest'       # Fallback cuối cùng
        ]
        
        last_error = ""
        
        for model_name in candidate_models:
            try:
                # Khởi tạo model với tên chính xác từ danh sách bạn cung cấp
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(full_prompt)
                return response.text 
            except Exception as e:
                # Nếu model này lỗi, thử model kế tiếp
                last_error = str(e)
                continue
        
        return f"❌ Không thể kết nối. Lỗi cuối cùng: {last_error}"

    except Exception as e:
        return f"❌ Lỗi hệ thống AI: {str(e)}"