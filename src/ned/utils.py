import shutil


def format_milli(milli: int) -> str:
    total_seconds = milli // 1000

    hr = total_seconds // 3600
    min = (total_seconds % 3600) // 60
    sec = total_seconds % 60

    if hr > 0:
        return f"{hr}:{min:02}:{sec:02}"
    else:
        return f"{min}:{sec:02}"


def is_librespot_installed():
    return shutil.which("librespot") is not None
