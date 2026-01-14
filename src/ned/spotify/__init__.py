from typing import Literal
from urllib.parse import urlencode

import requests

ACCOUNT_API = "https://accounts.spotify.com/api"
API = "https://api.spotify.com/v1"


def get_access_token(id, secret):
    res = requests.post(
        f"{ACCOUNT_API}/token",
        data=f"grant_type=client_credentials&client_id={id}&client_secret={secret}",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    res.raise_for_status()
    if res.ok:
        return res.json().get("access_token")
    return res.json()


def get_user(token, id):
    res = requests.get(
        f"{API}/users/{id}",
        headers={"Authorization": f"Bearer  {token}"},
    )
    res.raise_for_status()
    return res.json()


def get_me(oauth_token):
    res = requests.get(
        f"{API}/me",
        headers={"Authorization": f"Bearer  {oauth_token}"},
    )
    res.raise_for_status()
    return res.json()


def get_top(
    oauth_token,
    type: Literal["artists"] | Literal["tracks"],
    time_range: Literal["short_term"]
    | Literal["medium_term"]
    | Literal["long_term"] = "medium_term",
    limit: int = 20,
    offset: int = 0,
):
    """Get the current user's top artists or tracks based on calculated affinity.

    :param type: The type of entity to return. Valid values: ``artists`` or ``tracks``
    :type type: str
    :param time_range: Over what time frame the affinities are computed.
        Valid values: ``long_term`` (calculated from ~1 year of data and including
        all new data as it becomes available), ``medium_term`` (approximately last 6 months),
        ``short_term`` (approximately last 4 weeks). Default: ``medium_term``
    :type time_range: str
    """
    assert 50 >= limit >= 1
    params = urlencode({"offset": offset, "limit": limit, "time_range": time_range})
    res = requests.get(
        f"{API}/me/top/{type}?{params}",
        headers={"Authorization": f"Bearer  {oauth_token}"},
    )
    res.raise_for_status()
    if res.ok:
        return res.json().get("items")
    return res.json()
