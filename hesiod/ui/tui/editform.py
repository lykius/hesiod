from typing import TYPE_CHECKING, List, Optional, Tuple

from asciimatics.screen import Screen  # type: ignore
from asciimatics.widgets import Layout, Widget  # type: ignore

from hesiod.cfgparse.cfgparser import CFG_T
from hesiod.ui.tui.baseform import BaseForm
from hesiod.ui.tui.widgets.wgtfactory import WidgetFactory
from hesiod.ui.tui.widgets.wgthandler import WidgetHandler

if TYPE_CHECKING:
    from hesiod.ui import TUI


class EditForm(BaseForm):
    TITLE = "Edit configuration (^N: next)"

    def __init__(self, screen: Screen, parent: "TUI") -> None:
        """Create new form that allows editing the run configuration.

        Args:
            screen: the screen where the form will be displayed.
            parent: the parent TUI.
        """
        BaseForm.__init__(self, BaseForm.EDIT_FORM, screen, parent, next_form=BaseForm.RECAP_FORM)
        self.title = EditForm.TITLE

    def draw(self) -> None:
        template_cfg = self.parent.template_cfg
        base_cfg_dir = self.parent.base_cfg_dir

        layout = Layout([100])
        self.add_layout(layout)

        self.widgets: List[Tuple[Optional[WidgetHandler], Widget]] = []
        for handler, widget in WidgetFactory.get_widgets(template_cfg, base_cfg_dir):
            layout.add_widget(widget)
            self.widgets.append((handler, widget))

        self.fix()

    def before_exit(self) -> None:
        """Save the config edited by the user in the parent app
        when exiting the form.
        """
        edited_cfg: CFG_T = {}

        for handler, widget in self.widgets:
            if handler is not None:
                edited_cfg = handler.update_cfg(edited_cfg, widget)

        parser = self.parent.cfgparser
        base_cfgs = parser.load_base_cfgs(self.parent.base_cfg_dir)
        run_cfg = parser.replace_bases(edited_cfg, base_cfgs)

        self.parent.run_cfg.update(run_cfg)
