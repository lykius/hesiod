from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict


class ConfigParser(ABC):
    def __init__(self, run_cfg_path: Path, cfg_dir: Path) -> None:
        """Create a config parser.

        Args:
            run_cfg_path : path to the run config file.
            cfg_dir : path to the configs directory.
        """
        self.run_cfg_path = run_cfg_path
        self.cfg_dir = cfg_dir

    @abstractmethod
    def load_cfg(self) -> Dict[str, Any]:
        ...
