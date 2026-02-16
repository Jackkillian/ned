import atexit
from enum import Enum
import shutil
import subprocess
import threading
import time
from typing import TYPE_CHECKING, Literal, Type, TypeVar, Any
from dataclasses import dataclass

from ned.config import get_cached_token, get_device_name, save_cached_token
from ned.spotify.api_instance import SpotifyAPI
from ned.spotify.scope import Library, Playback, SpotifyConnect, get_scope
from ned.timer import BackgroundTimer
from ned.utils import CACHE_DIR, is_librespot_installed

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


class LSStatus(Enum):
    CONNECTING = "Connecting to Spotify..."
    CONNECTED = "Connected"
    WAITING = "Waiting for Librespot..."
    FAILED = "Failed to connect to Spotify."


@dataclass
class DataClass:
    def update(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


@dataclass
class DeviceData(DataClass):
    id: str | None
    is_active: bool
    is_private_session: bool
    is_restricted: bool
    name: str
    type: str
    volume_percent: int | None
    supports_volume: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceData":
        return cls(
            id=data.get("id"),
            is_active=data.get("is_active", False),
            is_private_session=data.get("is_private_session", False),
            is_restricted=data.get("is_restricted", False),
            name=data.get("name", ""),
            type=data.get("type", ""),
            volume_percent=data.get("volume_percent"),
            supports_volume=data.get("supports_volume", False),
        )


@dataclass
class PlaybackActionsData(DataClass):
    interrupting_playback: bool
    pausing: bool
    resuming: bool
    seeking: bool
    skipping_next: bool
    skipping_prev: bool
    toggling_repeat_context: bool
    toggling_shuffle: bool
    toggling_repeat_track: bool
    transferring_playback: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlaybackActionsData":
        return cls(
            interrupting_playback=data.get("interrupting_playback", False),
            pausing=data.get("pausing", False),
            resuming=data.get("resuming", False),
            seeking=data.get("seeking", False),
            skipping_next=data.get("skipping_next", False),
            skipping_prev=data.get("skipping_prev", False),
            toggling_repeat_context=data.get("toggling_repeat_context", False),
            toggling_shuffle=data.get("toggling_shuffle", False),
            toggling_repeat_track=data.get("toggling_repeat_track", False),
            transferring_playback=data.get("transferring_playback", False),
        )


@dataclass
class ContextData(DataClass):
    type: str
    href: str
    external_urls: dict[str, str]
    uri: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContextData":
        return cls(
            type=data.get("type", ""),
            href=data.get("href", ""),
            external_urls=data.get("external_urls", {}),
            uri=data.get("uri", ""),
        )


@dataclass
class TrackData(DataClass):
    album: dict[str, str]
    artists: list[dict[str, str]]
    available_markets: list[str]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: dict[str, str]
    external_urls: dict[str, str]
    href: str
    id: str
    is_playable: bool
    linked_from: dict[str, str]
    restrictions: dict[str, str]
    name: str
    popularity: int
    preview_url: str | None
    track_number: int
    type: Literal["track"]
    uri: str
    is_local: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrackData":
        return cls(
            album=data.get("album", {}),
            artists=data.get("artists", []),
            available_markets=data.get("available_markets", []),
            disc_number=data.get("disc_number", 0),
            duration_ms=data.get("duration_ms", 0),
            explicit=data.get("explicit", False),
            external_ids=data.get("external_ids", {}),
            external_urls=data.get("external_urls", {}),
            href=data.get("href", ""),
            id=data.get("id", ""),
            is_playable=data.get("is_playable", False),
            linked_from=data.get("linked_from", {}),
            restrictions=data.get("restrictions", {}),
            name=data.get("name", ""),
            popularity=data.get("popularity", 0),
            preview_url=data.get("preview_url"),
            track_number=data.get("track_number", 0),
            type=data.get("type", "track"),
            uri=data.get("uri", ""),
            is_local=data.get("is_local", False),
        )


@dataclass
class EpisodeData(DataClass):
    audio_preview_url: str | None
    description: str
    html_description: str
    duration_ms: int
    explicit: bool
    external_urls: dict[str, str]
    href: str
    id: str
    images: list[dict[str, str | int]]
    is_externally_hosted: bool
    is_playable: bool
    language: str
    languages: list[str]
    name: str
    release_date: str
    release_date_precision: Literal["year"] | Literal["month"] | Literal["day"]
    resume_point: dict[str, bool | int]
    type: Literal["episode"]
    uri: str
    show: dict

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EpisodeData":
        return cls(
            audio_preview_url=data.get("audio_preview_url"),
            description=data.get("description", ""),
            html_description=data.get("html_description", ""),
            duration_ms=data.get("duration_ms", 0),
            explicit=data.get("explicit", False),
            external_urls=data.get("external_urls", {}),
            href=data.get("href", ""),
            id=data.get("id", ""),
            images=data.get("images", []),
            is_externally_hosted=data.get("is_externally_hosted", False),
            is_playable=data.get("is_playable", False),
            language=data.get("language", ""),
            languages=data.get("languages", []),
            name=data.get("name", ""),
            release_date=data.get("release_date", ""),
            release_date_precision=data.get("release_date_precision", "day"),
            resume_point=data.get("resume_point", {}),
            type=data.get("type", "episode"),
            uri=data.get("uri", ""),
            show=data.get("show", {}),
        )


@dataclass
class PlaybackData(DataClass):
    # https://developer.spotify.com/documentation/web-api/reference/get-information-about-the-users-current-playback
    device: DeviceData
    repeat_state: Literal["off"] | Literal["track"] | Literal["context"]
    shuffle_state: bool
    context: ContextData
    timestamp: int
    progress_ms: int | None
    is_playing: bool
    item: TrackData | EpisodeData | None
    currently_playing_type: Literal["track"] | Literal["episode"]
    actions: PlaybackActionsData

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlaybackData":
        item_dict = data.get("item", {})
        item_type = item_dict.get("type")
        if item_type == "track":
            item = TrackData.from_dict(item_dict)
        elif item_type == "episode":
            item = EpisodeData.from_dict(item_dict)
        else:
            item = None

        return cls(
            device=DeviceData.from_dict(data.get("device", {})),
            repeat_state=data.get("repeat_state", ""),
            shuffle_state=data.get("shuffle_state", False),
            context=ContextData.from_dict(data.get("context", {})),
            timestamp=data.get("timestamp", 0),
            progress_ms=data.get("progress_ms", None),
            is_playing=data.get("is_playing", False),
            item=item,
            currently_playing_type=data.get("currently_playing_type", ""),
            actions=PlaybackActionsData.from_dict(data.get("actions", {})),
        )


@dataclass
class UserData(DataClass):
    country: str
    display_name: str
    email: str
    explicit_content: dict[str, bool]
    external_urls: dict[str, str]
    followers: dict[str, str | int]
    href: str
    id: str
    images: list[dict[str, str | int]]
    product: str
    type: Literal["user"]
    uri: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserData":
        return cls(
            country=data.get("country", ""),
            display_name=data.get("display_name", ""),
            email=data.get("email", ""),
            explicit_content=data.get("explicit_content", {}),
            external_urls=data.get("external_urls", {}),
            followers=data.get("followers", {}),
            href=data.get("href", ""),
            id=data.get("id", ""),
            images=data.get("images", []),
            product=data.get("product", ""),
            type=data.get("type", "user"),
            uri=data.get("uri", ""),
        )


class SessionData:
    device_id: str | None = None
    device_name: str = ""

    user = UserData.from_dict({})
    playback = PlaybackData.from_dict({})
    librespot: LSStatus = LSStatus.CONNECTING


# TODO: combine this class with the NedSession one
class SessionUpdater:
    def __init__(
        self, api: SpotifyAPI, session_data: SessionData, timer: BackgroundTimer
    ):
        self.timer = timer
        self.api = api
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.device_id = None

        self.data = session_data

    def get_device_id(self):
        if self.device_id is not None:
            return self.device_id
        result = self.api.get_devices()
        if not result["ok"]:
            return None
        for device in result["data"]["devices"]:
            if device["name"] == self.data.device_name:
                return device["id"]
        return None

    def _timer_loop(self):
        while self.running:
            time.sleep(UPDATE_INTERVAL)
            with self.lock:
                user_result = self.api.get_me()
                if user_result["ok"]:
                    # TODO: maybe only call this once
                    self.data.user = UserData.from_dict(user_result["data"])

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

                self.device_id = self.get_device_id()
                if not self.device_id:
                    self.data.librespot = LSStatus.WAITING
                elif self.data.playback.device.id == self.device_id:
                    self.data.librespot = LSStatus.CONNECTED
                else:
                    self.data.librespot = LSStatus.CONNECTING
                    result = self.api.transfer_playback(self.device_id)
                    if not result["ok"]:
                        self.data.librespot = LSStatus.FAILED

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._timer_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()


class NedSession:
    def __init__(self):
        self.librespot_process = None

        self.data = SessionData()
        self.data.device_name = get_device_name()

        self.timer = BackgroundTimer()
        self.timer.start()

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

        self.session_state = SessionUpdater(self.api, self.data, self.timer)
        self.session_state.start()

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
        # TODO: is this a dup
        if self.data.device_id is not None:
            return self.data.device_id
        result = self.api.get_devices()
        if result["ok"]:
            devices = result["data"]
        else:
            return None
        for device in devices:
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
