import urwid
from modern_urwid import Controller, assign_widget
from urwid import Text

from ned.config import get_spotify_creds
from ned.constants import ASCII_PAUSE, ASCII_PLAY
from ned.spotify.client import SpotifyTerminalClient
from ned.spotify.session_data import SpotifySessionInfo
from ned.utils import format_milli
from ned.widgets import TimeProgressBar

DEVICE_UPDATE_INTERVAL = 5


class MainController(Controller):
    name = "main"

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

    @assign_widget("session_info_text")
    def session_info_text(self) -> Text: ...

    @assign_widget("librespot_info_text")
    def librespot_info_text(self) -> Text: ...

    def on_load(self):
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
        pass

    def on_enter(self):
        self.client = SpotifyTerminalClient()
        self.session = SpotifySessionInfo()
        self.update_track_info(self.manager.loop, None)

    def update_track_info(self, mainloop, data):
        mainloop.set_alarm_in(0.1, self.update_track_info)

        self.librespot_info_text.set_text(self.session.librespot.value)

        if display_name := self.session.user.display_name:
            text = display_name
        else:
            text = "Logging in..."
        self.session_info_text.set_text(text)

        if not (playback := self.session.playback):
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

        artists = ", ".join(map(lambda artist: artist.get("name"), item.artists))

        progress_ms = self.client.timer.get_time()
        self.progressbar.current = progress_ms
        self.progressbar.set_current_time(format_milli(progress_ms))
        self.progressbar.done = item.duration_ms
        self.progressbar.set_max_time(format_milli(item.duration_ms))

        self.status_text.set_text(
            ASCII_PAUSE if self.client.timer.running else ASCII_PLAY
        )

        text = item.name
        if item.explicit:
            text += " (E)"
        self.song_text.set_text(text)
        self.artist_text.set_text(artists)

    def on_unhandled_input(self, data):
        if data == "q":
            raise urwid.ExitMainLoop()
        elif data == "left" and (playback := self.session.playback):
            self.client.timer.decrement_time(5000)
            new_ms = self.client.timer.get_time()
            self.progressbar.current = new_ms
            self.client.seek(new_ms)
        elif data == "right" and (playback := self.session.playback):
            self.client.timer.increment_time(5000)
            new_ms = self.client.timer.get_time()
            self.progressbar.current = new_ms
            # TODO: schedule a seek with the timer ?
            self.client.seek(new_ms)
        elif data == "up":
            self.client.previous_track()
        elif data == "down":
            self.client.next_track()
        elif data == " " and (playback := self.session.playback):
            if playback.is_playing:
                self.status_text.set_text(ASCII_PLAY)
                self.client.timer.stop()
                self.client.pause()
            else:
                self.status_text.set_text(ASCII_PAUSE)
                self.client.timer.start()
                self.client.resume()
