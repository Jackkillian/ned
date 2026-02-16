import atexit
import shutil
import subprocess
import threading
import time

from ned.config import get_cached_token, get_device_name, save_cached_token
from ned.spotify.api_instance import SpotifyAPI
from ned.spotify.scope import Library, Playback, SpotifyConnect, get_scope
from ned.timer import BackgroundTimer
from ned.utils import CACHE_DIR, is_librespot_installed
from ned.spotify.data import LSStatus, UserData, PlaybackData

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
REDIRECT_URI = "http://127.0.0.1:8080/callback"
UPDATE_INTERVAL = 2
DEVICE_UPDATE_INTERVAL = 5  # TODO: this isn't used


class SessionData:
    device_id: str | None = None
    device_name: str = ""
    logs: list[str] = []
    user = UserData.from_dict({})
    playback = PlaybackData.from_dict({})
    librespot: LSStatus = LSStatus.CONNECTING


class NedSession:
    def __init__(self):
        self.librespot_process = None

        self.data = SessionData()
        self.data.device_name = get_device_name()

        self.timer = BackgroundTimer()
        self.timer.start()

        self.thread_running = False
        self.thread = None
        self.lock = threading.Lock()

    def setup(self, client_id):
        self.client_id = client_id
        self.api = SpotifyAPI(
            client_id=self.client_id,
            scope=SCOPE,
        )
        token = get_cached_token()
        if token and self.api.is_token_valid(token):
            self.access_token = token
            self.api.oauth_token = self.access_token
        else:
            self.api.perform_oauth()
            self.access_token = self.api.oauth_token
        save_cached_token(self.access_token)

        self.start_thread()

        atexit.register(self.stop)

    def start_librespot(self):
        cmd = [
            shutil.which("librespot"),
            "--name",
            self.data.device_name,
            # "--backend",
            # "portaudio",  # or "alsa" or "pulseaudio"
            "--access-token",
            self.access_token,
            "--cache",
            CACHE_DIR,
            "--enable-oauth",
            "--device-type",
            "computer",
            "--bitrate",
            "320",
            # "--verbose",
        ]

        self.stop()

        if not is_librespot_installed():
            print(
                "Librespot is not installed. Please see the setup instructions at https://github.com/Jackkillian/ned for more details."
            )
            exit(1)

        self.librespot_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        def log_output(pipe):
            for line in pipe:
                self.data.logs.append(line.rstrip())

        threading.Thread(
            target=log_output, args=(self.librespot_process.stdout,), daemon=True
        ).start()
        threading.Thread(
            target=log_output, args=(self.librespot_process.stderr,), daemon=True
        ).start()

        # Check if process is still running
        if self.librespot_process.poll() is not None:
            return (
                False,
                f"Librespot exited with code {self.librespot_process.returncode}",
            )

        return True, "Successfully started Librespot"

    def get_device_id(self):
        if self.data.device_id is not None:
            return self.data.device_id
        result = self.api.get_devices()
        if not result["ok"]:
            self.data.logs.append(f"[ERR] Could not load devices: {result['data']}")
            return None
        for device in result["data"]["devices"]:
            if device["name"] == self.data.device_name:
                return device["id"]
        return None

    def stop(self):
        if self.librespot_process:
            self.librespot_process.terminate()
            try:
                self.librespot_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.librespot_process.kill()
                self.librespot_process.wait()

    def _update_state_loop(self):
        while self.thread_running:
            time.sleep(UPDATE_INTERVAL)
            with self.lock:
                user_result = self.api.get_me()
                if user_result["ok"]:
                    # TODO: maybe only call this once
                    self.data.user = UserData.from_dict(user_result["data"])
                else:
                    self.data.logs.append(
                        f"[ERR] Could not load user data: {user_result['data']}"
                    )

                result = self.api.get_current_playback()
                if result["ok"] and result["data"]:
                    self.data.playback = PlaybackData.from_dict(result["data"])
                    self.timer.set_time(self.data.playback.progress_ms)

                    # TODO: should logic be in this class?
                    if self.data.playback.is_playing and not self.timer.running:
                        self.timer.start()
                    elif not self.data.playback.is_playing and self.timer.running:
                        self.timer.stop()
                else:
                    self.data.playback = PlaybackData.from_dict({})

                if not result["ok"]:
                    self.data.logs.append(
                        f"[ERR] Could not load playback: {result['data']}"
                    )

                self.data.device_id = self.get_device_id()
                if not self.data.device_id:
                    self.data.librespot = LSStatus.WAITING
                elif self.data.playback.device.id == self.data.device_id:
                    self.data.librespot = LSStatus.CONNECTED
                else:
                    self.data.librespot = LSStatus.CONNECTING
                    result = self.api.transfer_playback(self.data.device_id)
                    if not result["ok"]:
                        self.data.logs.append(
                            f"[ERR] Could not transfer playback: {result['data']}"
                        )
                        self.data.librespot = LSStatus.FAILED

    def start_thread(self):
        if not self.thread_running:
            self.thread_running = True
            self.thread = threading.Thread(target=self._update_state_loop, daemon=True)
            self.thread.start()

    def stop_thread(self):
        self.thread_running = False
        if self.thread:
            self.thread.join()
