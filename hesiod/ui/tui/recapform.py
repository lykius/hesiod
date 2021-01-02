from typing import TYPE_CHECKING, Any

from asciimatics.screen import Screen

from hesiod.cfgparse import RUN_NAME_KEY
from hesiod.ui.tui.baseform import BaseForm

# from hesiod.ui.tui.wgtfactory import WidgetFactory

if TYPE_CHECKING:
    from hesiod.ui import TUI


class RecapForm(BaseForm):
    TITLE = "Recap"
    HINT = "^B: back - ^S: save"

    def __init__(self, screen: Screen, parent_app: "TUI", **kwargs: Any) -> None:
        """Create new form that show a recap of the run config.

        Args:
            screen: the screen where the form will be displayed.
            parent_app: the parent TUI.
        """
        BaseForm.__init__(self, screen, parent_app, previous_form=BaseForm.EDIT_FORM, **kwargs)

    def draw(self) -> None:
        return super().draw()

    # def create(self) -> None:
    #     """Add widgets to the form."""
    #     run_cfg = self.parent_app.run_cfg
    #     base_cfg_dir = self.parent_app.base_cfg_dir
    #     widgets = WidgetFactory.get_widgets(run_cfg, base_cfg_dir)
    #     for widget in widgets:
    #         w = widget[1]
    #         wargs = widget[2]
    #         wargs["editable"] = False
    #         self.add(w, **wargs)

    #     self.nextrely += 2
    #     run_name_widget = WidgetFactory.get_literal_widget("RUN NAME:", "")
    #     self.run_name_widget = self.add(run_name_widget[1], **run_name_widget[2])

    #     self.set_hint(RecapForm.HINT)

    # def before_exit(self) -> None:
    #     """Save run name in the parent app config when exiting the form.

    #     Raises:
    #         ValueError: if the user did not inserted a valid run name.
    #     """
    #     run_name = self.run_name_widget.get_value()
    #     if len(run_name) == 0:
    #         raise ValueError("Run name cannot be empty.")
    #     self.parent_app.run_cfg[RUN_NAME_KEY] = run_name

    def before_exit(self) -> None:
        return super().before_exit()
