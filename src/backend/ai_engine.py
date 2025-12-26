import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv() # Tải các biến từ file .env vào hệ thống
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
def ask_gemini(question):
    """
    Gửi câu hỏi lên Google Gemini và nhận câu trả lời
    """
    if not GOOGLE_API_KEY:
        return "⚠️ Hệ thống chưa có API Key. Vui lòng kiểm tra file `src/backend/ai_engine.py`."

    try:
        # Cấu hình
        genai.configure(api_key=GOOGLE_API_KEY)
        
        system_instruction = """
        Bạn là Trợ lý Năng lượng (Energy AI). 
        Hãy trả lời ngắn gọn, thân thiện bằng tiếng Việt.
        Tập trung vào giải pháp tiết kiệm điện.
        """
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_prompt = f"{system_instruction}\n\nUser: {question}"
        response = model.generate_content(full_prompt)
        
        return response.text

    except Exception as e:
        return f"❌ Lỗi kết nối AI: {str(e)}"