import imaplib
import email
from email.header import decode_header
import json
import os

PROCESSED_FILE = "processed_ids.json"

def load_processed_ids():
    """Tải danh sách email ID đã xử lý từ file json"""
    if os.path.exists(PROCESSED_FILE):
        try:
            with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_processed_id(msg_id):
    """Lưu ID email đã xử lý thành công"""
    processed = load_processed_ids()
    processed.add(msg_id)
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dumps(list(processed), f, ensure_ascii=False, indent=2)

def clean_text(header_val):
    """Decode tiêu đề hoặc người gửi email"""
    if not header_val:
        return ""
    decoded_list = decode_header(header_val)
    header_str = ""
    for bytes_or_str, encoding in decoded_list:
        if isinstance(bytes_or_str, bytes):
            header_str += bytes_or_str.decode(encoding or "utf-8", errors="ignore")
        else:
            header_str += str(bytes_or_str)
    return header_str

def fetch_unread_emails(imap_server, email_user, email_pass):
    """Kết nối IMAP và lấy danh sách email chưa đọc (UNSEEN) chưa từng xử lý"""
    processed_ids = load_processed_ids()
    unread_emails = []

    try:
        # Kết nối IMAP (SSL)
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select("INBOX")

        # Tìm các email chưa đọc (UNSEEN)
        status, messages = mail.search(None, 'UNSEEN')
        if status != 'OK' or not messages[0]:
            mail.logout()
            return []

        email_ids = messages[0].split()
        
        for e_id in email_ids:
            # Lấy thông tin Header
            status, msg_data = mail.fetch(e_id, '(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID SUBJECT FROM DATE)])')
            if status != 'OK':
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    msg_id = msg.get("Message-ID", "").strip()

                    # Nếu ID này đã xử lý trước đó rồi -> Bỏ qua ngay lập tức để tiết kiệm Quota!
                    if msg_id in processed_ids:
                        continue

                    # Nếu là email mới hoàn toàn -> Lấy toàn bộ Nội dung (Body)
                    _, full_msg_data = mail.fetch(e_id, '(RFC822)')
                    full_msg = email.message_from_bytes(full_msg_data[0][1])

                    subject = clean_text(full_msg.get("Subject"))
                    sender = clean_text(full_msg.get("From"))
                    date_str = full_msg.get("Date")

                    # Trích xuất nội dung Text thô
                    body = ""
                    if full_msg.is_multipart():
                        for part in full_msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
                                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                break
                    else:
                        body = full_msg.get_payload(decode=True).decode('utf-8', errors='ignore')

                    unread_emails.append({
                        "msg_id": msg_id,
                        "sender": sender,
                        "subject": subject,
                        "date": date_str,
                        "body": body[:3000] # Giới hạn 3000 ký tự tránh quá dài
                    })

        mail.logout()
    except Exception as e:
        print(f"❌ Lỗi đọc Email IMAP: {e}")

    return unread_emails
