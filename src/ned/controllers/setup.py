import urwid
from modern_urwid import Controller, assign_widget
from urwid import Edit, Pile, Text

from ned.config import save_config
from ned.custom_mu import APIController
from ned.utils import is_librespot_installed, open_url


class SetupController(APIController):
    name = "setup"

    @assign_widget("root")
    def root(self) -> Pile: ...

    @assign_widget("widgets_pile")
    def widgets_pile(self) -> Pile: ...

    @assign_widget("id_edit")
    def id_edit(self) -> Edit: ...

    @assign_widget("error_text")
    def error_text(self) -> Text: ...

    def on_load(self):
        self.root.set_focus(1)
        self.widgets_pile.set_focus(1)

    def help_callback(self, *args):
        open_url("https://github.com/Jackkillian/ned")

    def quit_callback(self, *args):
        raise urwid.ExitMainLoop()

    def setup_callback(self, *args):
        self.error_text.set_text("")

        id = self.id_edit.get_edit_text().strip()
        if not id or id.isspace():
            self.error_text.set_text("ID field must not be empty")
            return
        self.id_edit.set_edit_text("")

        self.error_text.set_text(("info_neutral", "Loading..."))
        save_config({"id": id})

        self.manager.switch("preload")
