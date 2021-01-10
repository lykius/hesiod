from abc import ABC, abstractmethod
from pathlib import Path
from typing import Type

from hesiod.cfgparse import CFG_T, ConfigParser


class UI(ABC):
    def __init__(
        self,
        template_cfg: CFG_T,
        base_cfg_dir: Path,
        cfgparser: Type[ConfigParser],
    ) -> None:
        """Create a new user interface (UI).

        Args:
            template_file: path to the config template file.
            base_cfg_dir: path to the base configs directory.
            cfgparser: config parser.
        """
        ABC.__init__(self)
        self.template_cfg = template_cfg
        self.base_cfg_dir = base_cfg_dir
        self.cfgparser = cfgparser

    @abstractmethod
    def show(self) -> CFG_T:
        ...
