import urwid
from modern_urwid import Controller, assign_widget
from urwid import Text

from ned.config import get_spotify_creds
from ned.spotify.client import SpotifyTerminalClient
from ned.spotify.session_data import DotDict, SpotifySessionInfo
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

    @assign_widget("session_info_text")
    def session_info_text(self) -> Text: ...

    @assign_widget("librespot_info_text")
    def librespot_info_text(self) -> Text: ...

    def on_load(self):
        creds = get_spotify_creds()
        if creds:
            self.client = SpotifyTerminalClient(*creds)
            result, msg = self.client.start_librespot()  # TODO: check result
        self.session = SpotifySessionInfo()

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
        self.update_track_info(self.manager.loop, None)

    def on_enter(self):
        if hasattr(self, "client"):
            return
        creds = get_spotify_creds()
        if creds:
            self.client = SpotifyTerminalClient(*creds)
            result, msg = self.client.start_librespot()  # TODO: check result

    def update_track_info(self, mainloop, data):
        mainloop.set_alarm_in(0.01, self.update_track_info)

        if self.session.librespot == "connecting":
            self.librespot_info_text.set_text("Connecting to Spotify...")
        elif self.session.librespot == "connected":
            self.librespot_info_text.set_text("Connected")
        elif self.session.librespot == "waiting":
            self.librespot_info_text.set_text("Waiting for Librespot...")

        if display_name := self.session.user.display_name:
            # text = f"Logged in as: {display_name}"
            text = display_name
        else:
            text = "Logging in..."
        self.session_info_text.set_text(text)

        if not (playback := self.session.playback):
            self.progressbar.current = 0
            self.song_text.set_text("<Nothing playing>")
            self.artist_text.set_text("")
            return

        if not (item := playback.item):
            self.progressbar.current = 0
            self.song_text.set_text("<Nothing playing>")
            self.artist_text.set_text("")
            return

        artists = ", ".join(map(lambda artist: artist.get("name"), item.artists))

        progress_ms = self.client.timer.get_time()
        self.progressbar.current = progress_ms
        self.progressbar.set_current_time(format_milli(progress_ms))
        self.progressbar.done = item.duration_ms
        self.progressbar.set_max_time(format_milli(item.duration_ms))

        text = item.name
        # if item.explicit:
        #     text += " (E)"
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
                self.client.timer.stop()
                self.client.pause()
            else:
                self.client.timer.start()
                self.client.resume()
