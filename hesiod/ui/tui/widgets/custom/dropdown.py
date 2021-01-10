from typing import Optional

from asciimatics.event import Event, KeyboardEvent, MouseEvent  # type: ignore
from asciimatics.screen import Screen  # type: ignore
from asciimatics.widgets import DropdownList, _DropdownPopup  # type: ignore


class CustomDropdownPopup(_DropdownPopup):
    def _on_close(self, cancelled: bool) -> None:
        """When closing the popup, in any case, give the
        focus back to the parent widget.

        Args:
            cancelled: a flag that indicates if the selection was cancelled.
        """
        _DropdownPopup._on_close(self, cancelled)
        self._parent.focus()


class CustomDropdownList(DropdownList):
    def update(self, frame_no: int) -> None:
        """Update the widget appearance.

        Args:
            frame_no: the number of the current frame (not used).
        """
        self._draw_label()
        text = "" if self._line is None else self._options[self._line][0]
        (colour, attr, background) = self._pick_colours("field", selected=self._has_focus)
        self._frame.canvas.print_at(text, self._x + self._offset, self._y, colour, attr, background)

    def process_event(self, event: Optional[Event]) -> Optional[Event]:
        """Process either a keyboard or a mouse event. If the user pressed
        enter/space or double clicked on the widget, a popup will be shown
        to allow the user the make a selection among available options.

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
                self._child = CustomDropdownPopup(self)
                self.frame.scene.add_effect(self._child)

        return event
