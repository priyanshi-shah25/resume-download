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


def email_matches_keyword(msg: Message, keyword: str, attachment_filenames=None) -> bool:
    """
    True if any configured keyword/phrase appears in the subject, body,
    or (if provided) any attachment filename.

    attachment_filenames: optional list of decoded attachment filenames,
    e.g. ["priyanshi_ResUMe.pdf"]. Matching is case-insensitive substring
    matching, same as subject/body.
    """
    subject = decode_str(msg["Subject"]).lower()
    body = get_email_body(msg).lower()

    if not keyword:
        return False

    keywords = [part.strip().lower() for part in str(keyword).split(",") if part.strip()]
    if not keywords:
        return False

    if any(k in subject or k in body for k in keywords):
        return True

    if attachment_filenames:
        filenames_lower = [f.lower() for f in attachment_filenames if f]
        if any(k in fname for k in keywords for fname in filenames_lower):
            return True

    return False


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