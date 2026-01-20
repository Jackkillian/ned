from enum import Enum
from typing import Any, Literal, TypedDict
from urllib.parse import urlencode

import requests

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


class SpotifyAPI:
    def __init__(self, client_id, client_secret, scope, redirect_uri=REDIRECT_URI):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.redirect_uri = redirect_uri
        self.oauth_token = None
        # TODO: cache
        # self.cache_path = ...

    def _get_auth_headers(self):
        return {
            "Authorization": f"Bearer  {self.oauth_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def _make_req(
        self,
        url: str,
        data: dict[str, str] = {},
        type: Literal["get"] | Literal["post"] = "get",
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
                data=data,
                headers=self._get_auth_headers(),
                **kw,
            )

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
