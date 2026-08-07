import time
import os
from dotenv import load_dotenv
from email_reader import fetch_unread_emails, save_processed_id
from ai_reporter import generate_email_report

load_dotenv()

IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")  # Với Gmail: Dùng App Password (Mật khẩu ứng dụng)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_SECONDS", "300")) # Quét mỗi 5 phút

def run_pipeline():
    print("\n🔍 Đang quét Email chưa đọc...")
    emails = fetch_unread_emails(IMAP_SERVER, EMAIL_USER, EMAIL_PASS)

    if not emails:
        print("✅ Không có Email mới chưa đọc.")
        return

    print(f"📩 Phát hiện {len(emails)} email mới!")

    for item in emails:
        print(f"\n--- Đang xử lý Email: {item['subject']} ---")
        
        # 1. Gọi Gemini lập báo cáo
        report = generate_email_report(item, GEMINI_API_KEY)

        # 2. In báo cáo ra Console (Sau này sẽ nối sang Telegram Bot)
        print("\n=== BÁO CÁO TẠO BỞI GEMINI AI ===")
        print(report)
        print("==================================")

        # 3. Lưu lại ID đã xử lý thành công để tránh tốn Quota lần sau!
        save_processed_id(item["msg_id"])

if __name__ == "__main__":
    print("🚀 Bắt đầu chương trình thử nghiệm Email Agent...")
    while True:
        try:
            run_pipeline()
        except Exception as e:
            print(f"❌ Lỗi Pipeline: {e}")
        
        print(f"💤 Tạm nghỉ {CHECK_INTERVAL} giây trước lần quét tiếp theo...")
        time.sleep(CHECK_INTERVAL)
