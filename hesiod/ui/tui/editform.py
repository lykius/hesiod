from typing import TYPE_CHECKING, Any, List, Optional, Tuple
from weakref import CallableProxyType

from hesiod.cfgparse.cfgparser import CFG_T
from hesiod.ui.tui.baseform import BaseForm
from hesiod.ui.tui.recapform import RecapForm
from hesiod.ui.tui.wgtfactory import WidgetFactory
from hesiod.ui.tui.wgthandler import WidgetHandler

if TYPE_CHECKING:
    from hesiod.ui import TUI


class EditForm(BaseForm):
    NAME = "MAIN"
    TITLE = "Edit configuration"
    HINT = "^S: save and show recap"

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
        template_cfg = self.parent_app.template_cfg
        base_cfg_dir = self.parent_app.base_cfg_dir
        self.widgets: List[Tuple[Optional[WidgetHandler], CallableProxyType]] = []
        for handler, widget, wargs in WidgetFactory.get_widgets(template_cfg, base_cfg_dir):
            w = self.add(widget, **wargs)
            self.widgets.append((handler, w))

        self.set_hint(EditForm.HINT)

    def before_exit(self) -> None:
        """Save the config edited by the user in the parent app
        when exiting the form.
        """
        edited_cfg: CFG_T = {}

        for handler, widget in self.widgets:
            if handler is not None:
                edited_cfg = handler.update_cfg(edited_cfg, widget)

        parser = self.parent_app.cfgparser
        base_cfgs = parser.load_base_cfgs(self.parent_app.base_cfg_dir)
        run_cfg = parser.replace_bases(edited_cfg, base_cfgs)

        self.parent_app.run_cfg.update(run_cfg)
