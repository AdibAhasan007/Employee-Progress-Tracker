import requests
import config
from urllib.parse import urlparse


def _host_from_api_url():
    try:
        parsed = urlparse(config.API_URL)
        return f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else None
    except Exception:
        return None


def is_connected():
    """Checks connectivity. Prefer the configured API host; fallback to Google."""
    timeout = 5
    # 1) Try API host
    api_host = _host_from_api_url()
    if api_host:
        try:
            requests.get(api_host, timeout=timeout)
            return True
        except Exception:
            pass

    # 2) Fallback to Google
    try:
        requests.get("https://www.google.com/", timeout=timeout)
        return True
    except Exception:
        return False