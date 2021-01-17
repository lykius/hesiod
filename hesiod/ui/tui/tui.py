from pathlib import Path
from typing import List

from asciimatics.exceptions import ResizeScreenError  # type: ignore
from asciimatics.scene import Scene  # type: ignore
from asciimatics.screen import Screen  # type: ignore

from hesiod.cfg.cfghandler import CFG_T
from hesiod.ui.tui.baseform import BaseForm
from hesiod.ui.tui.editform import EditForm
from hesiod.ui.tui.recapform import RecapForm
from hesiod.ui.ui import UI


class TUI(UI):
    def __init__(
        self,
        template_cfg: CFG_T,
        base_cfg_dir: Path,
    ) -> None:
        """Create a new terminal user interface (TUI).

        Args:
            template_file: path to the config template file.
            base_cfg_dir: path to the base configs directory.
        """
        UI.__init__(self, template_cfg, base_cfg_dir)
        self.run_cfg: CFG_T = {}

    @staticmethod
    def run(screen: Screen, scene: Scene, tui: "TUI") -> None:
        """Define the sequence of forms to be shown and play them.

        Args:
            screen: the screen where the TUI will be displayed.
            scene: the start scene.
            tui: the TUI instance.
        """
        scenes: List[Scene] = []
        scenes.append(Scene([EditForm(screen, tui)], duration=-1, name=BaseForm.EDIT_FORM))
        scenes.append(Scene([RecapForm(screen, tui)], duration=-1, name=BaseForm.RECAP_FORM))
        screen.play(scenes, stop_on_resize=True, start_scene=scene)

    def show(self) -> CFG_T:
        """Show the terminal user interface.

        Returns:
            The run configuration selected by the user.
        """
        last_scene = None
        while True:
            try:
                Screen.wrapper(TUI.run, arguments=[last_scene, self])
                break
            except ResizeScreenError as e:
                last_scene = e.scene

        return self.run_cfg
