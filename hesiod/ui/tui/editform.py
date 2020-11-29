from typing import Any, TYPE_CHECKING

from hesiod.ui.tui.baseform import BaseForm
from hesiod.ui.tui.recapform import RecapForm
from hesiod.ui.tui.wgtfactory import WidgetFactory

if TYPE_CHECKING:
    from hesiod.ui import TUI


class EditForm(BaseForm):
    NAME = "MAIN"
    TITLE = "Edit configuration"

    def __init__(self, parent_app: "TUI", **kwargs: Any) -> None:
        """Create new form that allows editing the run configuration.

        Args:
            parent_app: the parent TUI.
        """
        BaseForm.__init__(self, parent_app, RecapForm.NAME, name=EditForm.TITLE, **kwargs)
        key_bindings = {"^S": self.save}
        self.define_key_bindings(key_bindings)

    def create(self) -> None:
        """Add widgets to the form."""
        widgets = WidgetFactory.get_widgets(self.parent_app.template_cfg)
        for widget in widgets:
            self.add(widget[0], **widget[1])

        self.set_hint("^S: save and show recap")
