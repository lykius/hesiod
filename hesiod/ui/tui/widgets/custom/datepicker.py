from typing import Optional

from asciimatics.event import Event, KeyboardEvent, MouseEvent  # type: ignore
from asciimatics.screen import Screen  # type: ignore
from asciimatics.widgets import DatePicker, _DatePickerPopup  # type: ignore


class CustomDatePickerPopup(_DatePickerPopup):
    def _on_close(self, cancelled: bool) -> None:
        """When closing the popup, in any case, give the
        focus back to the parent widget.

        Args:
            cancelled: a flag that indicates if the selection was cancelled.
        """
        _DatePickerPopup._on_close(self, cancelled)
        self._parent.focus()


class CustomDatePicker(DatePicker):
    def process_event(self, event: Optional[Event]) -> Optional[Event]:
        """Process either a keyboard or a mouse event. If the user pressed
        enter/space or double clicked on the widget, a popup will be shown
        to allow the user to pick a date.

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
                self._child = CustomDatePickerPopup(self, year_range=self._year_range)
                self.frame.scene.add_effect(self._child)

        return event
