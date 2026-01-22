from enum import Enum
from threading import Lock
from typing import Literal, NotRequired, TypedDict


class DeviceDict(TypedDict):
    id: NotRequired[str]
    is_active: bool
    is_private_session: bool
    is_restricted: bool
    name: str
    type: str
    volume_percent: NotRequired[int]
    supports_volume: bool


class PlaybackActionsDict(TypedDict):
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


class ContextDict(TypedDict):
    type: str
    href: str
    external_urls: dict[str, str]
    uri: str


class TrackDict(TypedDict):
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
    preview_url: NotRequired[str]
    track_number: int
    type: Literal["track"]
    uri: str
    is_local: bool


class EpisodeDict(TypedDict):
    audio_preview_url: NotRequired[str]
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
    type: Literal["track"]
    uri: str
    show: dict


class PlaybackDict(TypedDict):
    # https://developer.spotify.com/documentation/web-api/reference/get-information-about-the-users-current-playback
    device: DeviceDict
    repeat_state: Literal["off"] | Literal["track"] | Literal["context"]
    shuffle_state: bool
    context: NotRequired[ContextDict]
    timestamp: int
    progress_ms: NotRequired[int]
    is_playing: bool
    item: TrackDict | EpisodeDict
    currently_playing_type: Literal["track"] | Literal["episode"]
    actions: PlaybackActionsDict


class UserDict(TypedDict):
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


# class SessionDict(TypedDict):
#     user: UserDict
#     playback: PlaybackDict
#     librespot: Literal["connecting"] | Literal["connecting"]


class DotDict(dict):
    def __init__(self, d=None):
        super().__init__()
        if d:
            for k, v in d.items():
                self[k] = self._wrap(v)

    def _wrap(self, v):
        if isinstance(v, dict):
            return DotDict(v)
        return v

    def __getattr__(self, k):
        if k not in self:
            self[k] = DotDict()
        return self[k]

    def __setattr__(self, k, v):
        self[k] = self._wrap(v)

    # def update(self, d):
    #     for k, v in d.items():
    #         self[k] = self._wrap(v)


class LSStatus(Enum):
    CONNECTING = "Connecting to Spotify..."
    CONNECTED = "Connected"
    WAITING = "Waiting for Librespot..."
    FAILED = "Failed to connect to Spotify."


class SpotifySessionInfo:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.user: UserDict = DotDict()
        self.playback: PlaybackDict = DotDict()
        self.librespot: LSStatus = LSStatus.CONNECTING
