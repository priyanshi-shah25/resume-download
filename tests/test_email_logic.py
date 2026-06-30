"""
Tests for email_logic.py — no network or mailbox required.

Run with:
    pytest tests/test_email_logic.py -v
"""
import sys
import os
import unittest
from email.message import EmailMessage

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from email_logic import (
    decode_str,
    get_email_body,
    email_matches_keyword,
    is_allowed_attachment,
    extract_attachments,
)


def make_email(subject="", body="", attachments=None):
    """Build a real EmailMessage with optional attachments for testing."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "sender@example.com"
    msg.set_content(body)

    for filename, content, maintype, subtype in (attachments or []):
        msg.add_attachment(
            content, maintype=maintype, subtype=subtype, filename=filename
        )
    return msg


class TestDecodeStr(unittest.TestCase):
    def test_plain_ascii(self):
        self.assertEqual(decode_str("Hello"), "Hello")

    def test_empty_or_none(self):
        self.assertEqual(decode_str(""), "")
        self.assertEqual(decode_str(None), "")


class TestGetEmailBody(unittest.TestCase):
    def test_simple_body(self):
        msg = make_email(subject="Hi", body="Please find my resume attached.")
        self.assertIn("resume", get_email_body(msg).lower())

    def test_empty_body(self):
        msg = make_email(subject="Hi", body="")
        self.assertEqual(get_email_body(msg).strip(), "")


class TestEmailMatchesKeyword(unittest.TestCase):
    def test_keyword_in_subject(self):
        msg = make_email(subject="My Resume", body="See attached.")
        self.assertTrue(email_matches_keyword(msg, "resume"))

    def test_keyword_in_body_only(self):
        msg = make_email(subject="Application", body="I've attached my resume.")
        self.assertTrue(email_matches_keyword(msg, "resume"))

    def test_keyword_case_insensitive(self):
        msg = make_email(subject="RESUME for job", body="")
        self.assertTrue(email_matches_keyword(msg, "resume"))

    def test_no_keyword_match(self):
        msg = make_email(subject="Meeting notes", body="See you at 3pm.")
        self.assertFalse(email_matches_keyword(msg, "resume"))


class TestIsAllowedAttachment(unittest.TestCase):
    ALLOWED = (".pdf", ".doc", ".docx")

    def test_pdf_allowed(self):
        self.assertTrue(is_allowed_attachment("resume.pdf", self.ALLOWED))

    def test_docx_allowed(self):
        self.assertTrue(is_allowed_attachment("resume.DOCX", self.ALLOWED))

    def test_image_rejected(self):
        self.assertFalse(is_allowed_attachment("photo.png", self.ALLOWED))

    def test_no_filename(self):
        self.assertFalse(is_allowed_attachment("", self.ALLOWED))
        self.assertFalse(is_allowed_attachment(None, self.ALLOWED))


class TestExtractAttachments(unittest.TestCase):
    ALLOWED = (".pdf", ".doc", ".docx")

    def test_extracts_only_allowed_types(self):
        msg = make_email(
            subject="My Resume",
            body="See attached.",
            attachments=[
                ("resume.pdf", b"%PDF-1.4 fake pdf content", "application", "pdf"),
                ("photo.png", b"fake png bytes", "image", "png"),
            ],
        )
        results = extract_attachments(msg, self.ALLOWED)
        filenames = [f for f, _ in results]
        self.assertIn("resume.pdf", filenames)
        self.assertNotIn("photo.png", filenames)

    def test_no_attachments(self):
        msg = make_email(subject="My Resume", body="Forgot to attach it!")
        results = extract_attachments(msg, self.ALLOWED)
        self.assertEqual(results, [])

    def test_multiple_allowed_attachments(self):
        msg = make_email(
            subject="My Resume",
            body="Two formats attached.",
            attachments=[
                ("resume.pdf", b"pdf bytes", "application", "pdf"),
                ("resume.docx", b"docx bytes", "application",
                 "vnd.openxmlformats-officedocument.wordprocessingml.document"),
            ],
        )
        results = extract_attachments(msg, self.ALLOWED)
        self.assertEqual(len(results), 2)
        payload_map = dict(results)
        self.assertEqual(payload_map["resume.pdf"], b"pdf bytes")
        self.assertEqual(payload_map["resume.docx"], b"docx bytes")


if __name__ == "__main__":
    unittest.main()
