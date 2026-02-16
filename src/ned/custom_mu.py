from pathlib import Path

from modern_urwid import Controller, LifecycleManager
from .session import NedSession


class APIController(Controller):
    session: NedSession

    def set_session(self, session: NedSession):
        self.session = session


class APILifecycleManager(LifecycleManager):
    def __init__(
        self,
        context,
        session: NedSession,
        loop=None,
    ):
        super().__init__(context, loop)
        self.session = session

    def register(self, layout_path: str | Path, key: str):
        super().register(layout_path, key)
        controller: APIController = self.controllers[key]
        controller.set_session(self.session)
