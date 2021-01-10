from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Union

from asciimatics.event import KeyboardEvent, MouseEvent  # type: ignore
from asciimatics.exceptions import NextScene, StopApplication  # type: ignore
from asciimatics.screen import Screen  # type: ignore
from asciimatics.widgets import Frame  # type: ignore

if TYPE_CHECKING:
    from hesiod.ui import TUI


class BaseForm(ABC, Frame):
    EDIT_FORM = "EDIT"
    RECAP_FORM = "RECAP"
    LAST_ROW = -3

    def __init__(
        self,
        name: str,
        screen: Screen,
        parent: "TUI",
        previous_form: Optional[str] = None,
        next_form: Optional[str] = None,
    ) -> None:
        """Base class for TUI forms.

        Args:
            name: the name of the form.
            screen: the screen where the form will be displayed.
            parent: the parent TUI.
            previous: the name of the previous form (optional).
            next: the name of the next form (optional).
        """
        ABC.__init__(self)
        Frame.__init__(
            self,
            screen,
            int(screen.height),
            int(screen.width),
            name=name,
            on_load=self.refresh,
        )
        self.set_theme("bright")
        self.parent = parent
        self.previous_form = previous_form
        self.next_form = next_form
        self.draw()

    @abstractmethod
    def draw(self) -> None:
        """Draw the form, adding the needed widgets."""
        pass

    def refresh(self) -> None:
        """Refresh the form."""
        pass

    def process_event(self, event: Union[MouseEvent, KeyboardEvent]) -> None:
        """Process either a mouse or a keyboard event.

        Args:
            event : The event that triggered the function.
        """
        if isinstance(event, KeyboardEvent):
            if event.key_code == Screen.ctrl("n"):
                self.next()
            elif event.key_code == Screen.ctrl("b") and self.previous_form is not None:
                self.back()
        Frame.process_event(self, event)

    @abstractmethod
    def before_exit(self) -> None:
        """Perform final operations when exiting the form."""
        pass

    def next(self) -> None:
        """Exit this form and move to the next one."""
        self.before_exit()
        if self.next_form is not None:
            raise NextScene(self.next_form)
        else:
            raise StopApplication("Stop")

    def back(self) -> None:
        """Move to the previous form."""
        if self.previous_form is not None:
            raise NextScene(self.previous_form)
