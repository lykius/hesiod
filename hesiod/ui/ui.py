from abc import ABC, abstractmethod
from pathlib import Path

from hesiod.cfg.cfghandler import CFG_T


class UI(ABC):
    def __init__(
        self,
        template_cfg: CFG_T,
        base_cfg_dir: Path,
    ) -> None:
        """Create a new user interface (UI).

        Args:
            template_file: path to the config template file.
            base_cfg_dir: path to the base configs directory.
        """
        ABC.__init__(self)
        self.template_cfg = template_cfg
        self.base_cfg_dir = base_cfg_dir

    @abstractmethod
    def show(self) -> CFG_T:
        ...
