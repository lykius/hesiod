from typing import TYPE_CHECKING

from asciimatics.parsers import AsciimaticsParser  # type: ignore
from asciimatics.screen import Screen  # type: ignore
from asciimatics.widgets import Divider, Layout, Text, TextBox  # type: ignore

from hesiod.cfgparse import RUN_NAME_KEY
from hesiod.ui.tui.baseform import BaseForm
from hesiod.ui.tui.widgets.wgtfactory import WidgetFactory

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
        self.palette["disabled"] = self.palette["edit_text"]

    def draw(self) -> None:
        layout = Layout([100])
        self.add_layout(layout)

        self.recap_text_box = TextBox(1, parser=AsciimaticsParser())
        self.recap_text_box.disabled = True
        layout.add_widget(self.recap_text_box)

        layout.add_widget(Divider())

        self.run_name_widget = Text(name=RUN_NAME_KEY, label=RecapForm.RUN_NAME)
        self.run_name_widget.value = ""
        layout.add_widget(self.run_name_widget)

        self.fix()

    def refresh(self) -> None:
        label_style = (self.palette["label"][0], self.palette["label"][1])
        text_style = (self.palette["edit_text"][0], self.palette["edit_text"][1])
        recap = WidgetFactory.get_recap_text(self.parent.run_cfg, label_style, text_style)
        self.recap_text_box._required_height = len(recap)
        self.recap_text_box.value = recap

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
