import webbrowser

import urwid
from modern_urwid import Controller, assign_widget
from urwid import Edit, Pile, Text

from ned.config import save_config
from ned.spotify.client import SpotifyTerminalClient


class SetupController(Controller):
    name = "setup"

    @assign_widget("root")
    def root(self) -> Pile: ...

    @assign_widget("widgets_pile")
    def widgets_pile(self) -> Pile: ...

    @assign_widget("id_edit")
    def id_edit(self) -> Edit: ...

    @assign_widget("secret_edit")
    def secret_edit(self) -> Edit: ...

    @assign_widget("error_text")
    def error_text(self) -> Text: ...

    def on_load(self):
        self.root.set_focus(1)
        self.widgets_pile.set_focus(1)

    def help_callback(self, *args):
        webbrowser.open("https://github.com/Jackkillian/ned")

    def quit_callback(self, *args):
        raise urwid.ExitMainLoop()

    def setup_callback(self, node, ctx, w):
        self.error_text.set_text("")
        id = self.id_edit.get_edit_text().strip()
        secret = self.secret_edit.get_edit_text().strip()
        if (not id or id.isspace()) or (not secret or secret.isspace()):
            self.error_text.set_text("ID and secret fields must not be empty")
            return
        self.error_text.set_text(("info_neutral", "Loading..."))
        save_config({"id": id, "secret": secret})
        self.error_text.set_text(("info_neutral", "Starting Librespot..."))
        self.client = SpotifyTerminalClient(id, secret)
        result, msg = self.client.start_librespot()
        if result:
            self.error_text.set_text(("info_success", msg))
            self.manager.switch("main")
        else:
            self.error_text.set_text(msg)
