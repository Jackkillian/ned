import threading
import time
from typing import TYPE_CHECKING

from ned.spotify.session_data import DotDict, SpotifySessionInfo

if TYPE_CHECKING:
    from ned.spotify.client import SpotifyTerminalClient

UPDATE_INTERVAL_MS = 2000
DEVICE_UPDATE_INTERVAL_MS = 5000


class SessionState:
    def __init__(self, client: "SpotifyTerminalClient"):
        self.timer = 0
        self.client = client
        self.session = SpotifySessionInfo()
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

    def _timer_loop(self):
        while self.running:
            time.sleep(0.01)
            with self.lock:
                self.timer += 10
                if self.timer >= UPDATE_INTERVAL_MS:
                    user: dict = self.client.sp.current_user()
                    if user:
                        # TODO: maybe only call this once
                        self.session.user = DotDict(user)

                    device_id = self.client.get_device_id()
                    if not device_id:
                        self.session.librespot = "waiting"
                    elif self.session.playback.device.id == device_id:
                        self.session.librespot = "connected"
                    else:
                        self.session.librespot = "connecting"
                        self.client.sp.transfer_playback(device_id, False)

                    if playback := self.client.get_current_playback():
                        self.session.playback = DotDict(playback)
                        self.client.timer.set_time(self.session.playback.progress_ms)

                        if (
                            self.session.playback.is_playing
                            and not self.client.timer.running
                        ):
                            self.client.timer.start()
                        elif (
                            not self.session.playback.is_playing
                            and self.client.timer.running
                        ):
                            self.client.timer.stop()
                    else:
                        self.session.playback.clear()

                    self.timer = 0

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._timer_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
