"""
Core, side-effect-free logic for parsing emails and deciding what to save.

Keeping this logic separate from imaplib I/O (see imap_client.py) means it
can be unit tested without a real mailbox or network connection.
"""
from email.header import decode_header
from email.message import Message


def decode_str(value: str) -> str:
    """Safely decode an email header value (subject, filename, etc.)."""
    if not value:
        return ""
    decoded, encoding = decode_header(value)[0]
    if isinstance(decoded, bytes):
        decoded = decoded.decode(encoding or "utf-8", errors="ignore")
    return decoded


def get_email_body(msg: Message) -> str:
    """Extract plain-text body from an email message (handles multipart)."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition") or "")
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode(
                            part.get_content_charset() or "utf-8", errors="ignore"
                        )
                except Exception:
                    pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(
                    msg.get_content_charset() or "utf-8", errors="ignore"
                )
        except Exception:
            pass
    return body


def email_matches_keyword(msg: Message, keyword: str) -> bool:
    """True if `keyword` appears in the subject or body (case-insensitive)."""
    subject = decode_str(msg["Subject"]).lower()
    body = get_email_body(msg).lower()
    keyword = keyword.lower()
    return keyword in subject or keyword in body


def is_allowed_attachment(filename: str, allowed_extensions: tuple) -> bool:
    """True if filename ends with one of the allowed extensions."""
    if not filename:
        return False
    return filename.lower().endswith(tuple(ext.lower() for ext in allowed_extensions))


def extract_attachments(msg: Message, allowed_extensions: tuple):
    """
    Return a list of (decoded_filename, raw_bytes) for every attachment in
    `msg` whose filename matches `allowed_extensions`.
    """
    results = []
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        if part.get("Content-Disposition") is None:
            continue

        filename = part.get_filename()
        if not filename:
            continue

        decoded_filename = decode_str(filename)
        if not is_allowed_attachment(decoded_filename, allowed_extensions):
            continue

        payload = part.get_payload(decode=True)
        if payload is None:
            continue

        results.append((decoded_filename, payload))

    return results
