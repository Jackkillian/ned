import threading
import time
from typing import TYPE_CHECKING

from ned.spotify.scope import Library, Playback, SpotifyConnect, get_scope
from ned.spotify.session_data import DotDict, LSStatus, SpotifySessionInfo

if TYPE_CHECKING:
    from ned.spotify.client import SpotifyTerminalClient

UPDATE_INTERVAL_MS = 2000
DEVICE_UPDATE_INTERVAL_MS = 5000  # TODO: this isn't used
SCOPE = get_scope(
    SpotifyConnect.ReadPlaybackState,
    SpotifyConnect.ModifyPlaybackState,
    SpotifyConnect.ReadCurrentlyPlaying,
    Playback.AppRemoteControl,
    Playback.Streaming,
    # Users.Personalized,
    # Users.ReadPrivate,
    # Users.ReadEmail,
    Library.Read,
)


class SessionState:
    def __init__(self, client: "SpotifyTerminalClient"):
        self.timer = 0
        self.client = client
        self.session = SpotifySessionInfo()
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.device_id = None

    def get_device_id(self):
        if self.device_id is not None:
            return self.device_id
        result = self.client.api.get_devices()
        if not result["ok"]:
            return None
        for device in result["data"]["devices"]:
            if device["name"] == self.client.device_name:
                return device["id"]
        return None

    def _timer_loop(self):
        while self.running:
            time.sleep(0.01)
            with self.lock:
                self.timer += 10
                if self.timer >= UPDATE_INTERVAL_MS:
                    user_result = self.client.api.get_me()
                    if user_result["ok"]:
                        # TODO: maybe only call this once
                        self.session.user = DotDict(user_result["data"])

                    self.device_id = self.get_device_id()
                    if not self.device_id:
                        self.session.librespot = LSStatus.WAITING
                    elif self.session.playback.device.id == self.device_id:
                        self.session.librespot = LSStatus.CONNECTED
                    else:
                        self.session.librespot = LSStatus.CONNECTING
                        result = self.client.api.transfer_playback(self.device_id)
                        if not result["ok"]:
                            self.session.librespot = LSStatus.FAILED

                    result = self.client.api.get_current_playback()
                    if result["ok"] and result["data"]:
                        self.session.playback = DotDict(result["data"])
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
