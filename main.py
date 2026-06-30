import sys
import time
import platform

from dotenv import load_dotenv
load_dotenv()

from imap_client import process_inbox
import config

# Only import notifications on Windows
if platform.system() == "Windows":
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        NOTIFICATIONS_ENABLED = True
    except ImportError:
        print("⚠️  win10toast not installed!")
        print("   Run: pip install win10toast")
        NOTIFICATIONS_ENABLED = False
else:
    NOTIFICATIONS_ENABLED = False
    print("⚠️  Desktop notifications only work on Windows")


def send_notification(title, message):
    """Send Windows desktop notification"""
    if not NOTIFICATIONS_ENABLED:
        return
    
    try:
        toaster.show_toast(
            title=title,
            msg=message,
            duration=10,  # Show for 10 seconds
            threaded=True
        )
    except Exception:
        pass  # Silent fail if notification doesn't work


def main():
    loop_mode = "--loop" in sys.argv

    print(f"🚀 Resume Downloader Started")
    print(f"📧 Email: {config.EMAIL_ACCOUNT}")
    print(f"💾 Saving to: {config.SAVE_FOLDER}")
    
    if not loop_mode:
        # Single run
        try:
            process_inbox()
            print("✅ Done!")
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error: {error_msg}")
            send_notification("Resume Downloader Error", error_msg)
        return

    # Loop mode - keep checking inbox forever
    print(f"⏳ Checking every {config.POLL_INTERVAL_SECONDS} seconds")
    print("   (Close this window or press Ctrl+C to stop)\n")
    
    error_count = 0
    max_errors = 5

    try:
        while True:
            try:
                print(f"[{time.strftime('%H:%M:%S')}] Checking inbox...", end=" ")
                process_inbox()
                print("✅")
                error_count = 0  # Reset errors
                
            except Exception as e:
                error_count += 1
                error_msg = str(e)
                print(f"❌ Error: {error_msg}")
                
                # Send notification
                send_notification(
                    "❌ Resume Downloader Error",
                    error_msg[:100]  # First 100 chars
                )
                
                # Stop after too many errors
                if error_count >= max_errors:
                    print(f"\n🛑 Too many errors ({max_errors}). Stopping.")
                    send_notification(
                        "Resume Downloader Stopped",
                        f"Failed {max_errors} times. Please check settings."
                    )
                    break
            
            time.sleep(config.POLL_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n\n👋 Stopped by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        send_notification("Resume Downloader Crashed", str(e)[:100])


if __name__ == "__main__":
    main()