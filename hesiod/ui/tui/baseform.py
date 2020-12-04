from abc import ABC
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from npyscreen import FixedText  # type: ignore
from npyscreen.fmForm import FormBaseNew  # type: ignore

if TYPE_CHECKING:
    from hesiod.ui import TUI


class BaseForm(ABC, FormBaseNew):
    LAST_ROW = -3

    def __init__(self, parent_app: "TUI", next_form: Optional[str], **kwargs: Any) -> None:
        """Base class for TUI forms.

        Args:
            parent_app: the parent TUI.
            next_form: the form to show after this one.
        """
        ABC.__init__(self)
        self.parent_app = parent_app
        self.going_back = False
        self.next_form = next_form
        FormBaseNew.__init__(self, **kwargs)

    def define_key_bindings(self, key_bindings: Dict[str, Callable]) -> None:
        """Define form key bindings.

        Args:
            key_bindings: dictionary with key bindings.
        """
        self.add_handlers(key_bindings)

    def set_hint(self, s: str) -> None:
        """Set hint text at the bottom of the form.

        Args:
            s: the text to be shown.
        """
        self.add(FixedText, value=s, editable=False, rely=BaseForm.LAST_ROW)

    def before_exit(self) -> None:
        """Perform final operations when exiting the form."""
        pass

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Exit this form and move to the next one."""
        self.before_exit()
        self.parent_app.switchFormNow()

    def back(self, *args: Any, **kwargs: Any) -> None:
        """Move the previous form."""
        self.going_back = True
        self.parent_app.switchFormPrevious()

    def afterEditing(self) -> None:
        """Set the form to be shown when this one is closed."""
        if not self.going_back:
            self.parentApp.setNextForm(self.next_form)
        self.going_back = False
