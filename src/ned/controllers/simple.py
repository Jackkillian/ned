import urwid
from modern_urwid import assign_widget
from urwid import Text

from ned.constants import ASCII_PAUSE, ASCII_PLAY
from ned.custom_mu import APIController
from ned.spotify.data import TrackData
from ned.utils import format_milli
from ned.widgets import TimeProgressBar


class SimpleController(APIController):
    name = "simple"

    @assign_widget("progressbar")
    def progressbar(self) -> TimeProgressBar: ...

    @assign_widget("footer_text")
    def footer_text(self) -> Text: ...

    @assign_widget("song_text")
    def song_text(self) -> Text: ...

    @assign_widget("artist_text")
    def artist_text(self) -> Text: ...

    @assign_widget("status_text")
    def status_text(self) -> Text: ...

    @assign_widget("librespot_info_text")
    def librespot_info_text(self) -> Text: ...

    def on_load(self):
        self.update_handle = None
        # keybinds = {
        #     "q": "quit",
        #     "esc": "back",
        #     "▲": "prev track",
        #     "▼": "next track",
        #     "◄": "back 5s",
        #     "►": "forward 5s",
        # }
        # text = []
        # for key, bind in keybinds.items():
        #     text.extend([("keybind_key", f"[{key}] "), ("keybind_bind", f"{bind}   ")])
        # self.keybind_text.set_text(text)
        # self.footer_text.set_text("Press [n] to wake up Ned")

    def on_enter(self):
        self.update_track_info(self.manager.loop, None)

    def on_exit(self):
        if self.update_handle:
            self.manager.loop.remove_alarm(self.update_handle)
            self.update_handle = None

    def update_track_info(self, mainloop, data):
        self.update_handle = mainloop.set_alarm_in(0.1, self.update_track_info)

        self.librespot_info_text.set_text(self.session.data.librespot.value)

        if display_name := self.session.data.user.display_name:
            text = display_name
        else:
            text = "Logging in..."

        if not (playback := self.session.data.playback):
            self.progressbar.current = 0
            self.status_text.set_text(ASCII_PLAY)
            self.song_text.set_text("<Nothing playing>")
            self.artist_text.set_text("")
            return

        if not (item := playback.item):
            self.progressbar.current = 0
            self.status_text.set_text(ASCII_PLAY)
            self.song_text.set_text("<Nothing playing>")
            self.artist_text.set_text("")
            return

        artists = "<TODO>"
        if isinstance(item, TrackData):
            artists = ", ".join(map(lambda artist: artist.get("name"), item.artists))

        progress_ms = self.session.timer.get_time()
        self.progressbar.current = progress_ms
        self.progressbar.set_current_time(format_milli(progress_ms))

        self.progressbar.done = item.duration_ms
        self.progressbar.set_max_time(format_milli(item.duration_ms))

        self.status_text.set_text(
            ASCII_PAUSE if self.session.timer.running else ASCII_PLAY
        )

        text = item.name
        if item.explicit:
            text += " (E)"
        self.song_text.set_text(text)
        self.artist_text.set_text(artists)

    def on_unhandled_input(self, data):
        if data == "q":
            raise urwid.ExitMainLoop()
        elif data == "l":
            self.manager.switch("logs")
        elif data == "left" and (playback := self.session.data.playback):
            self.session.timer.decrement_time(5000)
            new_ms = self.session.timer.get_time()
            self.progressbar.current = new_ms
            self.session.api.seek_to_position(new_ms)
        elif data == "right" and (playback := self.session.data.playback):
            self.session.timer.increment_time(5000)
            new_ms = self.session.timer.get_time()
            self.progressbar.current = new_ms
            # TODO: schedule a seek with the timer ?
            self.session.api.seek_to_position(new_ms)
        elif data == "up":
            self.session.api.skip_to_previous()
        elif data == "down":
            self.session.api.skip_to_next()
        elif data == " " and (playback := self.session.data.playback):
            if playback.is_playing:
                self.status_text.set_text(ASCII_PLAY)
                self.session.timer.stop()
                self.session.api.pause_playback()
            else:
                self.status_text.set_text(ASCII_PAUSE)
                self.session.timer.start()
                # TODO: start timer after confirming playback starts?
                self.session.api.start_playback()
