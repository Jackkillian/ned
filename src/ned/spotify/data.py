from enum import Enum
from typing import Literal, Any
from dataclasses import dataclass


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

        item = None
        if item_dict:
            item_type = item_dict.get("type")
            if item_type == "track":
                item = TrackData.from_dict(item_dict)
            elif item_type == "episode":
                item = EpisodeData.from_dict(item_dict)

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
