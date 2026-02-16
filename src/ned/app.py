import urwid
from modern_urwid import CompileContext, LifecycleManager
from urwid.event_loop.main_loop import ExitMainLoop

from ned.custom_mu import APILifecycleManager
from ned.session import NedSession
from ned.utils import RESOURCES_DIR, setup_resources


def run():
    setup_resources(True)  # TODO: for dev
    context = CompileContext(RESOURCES_DIR)
    loop = urwid.MainLoop(
        urwid.Text(""),
        palette=[
            ("pb_empty", "", "", "", "#efefef", "#000000"),
            ("pb_full", "", "", "", "#000000", "#ffb955"),
            ("pb_satt", "", "", "", "#ffb955", "#000000"),
            ("info_success", "", "", "", "#64ff64,bold", "#131313"),
            ("info_neutral", "", "", "", "#6464ff,bold", "#131313"),
            ("info_error", "", "", "", "#ff6464,bold", "#131313"),
            ("keybind_key", "", "", "", "#ff9905,bold", "#222222"),
            ("keybind_bind", "", "", "", "#df7905", "#222222"),
        ],
    )
    loop.screen.set_terminal_properties(2**24)

    manager = APILifecycleManager(context, NedSession(), loop)
    manager.register("layouts/preload.xml", "preload")
    manager.register("layouts/simple.xml", "simple")
    manager.register("layouts/setup.xml", "setup")
    manager.register("layouts/logs.xml", "logs")

    try:
        manager.run("preload")
    except (ExitMainLoop, KeyboardInterrupt):
        pass
