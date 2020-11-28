from npyscreen import NPSAppManaged  # type: ignore
from pathlib import Path

from hesiod.cfgparse import CFGT
from hesiod.ui.ui import UI
from hesiod.ui.tui.editform import EditForm
from hesiod.ui.tui.recapform import RecapForm


class TUI(UI, NPSAppManaged):
    def __init__(self, template_file: Path, base_cfg_dir: Path) -> None:
        """Create a new terminal user interface (TUI).

        Args:
            template_file: path to the config template file.
            base_cfg_dir: path to the base configs directory.
        """
        UI.__init__(self, template_file, base_cfg_dir)
        NPSAppManaged.__init__(self)
        self.run_cfg: CFGT = {}

    def onStart(self) -> None:
        """Register interface forms following npyscreen protocol."""
        self.registerForm("MAIN", EditForm(self, name="Edit run config"))
        self.registerForm(RecapForm.NAME, RecapForm(self, name="Recap (^B to go back)"))

    def back(self) -> None:
        self.switchFormPrevious()

    def show(self) -> CFGT:
        """Show the terminal user interface.

        Returns:
            The run configuration selected by the user.
        """
        self.run()
        return self.run_cfg
