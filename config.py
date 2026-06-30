import os

IMAP_SERVER = os.environ.get("IMAP_SERVER", "imap.gmail.com")
EMAIL_ACCOUNT = os.environ.get("EMAIL_ACCOUNT", "")
EMAIL_APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD", "")

SAVE_FOLDER = os.environ.get("SAVE_FOLDER", "./Resumes")
KEYWORD_FILTER = os.environ.get("KEYWORD_FILTER", "resume").lower()
ALLOWED_EXTENSIONS = (".pdf", ".doc", ".docx")

# How often to poll, in seconds, when running in continuous (loop) mode.
POLL_INTERVAL_SECONDS = int(os.environ.get("POLL_INTERVAL_SECONDS", "300"))
