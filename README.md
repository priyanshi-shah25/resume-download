# Resume Email Downloader

Watches an inbox over IMAP and automatically saves PDF/Word attachments
from emails whose subject or body contains a keyword (default: "resume").

## Project structure

```
resume_downloader/
├── config.py            # settings, all read from environment variables
├── email_logic.py        # pure parsing/filtering logic (no network) — unit tested
├── imap_client.py         # talks to the IMAP server, saves files
├── main.py                 # entry point (single run or --loop polling)
├── requirements.txt
├── .env.example
└── tests/
    ├── test_email_logic.py   # tests parsing/filtering with fake emails
    └── test_imap_client.py    # tests inbox-processing flow with a mocked IMAP server
```

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Generate an **App Password** for your account (you cannot use your normal
   login password with IMAP):
   - Gmail / Google Workspace: Google Account → Security → 2-Step
     Verification (must be on) → App Passwords.
   - Outlook/Office365: Microsoft Account → Security → App Passwords.
   - Other providers: check their IMAP/app-password docs.

3. Copy `.env.example` to `.env` and fill in your real values, then either
   load it with `python-dotenv` or export the variables manually:

   **Windows PowerShell**
   ```
   $env:EMAIL_ACCOUNT="priyanshi.s@devstree.in"
   $env:EMAIL_APP_PASSWORD="your_app_password"
   $env:SAVE_FOLDER="C:\Users\YourUsername\Documents\Resumes"
   ```

   **macOS/Linux**
   ```
   export EMAIL_ACCOUNT="priyanshi.s@devstree.in"
   export EMAIL_APP_PASSWORD="your_app_password"
   export SAVE_FOLDER="$HOME/Documents/Resumes"
   ```

## Running

Check the inbox once:
```
python main.py
```

Run continuously, checking every `POLL_INTERVAL_SECONDS` (default 300s):
```
python main.py --loop
```

## Running the tests

```
pytest tests/ -v
```

All tests run offline — `test_email_logic.py` builds fake `EmailMessage`
objects in memory, and `test_imap_client.py` mocks the IMAP connection, so
no real mailbox or network access is required.

## How matching works

- An email matches if the keyword (`KEYWORD_FILTER`, default `"resume"`)
  appears anywhere in the subject line or plain-text body, case-insensitive.
- Of the attachments on a matching email, only files ending in `.pdf`,
  `.doc`, or `.docx` are saved (configurable via `ALLOWED_EXTENSIONS` in
  `config.py`).
- Processed emails are marked as read (`\Seen`) so they aren't picked up
  again on the next run.
