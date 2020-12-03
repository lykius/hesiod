from pathlib import Path

from npyscreen import NPSAppManaged  # type: ignore

from hesiod.cfgparse import CFG_T
from hesiod.ui.tui.editform import EditForm
from hesiod.ui.tui.recapform import RecapForm
from hesiod.ui.ui import UI


class TUI(UI, NPSAppManaged):
    def __init__(self, template_file: Path, base_cfg_dir: Path) -> None:
        """Create a new terminal user interface (TUI).

        Args:
            template_file: path to the config template file.
            base_cfg_dir: path to the base configs directory.
        """
        UI.__init__(self, template_file, base_cfg_dir)
        NPSAppManaged.__init__(self)
        self.run_cfg: CFG_T = {}

    def onStart(self) -> None:
        """Register interface forms following npyscreen protocol."""
        self.addForm(EditForm.NAME, EditForm, self)
        self.addFormClass(RecapForm.NAME, RecapForm, self)

    def show(self) -> CFG_T:
        """Show the terminal user interface.

        Returns:
            The run configuration selected by the user.
        """
        self.run()
        return self.run_cfg
