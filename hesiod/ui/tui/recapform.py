from typing import Any, TYPE_CHECKING
from npyscreen import FixedText  # type: ignore

from hesiod.ui.tui.baseform import BaseForm

if TYPE_CHECKING:
    from hesiod.ui import TUI


class RecapForm(BaseForm):
    NAME = "RECAP"
    TITLE = "Recap"

    def __init__(self, parent_app: "TUI", **kwargs: Any) -> None:
        """Create new form that show a recap of the run config.

        Args:
            parent_app: the parent TUI.
        """
        BaseForm.__init__(self, parent_app, None, name=RecapForm.TITLE, **kwargs)
        key_bindings = {"^B": self.back, "^S": self.save}
        self.define_key_bindings(key_bindings)

    def create(self) -> None:
        """Add widgets to the form."""
        self.add(FixedText, value="^B: back - ^S: save", rely=BaseForm.LAST_ROW)
