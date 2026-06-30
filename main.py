import sys
import time

from dotenv import load_dotenv
load_dotenv()
from imap_client import process_inbox
import config


def main():
    loop_mode = "--loop" in sys.argv

    if not loop_mode:
        process_inbox()
        return

    print(f"Polling every {config.POLL_INTERVAL_SECONDS} seconds. Press Ctrl+C to stop.")
    while True:
        try:
            process_inbox()
        except Exception as e:
            print(f"Error during inbox check: {e}")
        time.sleep(config.POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()