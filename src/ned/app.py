import signal
import sys
import time

import urwid
from modern_urwid import CompileContext, LifecycleManager
from urwid.event_loop.main_loop import ExitMainLoop

from ned.config import get_config
from ned.utils import RESOURCES_DIR, setup_resources

from .spotify.client import SpotifyTerminalClient


def run():
    setup_resources(True)  # TODO: for dev
    context = CompileContext(RESOURCES_DIR)
    loop = urwid.MainLoop(
        urwid.Text(""),
        palette=[
            ("pb_empty", "", "", "", "#efefef", "#000000"),
            ("pb_full", "", "", "", "#000000", "#ffb955"),
            ("pb_satt", "", "", "", "#ffb955", "#000000"),
            ("info_success", "", "", "", "#64ff64,bold", "#131313"),
            ("info_neutral", "", "", "", "#6464ff,bold", "#131313"),
            ("info_error", "", "", "", "#ff6464,bold", "#131313"),
            ("keybind_key", "", "", "", "#ff9905,bold", "#222222"),
            ("keybind_bind", "", "", "", "#df7905", "#222222"),
        ],
    )
    loop.screen.set_terminal_properties(2**24)

    manager = LifecycleManager(context, loop)
    manager.register("layouts/main.xml")
    manager.register("layouts/setup.xml")

    # determine if this is the first run
    config = get_config()
    layout = "main"
    if config is None:
        layout = "setup"

    try:
        manager.run(layout)
    except (ExitMainLoop, KeyboardInterrupt):
        pass

    return
    client = SpotifyTerminalClient(client_id=ID, client_secret=SECRET)

    def signal_handler(sig, frame):
        print("\nShutting down...")
        client.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Start librespot
    client.start_librespot()

    # Wait a bit
    time.sleep(5)

    # Play a track
    # uri = "spotify:artist:3YQKmKGau1PzlVlkL1iodx"
    # client.sp.start_playback(device_id=client.get_device_id(), context_uri=uri)
    # client.play_track("spotify:track:3CRDbSIZ4r5MsZ0YwxuEkn")

    # Get current playback
    current = client.get_current_playback()
    if current and current["is_playing"]:
        track = current["item"]
        print(f"Now playing: {track['name']} by {track['artists'][0]['name']}")
        print(f"Progress: {current['progress_ms']}ms / {track['duration_ms']}ms")

    # Pause
    time.sleep(10)
    client.pause()
    print("Paused")

    # Resume
    time.sleep(3)
    client.resume()
    print("Resumed")

    # Stop when done
    input("Press Enter to stop...")
    client.stop()
