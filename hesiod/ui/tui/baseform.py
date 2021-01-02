from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import NextScene, StopApplication
from asciimatics.screen import Screen
from asciimatics.widgets import Frame, Layout

if TYPE_CHECKING:
    from hesiod.ui import TUI


class BaseForm(ABC, Frame):
    EDIT_FORM = "EDIT"
    RECAP_FORM = "RECAP"
    LAST_ROW = -3

    def __init__(
        self,
        screen: Screen,
        parent: "TUI",
        next_form: Optional[str] = None,
        previous_form: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Base class for TUI forms.

        Args:
            screen: the screen where the form will be displayed.
            parent: the parent TUI.
            next_form: the form to show after this one.
            previous_form: the form shown before this one.
        """
        ABC.__init__(self)
        Frame.__init__(self, screen, int(screen.height), int(screen.width), **kwargs)
        self.set_theme("bright")
        self.parent = parent
        self.next_form = next_form
        self.previous_form = previous_form
        self.main_layout = Layout([100])
        self.add_layout(self.main_layout)
        self.draw()

    @abstractmethod
    def draw(self) -> None:
        pass

    @staticmethod
    def handle_shortcut(event: Any) -> None:
        if isinstance(event, KeyboardEvent):
            if event.key_code == Screen.ctrl("n"):
                pass

    def set_hint(self, s: str) -> None:
        """Set hint text at the bottom of the form.

        Args:
            s: the text to be shown.
        """
        # self.add(FixedText, value=s, editable=False, rely=BaseForm.LAST_ROW)
        raise NotImplementedError

    @abstractmethod
    def before_exit(self) -> None:
        """Perform final operations when exiting the form."""
        pass

    def next(self, *args: Any, **kwargs: Any) -> None:
        """Exit this form and move to the next one."""
        self.before_exit()
        if self.next_form is not None:
            raise NextScene(self.next_form)
        else:
            raise StopApplication("Stop")

    def back(self, *args: Any, **kwargs: Any) -> None:
        """Move to the previous form."""
        if self.previous_form is not None:
            raise NextScene(self.previous_form)
