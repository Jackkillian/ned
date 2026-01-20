import atexit
import shutil
import subprocess

import spotipy

from ned.api import spotify_call
from ned.config import get_device_name
from ned.session import SessionState
from ned.timer import BackgroundTimer
from ned.utils import is_librespot_installed

from .scope import Library, Playback, SpotifyConnect, get_scope
from .session_data import DotDict, SpotifySessionInfo

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
    def __init__(self, client_id=None, client_secret=None):
        if client_id:
            self.client_id = client_id
        if client_secret:
            self.client_secret = client_secret
        if not hasattr(self, "sp"):
            sp_oauth = spotipy.SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=REDIRECT_URI,
                scope=SCOPE,
                cache_path=".cache",  # TODO: use diff dir
            )
            access_token = sp_oauth.get_access_token(as_dict=False)
            self.sp = spotipy.Spotify(auth=access_token)

        atexit.register(self.stop)

    def start_librespot(self):
        cmd = [
            shutil.which("librespot"),
            "--name",
            self.device_name,
            # "--backend",
            # "portaudio",  # or "alsa", "pulseaudio" depending on your system
            "--cache",
            "./spotify_cache",
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
        self.sp.start_playback(device_id=device_id, uris=[track_uri])

    def pause(self):
        spotify_call(self.sp.pause_playback)

    def resume(self):
        spotify_call(self.sp.start_playback)

    def next_track(self):
        spotify_call(self.sp.next_track)

    def previous_track(self):
        spotify_call(self.sp.previous_track)

    def seek(self, position_ms):
        spotify_call(self.sp.seek_track, position_ms)

    def get_current_playback(self):
        return spotify_call(self.sp.current_playback)

    def set_volume(self, volume_percent):
        spotify_call(self.sp.volume, volume_percent)

    def stop(self):
        if self.librespot_process:
            self.librespot_process.terminate()
            try:
                self.librespot_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.librespot_process.kill()
                self.librespot_process.wait()
