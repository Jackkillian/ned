"""
See https://developer.spotify.com/documentation/web-api/concepts/scopes
"""

from enum import Enum


class Scope(Enum):
    pass


class Images(Scope):
    UGCImageUpload = "ugc-image-upload"


class SpotifyConnect(Scope):
    ReadPlaybackState = "user-read-playback-state"
    ModifyPlaybackState = "user-modify-playback-state"
    ReadCurrentlyPlaying = "user-read-currently-playing"


class Playback(Scope):
    AppRemoteControl = "app-remote-control"
    Streaming = "streaming"


class Playlists(Scope):
    ReadPrivate = "playlist-read-private"
    ReadCollaborative = "playlist-read-collaborative"
    ModifyPrivate = "playlist-modify-private"
    ModifyPublic = "playlist-modify-public"


class Follow(Scope):
    Modify = "user-follow-modify"
    Read = "user-follow-read"


class ListeningHistory(Scope):
    ReadPlaybackPosition = "user-read-playback-position"
    TopRead = "user-top-read"
    ReadRecentlyPlayed = "user-read-recently-played"


class Library(Scope):
    Modify = "user-library-modify"
    Read = "user-library-read"


class Users(Scope):
    ReadEmail = "user-read-email"
    ReadPrivate = "user-read-private"
    Personalized = "user-personalized"


class OpenAccess(Scope):
    Link = "user-soa-link"
    Unlink = "user-soa-unlink"
    ManageEntitlements = "soa-manage-entitlements"
    ManagePartner = "soa-manage-partner"
    CreatePartner = "soa-create-partner"


def get_scope(*scopes: Scope):
    return " ".join(map(lambda s: s.value, scopes))
