import subprocess
import sys


def send_notification(title: str, message: str) -> None:
    """Send a desktop notification. Best-effort: silently ignores failures."""
    try:
        if sys.platform == "darwin":
            subprocess.run(
                ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
                timeout=5,
            )
        elif sys.platform == "linux":
            subprocess.run(["notify-send", title, message], timeout=5)
    except Exception:
        pass
