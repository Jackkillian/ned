import time


def handle_spotify_error(e):
    status = e.http_status
    message = e.msg or str(e)

    if status == 401:
        raise RuntimeError("Spotify auth expired — reauthenticate") from e

    elif status == 403:
        raise RuntimeError(
            "Insufficient Spotify scope. Re-login with the required permissions."
        ) from e

    elif status == 404:
        return "pass"

    elif status == 429:
        retry_after = int(e.headers.get("Retry-After", 1))
        time.sleep(retry_after)
        return "retry"

    elif 500 <= status < 600:
        time.sleep(2)
        return "retry"

    else:
        raise RuntimeError(f"Spotify error {status}: {message}") from e
