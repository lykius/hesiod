from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from asciimatics.screen import Screen

from hesiod.cfgparse.cfgparser import CFG_T
from hesiod.ui.tui.baseform import BaseForm
from hesiod.ui.tui.wgtfactory import WidgetFactory

# from hesiod.ui.tui.wgthandler import WidgetHandler

if TYPE_CHECKING:
    from hesiod.ui import TUI


class EditForm(BaseForm):
    TITLE = "Edit configuration"
    HINT = "^S: save and show recap"

    def __init__(self, screen: Screen, parent: "TUI", **kwargs: Any) -> None:
        """Create new form that allows editing the run configuration.

        Args:
            screen: the screen where the form will be displayed.
            parent: the parent TUI.
        """
        BaseForm.__init__(self, screen, parent, next_form=BaseForm.RECAP_FORM, **kwargs)

    def draw(self) -> None:
        """Add widgets to the form."""
        template_cfg = self.parent.template_cfg
        base_cfg_dir = self.parent.base_cfg_dir

        for widget in WidgetFactory.get_widgets(template_cfg, base_cfg_dir):
            self.main_layout.add_widget(widget)

        self.fix()

        # self.set_hint(EditForm.HINT)

    # def before_exit(self) -> None:
    #     """Save the config edited by the user in the parent app
    #     when exiting the form.
    #     """
    #     edited_cfg: CFG_T = {}

    #     for handler, widget in self.widgets:
    #         if handler is not None:
    #             edited_cfg = handler.update_cfg(edited_cfg, widget)

    #     parser = self.parent.cfgparser
    #     base_cfgs = parser.load_base_cfgs(self.parent.base_cfg_dir)
    #     run_cfg = parser.replace_bases(edited_cfg, base_cfgs)

    #     self.parent.run_cfg.update(run_cfg)

    def before_exit(self) -> None:
        return super().before_exit()
