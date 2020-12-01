from abc import ABC, abstractmethod
from pathlib import Path

from hesiod.cfgparse import CFGT, get_parser


class UI(ABC):
    def __init__(self, template_file: Path, base_cfg_dir: Path) -> None:
        ABC.__init__(self)
        ext = template_file.name.split(".")[-1]
        self.parser = get_parser(ext)(template_file, base_cfg_dir)
        self.template_cfg = self.parser.load_cfg()
        self.base_cfg_dir = base_cfg_dir

    @abstractmethod
    def show(self) -> CFGT:
        ...
