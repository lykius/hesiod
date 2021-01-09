from pathlib import Path
from typing import List, Optional, Tuple, cast

from asciimatics.event import Event, KeyboardEvent, MouseEvent  # type: ignore
from asciimatics.screen import Screen  # type: ignore
from asciimatics.widgets import Divider, Layout, ListBox, Text, Widget, _TempPopup  # type: ignore


class FileBrowserDropdownPopup(_TempPopup):
    def __init__(self, parent: "CustomFileBrowser"):
        location = parent.get_location()
        if parent.frame.screen.height - location[1] < 3:
            height = min(len(parent.options) + 4, location[1] + 2)
            start_line = location[1] - height + 2
            reverse = True
        else:
            start_line = location[1] - 1
            height = min(len(parent.options) + 4, parent.frame.screen.height - location[1] + 1)
            reverse = False

        _TempPopup.__init__(
            self,
            parent.frame.screen,
            parent,
            location[0],
            start_line,
            parent.width,
            height,
        )

        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)
        self._field = Text()
        self._field.disabled = True
        divider = Divider()
        divider.disabled = True
        self._list = ListBox(
            Widget.FILL_FRAME,
            parent.options,
            add_scroll_bar=len(parent.options) > height - 4,
            on_select=self.close,
            on_change=self._link,
        )
        layout.add_widget(self._list if reverse else self._field, 0)
        layout.add_widget(divider, 0)
        layout.add_widget(self._field if reverse else self._list, 0)
        self.fix()

        selected_name = parent.selection.name if parent.selection.is_file() else "."
        for p, i in self._list.options:
            if p == selected_name:
                self._list.value = i
                break

    def _link(self) -> None:
        self._field.value = self._list.options[self._list._line][0]

    def _on_close(self, cancelled: bool) -> None:
        if not cancelled:
            selection = cast(int, self._list.value)
            self._parent.value = self._list.options[selection][0]
            self._parent.focus()


class CustomFileBrowser(Widget):
    __slots__ = ["_label", "_child", "options", "selection"]

    def __init__(self, label: str, name: str, path: str):
        Widget.__init__(self, name)
        self._label = label
        self._child: Optional[FileBrowserDropdownPopup] = None

        if not Path(path).exists():
            raise ValueError(f"{path} doesn't exist.")

        self.selection = Path(path)
        self.options = self.get_options()

    def get_options(self) -> List[Tuple[str, int]]:
        root = self.selection if self.selection.is_dir() else self.selection.parent
        subpaths = sorted(list(root.glob("*")))
        options = [(str("."), int(0)), (str(".."), int(1))]
        options.extend([(p.name, i + 2) for i, p in enumerate(subpaths)])
        return options

    @property
    def value(self) -> str:
        return str(self.selection.absolute())

    @value.setter
    def value(self, new_value: str) -> None:
        root = self.selection if self.selection.is_dir() else self.selection.parent
        if new_value == ".":
            self.selection = root
        elif new_value == "..":
            self.selection = root.parent
        else:
            self.selection = root / new_value
        self.options = self.get_options()

    def update(self, frame_no: int) -> None:
        self._draw_label()

        (colour, attr, background) = self._pick_colours("field", selected=self._has_focus)
        self._frame.canvas.print_at(
            self.value,
            self._x + self._offset,
            self._y,
            colour,
            attr,
            background,
        )

    def reset(self) -> None:
        pass

    def process_event(self, event: Optional[Event]) -> Optional[Event]:
        if event is not None:
            if isinstance(event, KeyboardEvent):
                if event.key_code in [Screen.ctrl("M"), Screen.ctrl("J"), ord(" ")]:
                    event = None
            elif isinstance(event, MouseEvent):
                if event.buttons != 0:
                    if self.is_mouse_over(event, include_label=False):
                        event = None
            if event is None:
                self._child = FileBrowserDropdownPopup(self)
                self.frame.scene.add_effect(self._child)

        return event

    def required_height(self, offset: int, width: int) -> int:
        return 1
