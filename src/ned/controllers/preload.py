from modern_urwid import Controller, assign_widget
from urwid import Pile, Text

from ned.config import get_config, get_spotify_creds, save_config
from ned.spotify.client import SpotifyTerminalClient
from ned.utils import is_librespot_installed, open_url


class PreloadController(Controller):
    name = "preload"

    @assign_widget("root")
    def root(self) -> Pile: ...

    @assign_widget("info")
    def info_text(self) -> Text: ...

    def update_text(self, new_text):
        old_text = self.info_text._text
        self.info_text.set_text(f"{old_text}\n{new_text}")
        self.manager.loop.draw_screen()

    def on_enter(self):
        self.info_text.set_text("")
        self.manager.loop.set_alarm_in(0.01, self.preload)

    def preload(self, *args):
        self.update_text("Looking for librespot...")
        installed = is_librespot_installed()
        if installed:
            self.update_text("Found librespot installation.")
        else:
            self.update_text("Error: librespot not installed.")
            self.update_text(
                "Please see the setup instructions at https://github.com/Jackkillian/ned for more details."
            )
            return
        self.update_text("Connecting to API...")

        # setup all of the threads here
        client_id = get_spotify_creds()
        if client_id:
            self.client = SpotifyTerminalClient(client_id)
            self.client.setup()
            result, msg = self.client.start_librespot()  # TODO: check result
            if result:
                self.update_text("Started Librespot.")
            else:
                self.update_text(f"Error: {msg}")
        else:
            self.manager.switch("setup")
            return
        self.manager.switch("main")
