from enum import Enum
from typing import Any, Literal, TypedDict
from urllib.parse import urlencode

import requests

from ned.spotify.pkce import get_oauth, get_token_from_oauth

API = "https://api.spotify.com/v1"
ACCOUNT_API = "https://accounts.spotify.com/api"
REDIRECT_URI = "http://127.0.0.1:8080/callback"


class TimeRange(Enum):
    SHORT = "short_term"
    MEDIUM = "medium_term"
    LONG = "long_term"


class APIResult(TypedDict):
    ok: bool
    data: Any


# TODO: for each request, check if the status code is one of these:
# 401 (bad token)
# 403 (bad oauth request)
# 429 (the app has exceeded its rate limits)
class SpotifyAPI:
    def __init__(self, client_id, scope, redirect_uri=REDIRECT_URI):
        self.client_id = client_id
        self.scope = scope
        self.redirect_uri = redirect_uri
        self.oauth_token = None

    def _get_auth_headers(self):
        return {
            "Authorization": f"Bearer  {self.oauth_token}",
            "Content-Type": "application/json",
        }

    def _make_req(
        self,
        url: str,
        data: dict[str, Any] = {},
        type: Literal["get"] | Literal["post"] | Literal["put"] = "get",
        url_params={},
        **kw,
    ):
        if url.startswith("/"):
            url = f"{API}{url}"
        else:
            url = f"{API}/{url}"

        if type == "get":
            if data:
                url += f"?{urlencode(data)}"
            return requests.get(
                url,
                headers=self._get_auth_headers(),
                **kw,
            )
        elif type == "post":
            return requests.post(
                url,
                data,
                headers=self._get_auth_headers(),
                **kw,
            )
        elif type == "put":
            if url_params:
                url += f"?{urlencode(url_params)}"
            return requests.put(
                url,
                json=data,
                headers=self._get_auth_headers(),
                **kw,
            )

    def perform_oauth(self):
        code, verifier = get_oauth(self.client_id, self.scope)
        self.oauth_token = get_token_from_oauth(self.client_id, code, verifier)

    def is_token_valid(self, token):
        res = requests.get(
            f"{API}/me",
            headers={
                "Authorization": f"Bearer  {token}",
                "Content-Type": "application/json",
            },
        )
        return res.status_code not in [401, 403]

    def get_access_token(self, id, secret) -> APIResult:
        res = requests.post(
            f"{ACCOUNT_API}/token",
            data=f"grant_type=client_credentials&client_id={id}&client_secret={secret}",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if res.ok:
            return APIResult(ok=True, data=res.json().get("access_token"))
        return APIResult(ok=False, data=res.json())

    def get_user(self, user_id: str) -> APIResult:
        res = self._make_req(f"/users/{user_id}")
        return APIResult(ok=res.ok, data=res.json())

    def get_me(self) -> APIResult:
        res = self._make_req("/me")
        return APIResult(ok=res.ok, data=res.json())

    def get_devices(self) -> APIResult:
        res = self._make_req("/me/player/devices")
        return APIResult(ok=res.ok, data=res.json())

    def get_top(
        self,
        type: Literal["artists"] | Literal["tracks"],
        time_range: TimeRange
        | Literal["short_term"]
        | Literal["medium_term"]
        | Literal["long_term"] = "medium_term",
        limit: int = 20,
        offset: int = 0,
    ) -> APIResult:
        """Get the current user's top artists or tracks based on calculated affinity.

        :param type: The type of entity to return. Valid values: ``artists`` or ``tracks``
        :type type: str
        :param time_range: Over what time frame the affinities are computed.
            Valid values: ``long_term`` (calculated from ~1 year of data and including
            all new data as it becomes available), ``medium_term`` (approximately last 6 months),
            ``short_term`` (approximately last 4 weeks). Default: ``medium_term``
        :type time_range: str
        """
        if isinstance(time_range, TimeRange):
            time_range = time_range.value
        assert time_range in ["short_term", "medium_term", "long_term"]
        assert type in ["artists", "tracks"]
        assert 50 >= limit >= 1
        payload = {"offset": offset, "limit": limit, "time_range": time_range}
        res = self._make_req(f"/me/top/{type}", data=payload)
        if res.ok:
            return APIResult(ok=True, data=res.json().get("items"))
        return APIResult(ok=False, data=res.json())

    def transfer_playback(self, device_id: str, force_play=False):
        res = self._make_req(
            "/me/player", {"device_ids": [device_id], "play": force_play}, "put"
        )
        return APIResult(ok=res.ok, data=None)

    def get_current_playback(self):
        res = self._make_req("/me/player")
        if res.content:
            data = res.json()
        else:
            data = {}
        return APIResult(ok=res.ok, data=data)

    def pause_playback(self, device_id=None):
        if device_id:
            res = self._make_req(
                "/me/player/pause", url_params={"device_id": device_id}, type="put"
            )
        else:
            res = self._make_req("/me/player/pause", type="put")
        return APIResult(ok=res.ok, data=None)

    def start_playback(self, context_uri=None, uris=None, offset=None, device_id=None):
        data = {}
        if context_uri:
            data["context_uri"] = context_uri
        if uris:
            data["uris"] = uris
        if offset:
            data["offset"] = offset
        if device_id:
            res = self._make_req(
                "/me/player/play", data, "put", url_params={"device_id": device_id}
            )
        else:
            res = self._make_req("/me/player/play", data, "put")
        return APIResult(ok=res.ok, data=None)

    def skip_to_next(self, device_id=None):
        if device_id:
            res = self._make_req("/me/player/next", {"device_id": device_id}, "post")
        else:
            res = self._make_req("/me/player/next", type="post")
        return APIResult(ok=res.ok, data=None)

    def skip_to_previous(self, device_id=None):
        if device_id:
            res = self._make_req(
                "/me/player/previous", {"device_id": device_id}, "post"
            )
        else:
            res = self._make_req("/me/player/previous", type="post")
        return APIResult(ok=res.ok, data=None)

    def seek_to_position(self, position_ms, device_id=None):
        if device_id:
            res = self._make_req(
                "/me/player/seek",
                url_params={"position_ms": position_ms, "device_id": device_id},
                type="put",
            )
        else:
            res = self._make_req(
                "/me/player/seek", url_params={"position_ms": position_ms}, type="put"
            )
        return APIResult(ok=res.ok, data=None)

    def set_volume(self, volume_percent, device_id=None):
        if device_id:
            res = self._make_req(
                "/me/player/volume",
                url_params={"volume_percent": volume_percent, "device_id": device_id},
                type="put",
            )
        else:
            res = self._make_req(
                "/me/player/volume",
                url_params={"volume_percent": volume_percent},
                type="put",
            )
        return APIResult(ok=res.ok, data=None)
