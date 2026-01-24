import urwid
from modern_urwid import CompileContext, LifecycleManager
from urwid.event_loop.main_loop import ExitMainLoop

from ned.config import get_config
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

    manager = LifecycleManager(context, loop)
    manager.register("layouts/main.xml")
    manager.register("layouts/setup.xml")

    # determine if this is the first run
    config = get_config()
    layout = "main"
    if config is None:
        layout = "setup"

    try:
        manager.run(layout)
    except (ExitMainLoop, KeyboardInterrupt):
        pass
