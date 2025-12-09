import google.generativeai as genai
import streamlit as st

GOOGLE_API_KEY = "AIzaSyA9KbCCUBWqMbTnA2V0kLuvTyaHLHZA3YY" 

def ask_gemini(question):
    """
    Gửi câu hỏi lên Google Gemini và nhận câu trả lời
    """
    if GOOGLE_API_KEY == "AIzaSyA9KbCCUBWqMbTnA2V0kLuvTyaHLHZA3YY" or not GOOGLE_API_KEY:
        return "⚠️ Hệ thống chưa có API Key. Vui lòng mở file `src/backend/ai_engine.py` và dán Google API Key vào dòng 7 để kích hoạt trí tuệ nhân tạo."

    try:
        # 2. Cấu hình
        genai.configure(api_key=GOOGLE_API_KEY)
        
        system_instruction = """
        Bạn là Trợ lý Năng lượng Thông minh (Smart Energy AI).
        Nhiệm vụ của bạn là giúp người dùng tiết kiệm điện, giải thích các khái niệm điện năng, 
        và phân tích thói quen sử dụng điện.
        - Hãy trả lời ngắn gọn, súc tích, thân thiện.
        - Nếu câu hỏi không liên quan đến điện/năng lượng, hãy khéo léo lái về chủ đề tiết kiệm điện.
        - Luôn dùng tiếng Việt.
        """
        
        model = genai.GenerativeModel('gemini-pro')
        
        # 4. Gửi yêu cầu (Kết hợp ngữ cảnh + câu hỏi user)
        full_prompt = f"{system_instruction}\n\nNgười dùng hỏi: {question}"
        response = model.generate_content(full_prompt)
        
        return response.text

    except Exception as e:
        return f"❌ Lỗi kết nối AI: {str(e)}. Vui lòng kiểm tra lại mạng hoặc API Key."