from abc import ABC, abstractmethod
from pathlib import Path

from hesiod.cfgparse import CFG_T


class UI(ABC):
    def __init__(self, template_cfg: CFG_T, base_cfg_dir: Path) -> None:
        ABC.__init__(self)
        self.template_cfg = template_cfg
        self.base_cfg_dir = base_cfg_dir

    @abstractmethod
    def show(self) -> CFG_T:
        ...
