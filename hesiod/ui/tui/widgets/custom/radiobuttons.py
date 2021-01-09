from typing import Any, Callable, List, Optional, Tuple

from asciimatics.event import Event, KeyboardEvent  # type: ignore
from asciimatics.screen import Screen  # type: ignore
from asciimatics.widgets import RadioButtons  # type: ignore


class CustomRadioButtons(RadioButtons):
    def __init__(
        self,
        options: List[Tuple[str, int]],
        label: Optional[str] = None,
        name: Optional[str] = None,
        on_change: Optional[Callable] = None,
        **kwargs: Any,
    ):
        RadioButtons.__init__(self, options, label=label, name=name, on_change=on_change, **kwargs)
        self._value = self._options[self._selection][1]

    def update(self, frame_no: int) -> None:
        self._draw_label()

        # Decide on check char
        check_char = "•" if self._frame.canvas.unicode_aware else "X"

        # Render the list of radio buttons.
        for i, (text, _) in enumerate(self._options):
            fg, attr, bg = self._pick_colours("control", self._has_focus and i == self._selection)
            fg2, attr2, bg2 = self._pick_colours("field", self._has_focus and i == self._selection)
            check = check_char if self._value == self._options[i][1] else " "
            self._frame.canvas.print_at(
                "({}) ".format(check), self._x + self._offset, self._y + i, fg, attr, bg
            )
            self._frame.canvas.print_at(
                text, self._x + self._offset + 4, self._y + i, fg2, attr2, bg2
            )

    def process_event(self, event: Event) -> Optional[Event]:
        if isinstance(event, KeyboardEvent):
            if event.key_code == Screen.KEY_UP and self._selection > 0:
                self._selection -= 1
                return None
            elif event.key_code == Screen.KEY_DOWN and self._selection < len(self._options) - 1:
                self._selection += 1
                return None
            elif event.key_code in [Screen.ctrl("M"), Screen.ctrl("J"), ord(" ")]:
                self._value = self._options[self._selection][1]
                return None
            return event
        else:
            return RadioButtons.process_event(self, event)

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, new_value: int) -> None:
        self._value = new_value
