from typing import TYPE_CHECKING

from asciimatics.screen import Screen  # type: ignore
from asciimatics.widgets import Divider, Layout, Text  # type: ignore

from hesiod.cfgparse import RUN_NAME_KEY
from hesiod.ui.tui.baseform import BaseForm
from hesiod.ui.tui.wgtfactory import WidgetFactory

if TYPE_CHECKING:
    from hesiod.ui import TUI


class RecapForm(BaseForm):
    TITLE = "Recap (^B: back - ^N: save)"
    RUN_NAME = "RUN NAME:"

    def __init__(self, screen: Screen, parent_app: "TUI") -> None:
        """Create new form that show a recap of the run config.

        Args:
            screen: the screen where the form will be displayed.
            parent_app: the parent TUI.
        """
        BaseForm.__init__(
            self,
            BaseForm.RECAP_FORM,
            screen,
            parent_app,
            previous_form=BaseForm.EDIT_FORM,
        )
        self.title = RecapForm.TITLE

    def draw(self) -> None:
        run_cfg = self.parent.run_cfg
        base_cfg_dir = self.parent.base_cfg_dir

        for _, label, widget in WidgetFactory.get_widgets(run_cfg, base_cfg_dir):
            self.layout.add_widget(label, column=0)
            widget.disabled = True
            self.layout.add_widget(widget, column=-1)

        bottom_layout = Layout([100], fill_frame=True)
        self.add_layout(bottom_layout)
        bottom_layout.add_widget(Divider())
        self.run_name_widget = Text(label=RecapForm.RUN_NAME, name=RUN_NAME_KEY)
        bottom_layout.add_widget(self.run_name_widget, column=-1)

        self.fix()

    def before_exit(self) -> None:
        """Save run name in the parent app config when exiting the form.

        Raises:
            ValueError: if the user did not inserted a valid run name.
        """
        run_name = self.run_name_widget.value
        if len(run_name) == 0:
            raise ValueError("Run name cannot be empty.")
        self.parent.run_cfg[RUN_NAME_KEY] = run_name
