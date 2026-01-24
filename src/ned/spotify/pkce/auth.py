import base64
import hashlib
import secrets
import urllib.parse

from ned.utils import open_url

from .server import OAuthCallbackServer

SPOTIFY_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"


def generate_code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


class PKCEAuth:
    def __init__(
        self,
        client_id: str,
        redirect_uri: str,
        scope: str,
        host="127.0.0.1",
        port=8080,
        callback_path="/callback",
    ):
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scope = scope

        self.server = OAuthCallbackServer(
            host=host,
            port=port,
            path=callback_path,
        )

        self.code_verifier = secrets.token_urlsafe(64)
        self.code_challenge = generate_code_challenge(self.code_verifier)

    def build_auth_url(self) -> str:
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "scope": self.scope,
            "redirect_uri": self.redirect_uri,
            "code_challenge_method": "S256",
            "code_challenge": self.code_challenge,
        }
        return SPOTIFY_AUTHORIZE_URL + "?" + urllib.parse.urlencode(params)

    def authenticate(self) -> tuple[str, str]:
        self.server.start()

        auth_url = self.build_auth_url()
        open_url(auth_url)

        code = self.server.wait_for_code()
        return code, self.code_verifier
