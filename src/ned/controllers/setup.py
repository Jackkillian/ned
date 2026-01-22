import os
import webbrowser

import urwid
from modern_urwid import Controller, assign_widget
from urwid import Edit, Pile, Text

from ned.config import save_config
from ned.spotify.client import SpotifyTerminalClient
from ned.utils import is_librespot_installed, open_url


class SetupController(Controller):
    name = "setup"

    @assign_widget("root")
    def root(self) -> Pile: ...

    @assign_widget("widgets_pile")
    def widgets_pile(self) -> Pile: ...

    @assign_widget("id_edit")
    def id_edit(self) -> Edit: ...

    @assign_widget("error_text")
    def error_text(self) -> Text: ...

    @assign_widget("librespot")
    def librespot_text(self) -> Text: ...

    def on_load(self):
        self.root.set_focus(1)
        self.widgets_pile.set_focus(1)

        installed = is_librespot_installed()
        if installed:
            self.librespot_text.set_text("Found librespot installation")
        else:
            self.librespot_text.set_text("Error: librespot not installed")

    def help_callback(self, *args):
        open_url("https://github.com/Jackkillian/ned")

    def quit_callback(self, *args):
        raise urwid.ExitMainLoop()

    def setup_callback(self, *args):
        self.error_text.set_text("")

        installed = is_librespot_installed()
        if not installed:
            self.error_text.set_text("Please install librespot before continuing.")
            return

        id = self.id_edit.get_edit_text().strip()
        if not id or id.isspace():
            self.error_text.set_text("ID field must not be empty")
            return

        self.error_text.set_text(("info_neutral", "Loading..."))
        save_config({"id": id})

        self.error_text.set_text(("info_neutral", "Starting Librespot..."))
        self.client = SpotifyTerminalClient(id)
        result, msg = self.client.start_librespot()
        if result:
            self.error_text.set_text(("info_success", msg))
            self.manager.switch("main")
        else:
            self.error_text.set_text(msg)
