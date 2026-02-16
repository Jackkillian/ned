from modern_urwid import assign_widget
import urwid
from ned.custom_mu import APIController


class LogsController(APIController):
    name = "logs"

    @assign_widget("scrollbar")
    def scrollbar() -> urwid.ScrollBar: ...

    @assign_widget("listbox")
    def listbox() -> urwid.ListBox: ...

    @assign_widget("librespot_info_text")
    def librespot_info_text(self) -> urwid.Text: ...

    def on_load(self):
        self.update_handle = None

    def on_enter(self):
        self.update_handle = self.manager.loop.set_alarm_in(0.1, self.update_loop)

    def on_exit(self):
        if self.update_handle:
            self.manager.loop.remove_alarm(self.update_handle)
            self.update_handle = None

    def update_loop(self, mainloop, data):
        self.update_handle = mainloop.set_alarm_in(0.1, self.update_loop)
        self.librespot_info_text.set_text(self.session.data.librespot.value)
        if len(self.session.data.logs) != len(self.listbox.body):
            self.listbox.body.clear()
            for log in self.session.data.logs:
                style = "text_info"
                if "ERROR" in log:
                    style = "text_error"
                elif "WARN" in log:
                    style = "text_warn"
                self.listbox.body.append(urwid.Text((style, log)))
            self.listbox.set_focus(len(self.listbox.body) - 1)

    def on_unhandled_input(self, data):
        if data == "q":
            raise urwid.ExitMainLoop()
        elif data == "esc":
            self.manager.switch("simple")
