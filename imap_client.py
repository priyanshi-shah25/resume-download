"""
Thin IMAP I/O layer. Kept separate from email_logic.py so the parsing/
filtering rules can be unit tested without a real network connection.
"""
import email
import imaplib
import os

import config
from email_logic import email_matches_keyword, extract_attachments, decode_str


def connect():
    """Log in and select the inbox. Raises imaplib.IMAP4.error on failure."""
    if not config.EMAIL_ACCOUNT or not config.EMAIL_APP_PASSWORD:
        raise RuntimeError(
            "EMAIL_ACCOUNT and EMAIL_APP_PASSWORD must be set as environment "
            "variables (see config.py docstring)."
        )
    mail = imaplib.IMAP4_SSL(config.IMAP_SERVER)
    mail.login(config.EMAIL_ACCOUNT, config.EMAIL_APP_PASSWORD)
    mail.select("inbox")
    return mail


def fetch_unseen_ids(mail):
    status, messages = mail.search(None, "UNSEEN")
    if status != "OK" or not messages[0]:
        return []
    return messages[0].split()


def fetch_message(mail, msg_id):
    res, msg_data = mail.fetch(msg_id, "(RFC822)")
    if res != "OK":
        return None
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            return email.message_from_bytes(response_part[1])
    return None


def save_attachment(filename: str, payload: bytes, save_folder: str) -> str:
    os.makedirs(save_folder, exist_ok=True)
    filepath = os.path.join(save_folder, filename)
    with open(filepath, "wb") as f:
        f.write(payload)
    return filepath


def process_inbox():
    """Main entry point: scan unread mail, save matching attachments."""
    mail = connect()
    try:
        ids = fetch_unseen_ids(mail)
        if not ids:
            print("No unread emails.")
            return

        for msg_id in ids:
            msg = fetch_message(mail, msg_id)
            if msg is None:
                continue

            subject = decode_str(msg["Subject"])
            sender = msg.get("From", "")

            if not email_matches_keyword(msg, config.KEYWORD_FILTER):
                mail.store(msg_id, "+FLAGS", "\\Seen")
                continue

            print(f"Matched email from {sender}: {subject}")
            attachments = extract_attachments(msg, config.ALLOWED_EXTENSIONS)

            if not attachments:
                print("  No matching attachments found.")
            for filename, payload in attachments:
                path = save_attachment(filename, payload, config.SAVE_FOLDER)
                print(f"  Saved: {path}")

            mail.store(msg_id, "+FLAGS", "\\Seen")

    finally:
        mail.close()
        mail.logout()
