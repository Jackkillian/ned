import urwid
from modern_urwid import WidgetBuilder
from modern_urwid.compiler import create_wrapper
from urwid.canvas import CompositeCanvas


class TimeProgressBar(urwid.ProgressBar):
    def __init__(
        self,
        current: int = 0,
        done: int = 100,
    ) -> None:
        self.current_time = urwid.Text("0:00")
        self.max_time = urwid.Text("0:00", align="right")
        self.columns = urwid.Columns([self.current_time, self.max_time])

        super().__init__("pb_empty", "pb_full", current, done, "pb_satt")

    def set_current_time(self, time):
        self.current_time.set_text(time)

    def set_max_time(self, time):
        self.max_time.set_text(time)

    def render(
        self,
        size: tuple[int],  # type: ignore[override]
        focus: bool = False,
    ) -> urwid.TextCanvas:
        # pylint: disable=protected-access
        (maxcol,) = size

        c = urwid.TextCanvas(self.columns.render(size).text)

        cf = float(self.current) * maxcol / self.done
        ccol_dirty = int(cf)
        ccol = len(c._text[0][:ccol_dirty].decode("utf-8", "ignore").encode("utf-8"))
        cs = int((cf - ccol) * 8)
        if ccol < 0 or (ccol == cs == 0):
            c._attr = [[(self.normal, maxcol)]]
        elif ccol >= maxcol:
            c._attr = [[(self.complete, maxcol)]]
        elif cs and c._text[0][ccol] == 32:
            t = c._text[0]
            cenc = self.eighths[cs].encode("utf-8")
            c._text[0] = t[:ccol] + cenc + t[ccol + 1 :]
            a = []
            if ccol > 0:
                a.append((self.complete, ccol))
            a.append((self.satt, len(cenc)))
            if maxcol - ccol - 1 > 0:
                a.append((self.normal, maxcol - ccol - 1))
            c._attr = [a]
            c._cs = [[(None, len(c._text[0]))]]
        else:
            if ccol == 0:
                c._attr = [[(self.normal, maxcol)]]
            else:
                c._attr = [[(self.complete, ccol), (self.normal, maxcol - ccol)]]
        return c


class TimeProgressBarBuilder(WidgetBuilder):
    tag = "timebar"

    def build(self, **kwargs):
        return TimeProgressBar()


class CenteredButton(WidgetBuilder):
    tag = "centeredbutton"

    def build(self, **kwargs):
        text = None
        if self.node:
            text = self.node.text
        if text is None:
            text = kwargs.get("label", "")

        kwargs.update(self.resolve_attrs())
        button = urwid.Button(text, **kwargs)

        if self.node and (classes := self.node.meta_attrs.get("child_class")):
            _, hash, focus_hash = self.context.style_registry.get(
                create_wrapper(self.tag, classes=classes)
            )
            button = urwid.AttrMap(button, hash, focus_hash)

        widget = urwid.Overlay(
            urwid.Padding(button, align="center", width="pack"),
            urwid.SolidFill(" "),
            align="center",
            valign="middle",
            width="pack",
            height="pack",
        )

        return widget


class CenteredWidget(WidgetBuilder):
    tag = "centered"

    def build(self, **kwargs):
        kwargs.update(self.resolve_attrs())
        widget = urwid.Overlay(
            urwid.Padding(
                urwid.Text(""),
                **{"align": "center", "width": ("relative", 100), **kwargs},
            ),
            urwid.SolidFill(" "),
            align="center",
            valign="middle",
            width=("relative", 80),
            height="pack",
        )
        return widget

    def attach_children(
        self,
        widget,
        children,
    ):
        child = children[0][0]
        widget.top_w.original_widget = child
