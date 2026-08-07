import google.generativeai as genai
import os

GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

def generate_email_report(email_data, api_key):
    """Gửi email sang Gemini để phân tích và lập báo cáo"""
    genai.configure(api_key=api_key)
    
    prompt = f"""
Bạn là trợ lý AI phân tích Email hỗ trợ hệ thống Pythaverse.
Hãy đọc nội dung Email dưới đây và lập BÁO CÁO PHÂN TÍCH ngắn gọn.

--- THÔNG TIN EMAIL ---
Người gửi: {email_data['sender']}
Tiêu đề: {email_data['subject']}
Thời gian: {email_data['date']}
Nội dung:
{email_data['body']}

--- YÊU CẦU ĐẦU RA ---
Hãy trả về định dạng Báo cáo ngắn gọn bao gồm:
1. 📌 **Phân loại**: (Chọn 1: Lỗi Kỹ Thuật System / Yêu cầu Cấp License / Reset Password / Thắc mắc / Khác)
2. ⚠️ **Độ ưu tiên**: (Cao / Trung bình / Thấp)
3. 📝 **Tóm tắt vấn đề**: (Nêu trong 2-3 câu ngắn gọn)
4. 💡 **Đề xuất hành động**: (Cần làm gì tiếp theo)
"""

    for model_name in GEMINI_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"⚠️ Model {model_name} gặp lỗi hoặc hết Quota: {e}. Đang chuyển model tiếp theo...")
            continue

    return "❌ Lỗi: Tất cả model Gemini đều không phản hồi."
