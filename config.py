import os

IMAP_SERVER = os.environ.get("IMAP_SERVER", "imap.gmail.com")
EMAIL_ACCOUNT = os.environ.get("EMAIL_ACCOUNT", "")
EMAIL_APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD", "")

SAVE_FOLDER = os.environ.get("SAVE_FOLDER", "./Resumes")
KEYWORD_FILTER = os.environ.get(
    "KEYWORD_FILTER", "resume, job application, interested, application, experience, hire, cv, interview, role, this role, job opportunity, opportunity"
).lower()
ALLOWED_EXTENSIONS = (".pdf", ".doc", ".docx")
LOG_FILE = os.environ.get("LOG_FILE", "./errors.log") #change file path

# How often to poll, in seconds, when running in continuous (loop) mode.
POLL_INTERVAL_SECONDS = int(os.environ.get("POLL_INTERVAL_SECONDS", "300"))
