import json
import os
import shutil
import webbrowser
from importlib.resources import as_file, files
from pathlib import Path

ROOT_DIR = Path.home() / ".ned"
CACHE_DIR = ROOT_DIR / "cache"
RESOURCES_DIR = ROOT_DIR / "resources"


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


def setup_resources(override=False) -> Path:
    resources_package = files("ned.resources")
    with as_file(resources_package) as src_path:
        if not RESOURCES_DIR.exists():
            shutil.copytree(src_path, RESOURCES_DIR)
        elif override:
            for src_file in src_path.rglob("*"):
                if src_file.is_file():
                    relative_path = src_file.relative_to(src_path)
                    dest_file = RESOURCES_DIR / relative_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dest_file)


def open_url(url):
    savout = os.dup(1)
    os.close(1)
    os.open(os.devnull, os.O_RDWR)
    try:
        webbrowser.open(url)
    finally:
        os.dup2(savout, 1)
