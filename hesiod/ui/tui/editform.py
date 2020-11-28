from typing import Any, TYPE_CHECKING
from npyscreen import Form, TitleText, TitleFixedText  # type: ignore

from hesiod.ui.tui.recapform import RecapForm

if TYPE_CHECKING:
    from hesiod.ui import TUI


class EditForm(Form):
    NAME = "EDIT"

    def __init__(self, parent_app: "TUI", **kwargs: Any) -> None:
        """Create new form that allows editing the run configuration.

        Args:
            parent_app: the parent TUI.
        """
        self.parent_app = parent_app
        Form.__init__(self, **kwargs)

    def create(self) -> None:
        """Add widgets to the form."""
        tcfg = self.parent_app.template_cfg
        for cfg_key in tcfg:
            data = tcfg[cfg_key]
            if type(data) in [int, float, str, list]:
                self.add(TitleText, name=f"{cfg_key}:", value=str(tcfg[cfg_key]))
            elif isinstance(data, dict):
                self.add(TitleFixedText, name=f"{cfg_key}:")
                for subkey in data:
                    self.add(TitleText, name=f"|-{subkey}:", value=str(data[subkey]))

    def afterEditing(self) -> None:
        """Set the form to be shown when this one is closed."""
        self.parentApp.setNextForm(RecapForm.NAME)
