from typing import Any, TYPE_CHECKING
from npyscreen import Form, TitleText  # type: ignore

if TYPE_CHECKING:
    from hesiod.ui import TUI


class RecapForm(Form):
    NAME = "RECAP"

    def __init__(self, parent_app: "TUI", **kwargs: Any) -> None:
        """Create new form that show a recap of the run config.

        Args:
            parent_app: the parent TUI.
        """
        self.parent_app = parent_app
        Form.__init__(self, **kwargs)
        key_bindings = {"^B": self.back}
        self.add_handlers(key_bindings)

    def create(self) -> None:
        """Add widgets to the form."""
        self.add(TitleText, name="cfg:", value="test")

    def back(self, *args: Any, **kwargs: Any) -> None:
        self.going_back = True
        self.parent_app.back()

    def afterEditing(self) -> None:
        """Set form to be shown when this one is closed."""
        if not self.going_back:
            self.parentApp.setNextForm(None)
        self.going_back = False
