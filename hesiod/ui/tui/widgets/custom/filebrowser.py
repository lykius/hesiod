from pathlib import Path
from typing import List, Optional, Tuple, cast

from asciimatics.event import Event, KeyboardEvent, MouseEvent  # type: ignore
from asciimatics.screen import Screen  # type: ignore
from asciimatics.widgets import Divider, Layout, ListBox, Text, Widget, _TempPopup  # type: ignore


class FileBrowserDropdownPopup(_TempPopup):
    def __init__(self, parent: "CustomFileBrowser"):
        """Create a popup with the list of options from the parent widget.

        Args:
            parent: the parent widget.
        """
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
        """Update the field that shows the current selection."""
        self._field.value = self._list.options[self._list._line][0]

    def _on_close(self, cancelled: bool) -> None:
        """When closing the popup, if the user confirmed, save the
        selected value in the parent widget. In any case, give the
        focus back to the parent widget.

        Args:
            cancelled: a flag that indicates if the selection was cancelled.
        """
        if not cancelled:
            selection = cast(int, self._list.value)
            self._parent.value = self._list.options[selection][0]
        self._parent.focus()


class CustomFileBrowser(Widget):
    __slots__ = ["_label", "_child", "options", "selection"]

    def __init__(self, label: str, name: str, path: str):
        """Create a widget to choose a file by browsing directories.

        Args:
            label: the label for this widget.
            name: the name of this widget.
            path: the default file/dir path.

        Raises:
            ValueError: if the given default path doesn't exist.
        """
        Widget.__init__(self, name)
        self._label = label
        self._child: Optional[FileBrowserDropdownPopup] = None

        if not Path(path).exists():
            raise ValueError(f"{path} doesn't exist.")

        self.selection = Path(path)
        self.options = self.get_options()

    def get_options(self) -> List[Tuple[str, int]]:
        """Get the list of options according to the current selection.

        Returns:
            The list of options.
        """
        root = self.selection if self.selection.is_dir() else self.selection.parent
        subpaths = sorted(list(root.glob("*")))
        options = [(str("."), int(0)), (str(".."), int(1))]
        options.extend([(p.name, i + 2) for i, p in enumerate(subpaths)])
        return options

    @property
    def value(self) -> str:
        """Get current selection as absolute path.

        Returns:
            The current selection.
        """
        return str(self.selection.absolute())

    @value.setter
    def value(self, new_value: str) -> None:
        """Set current selection.

        Args:
            new_value: the new value to set.
        """
        root = self.selection if self.selection.is_dir() else self.selection.parent
        if new_value == ".":
            self.selection = root
        elif new_value == "..":
            self.selection = root.parent
        else:
            self.selection = root / new_value
        self.options = self.get_options()

    def update(self, frame_no: int) -> None:
        """Update the widget appearance.

        Args:
            frame_no: the number of the current frame (not used).
        """
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
        """Reset the widget."""
        pass

    def process_event(self, event: Optional[Event]) -> Optional[Event]:
        """Process either a keyboard or a mouse event. If the user pressed
        enter/space or double clicked on the widget, a popup will be shown
        to allow the user the make a selection among current options.

        Args:
            event: the event to be handled.

        Returns:
            The handled event, in case somebody else needs it.
        """
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
        """Return the required height for the widget.

        Args:
            offset: here for compatibility, not used.
            width: here for compatibility, not used.

        Returns:
            The required height.
        """
        return 1
