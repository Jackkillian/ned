import requests

from .auth import SpotifyAuth

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
REDIRECT_URI = "http://127.0.0.1:8080/callback"


def get_oauth(client_id, scope: str):
    auth = SpotifyAuth(
        client_id=client_id,
        redirect_uri=REDIRECT_URI,
        scope=scope,
    )
    code, verifier = auth.authenticate()
    return code, verifier


def get_token_from_oauth(
    client_id: str,
    code: str,
    code_verifier: str,
) -> dict:
    res = requests.post(
        SPOTIFY_TOKEN_URL,
        data={
            "client_id": client_id,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": code_verifier,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    res.raise_for_status()
    if res.ok:
        return res.json().get("access_token")
    return res.json()
