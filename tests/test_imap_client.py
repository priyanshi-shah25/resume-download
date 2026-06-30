"""
Tests for imap_client.py — IMAP server is mocked, so no network or real
mailbox is needed.

Run with:
    pytest tests/test_imap_client.py -v
"""
import sys
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock
from email.message import EmailMessage

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config
import imap_client


def make_raw_email(subject, body, attachments=None):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "candidate@example.com"
    msg.set_content(body)
    for filename, content, maintype, subtype in (attachments or []):
        msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)
    return msg.as_bytes()


class TestSaveAttachment(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_saves_file_to_folder(self):
        path = imap_client.save_attachment("resume.pdf", b"fake pdf bytes", self.tmpdir)
        self.assertTrue(os.path.exists(path))
        with open(path, "rb") as f:
            self.assertEqual(f.read(), b"fake pdf bytes")

    def test_creates_folder_if_missing(self):
        nested = os.path.join(self.tmpdir, "nested", "resumes")
        path = imap_client.save_attachment("resume.pdf", b"data", nested)
        self.assertTrue(os.path.exists(path))


class TestProcessInbox(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # Point config at a temp folder + set required credentials so
        # connect() doesn't raise.
        self._orig_save_folder = config.SAVE_FOLDER
        self._orig_account = config.EMAIL_ACCOUNT
        self._orig_password = config.EMAIL_APP_PASSWORD
        config.SAVE_FOLDER = self.tmpdir
        config.EMAIL_ACCOUNT = "test@example.com"
        config.EMAIL_APP_PASSWORD = "fake_app_password"

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        config.SAVE_FOLDER = self._orig_save_folder
        config.EMAIL_ACCOUNT = self._orig_account
        config.EMAIL_APP_PASSWORD = self._orig_password

    def _mock_mail(self, raw_emails):
        """
        Build a MagicMock standing in for an imaplib.IMAP4_SSL instance.
        `raw_emails` is a list of raw bytes, one per fake message.
        """
        mock_mail = MagicMock()
        ids = [str(i).encode() for i in range(len(raw_emails))]
        mock_mail.search.return_value = ("OK", [b" ".join(ids)])

        def fake_fetch(msg_id, _):
            idx = int(msg_id)
            return ("OK", [(b"1 (RFC822 {123}", raw_emails[idx])])

        mock_mail.fetch.side_effect = fake_fetch
        return mock_mail

    def test_no_unseen_emails(self):
        mock_mail = self._mock_mail([])
        imap_client.connect = MagicMock(return_value=mock_mail)

        imap_client.process_inbox()

        mock_mail.close.assert_called_once()
        mock_mail.logout.assert_called_once()
        self.assertEqual(os.listdir(self.tmpdir), [])

    def test_matching_email_saves_attachment(self):
        raw = make_raw_email(
            subject="My Resume",
            body="Please see attached.",
            attachments=[("resume.pdf", b"%PDF fake", "application", "pdf")],
        )
        mock_mail = self._mock_mail([raw])
        imap_client.connect = MagicMock(return_value=mock_mail)

        imap_client.process_inbox()

        saved_files = os.listdir(self.tmpdir)
        self.assertIn("resume.pdf", saved_files)
        # Email should be marked as read
        mock_mail.store.assert_called_with(b"0", "+FLAGS", "\\Seen")

    def test_non_matching_email_saves_nothing(self):
        raw = make_raw_email(
            subject="Team lunch",
            body="See you at noon.",
            attachments=[("menu.pdf", b"%PDF fake", "application", "pdf")],
        )
        mock_mail = self._mock_mail([raw])
        imap_client.connect = MagicMock(return_value=mock_mail)

        imap_client.process_inbox()

        self.assertEqual(os.listdir(self.tmpdir), [])
        # Still marked as read so it's not reprocessed forever
        mock_mail.store.assert_called_with(b"0", "+FLAGS", "\\Seen")

    def test_matching_email_with_disallowed_attachment_only(self):
        raw = make_raw_email(
            subject="My Resume",
            body="Attached as image, oops",
            attachments=[("resume_photo.png", b"fake png", "image", "png")],
        )
        mock_mail = self._mock_mail([raw])
        imap_client.connect = MagicMock(return_value=mock_mail)

        imap_client.process_inbox()

        self.assertEqual(os.listdir(self.tmpdir), [])


if __name__ == "__main__":
    unittest.main()
