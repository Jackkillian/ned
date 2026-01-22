import atexit
import shutil
import subprocess
import threading

from ned.config import get_cached_token, get_device_name, save_cached_token
from ned.session import SessionState
from ned.spotify.api_instance import SpotifyAPI
from ned.timer import BackgroundTimer
from ned.utils import CACHE_DIR, is_librespot_installed

from .scope import Library, Playback, SpotifyConnect, get_scope

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


class ClientSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(ClientSingleton, cls).__call__(*args, **kwargs)
            cls._instances[cls].librespot_process = None
            cls._instances[cls].device_name = get_device_name()
            cls._instances[cls].device_id = None
            timer = BackgroundTimer()
            timer.start()
            cls._instances[cls].timer = timer
            session_state = SessionState(cls._instances[cls])
            session_state.start()
            cls._instances[cls].session_state = session_state
        return cls._instances[cls]


class SpotifyTerminalClient(metaclass=ClientSingleton):
    def __init__(self, client_id=None):
        if client_id:
            self.client_id = client_id

        if not hasattr(self, "api"):
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

        atexit.register(self.stop)

    def start_librespot(self):
        cmd = [
            shutil.which("librespot"),
            "--name",
            self.device_name,
            # "--backend",
            # "portaudio",  # or "alsa", "pulseaudio" depending on your system
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

        # TODO: have log view screen

        # def log_output(pipe, prefix):
        #     for line in pipe:
        #         print(f"[LS {prefix}] {line.rstrip()}")

        # threading.Thread(
        #     target=log_output, args=(self.librespot_process.stdout, "OUT"), daemon=True
        # ).start()
        # threading.Thread(
        #     target=log_output, args=(self.librespot_process.stderr, "ERR"), daemon=True
        # ).start()

        # Check if process is still running
        if self.librespot_process.poll() is not None:
            return (
                False,
                f"Librespot exited with code {self.librespot_process.returncode}",
            )

        return True, "Successfully started Librespot"

    def get_device_id(self):
        if self.device_id is not None:
            return self.device_id
        devices = self.sp.devices()
        if devices:
            devices = devices["devices"]
        else:
            return None
        for device in devices:
            if device["name"] == self.device_name:
                return device["id"]
        return None

    def play_track(self, track_uri):
        device_id = self.get_device_id()
        if not device_id:
            print("Device not found! Make sure librespot is running.")
            return

        print(f"Playing {track_uri} on device {device_id}")
        self.api.start_playback(device_id=device_id, uris=[track_uri])

    def pause(self):
        self.api.pause_playback()

    def resume(self):
        self.api.start_playback()

    def next_track(self):
        self.api.skip_to_next()

    def previous_track(self):
        self.api.skip_to_previous()

    def seek(self, position_ms):
        self.api.seek_to_position(position_ms)

    def get_current_playback(self):
        return self.api.get_current_playback()

    def set_volume(self, volume_percent):
        self.api.set_volume(volume_percent)

    def stop(self):
        if self.librespot_process:
            self.librespot_process.terminate()
            try:
                self.librespot_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.librespot_process.kill()
                self.librespot_process.wait()
