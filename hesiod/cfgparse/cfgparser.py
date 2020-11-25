from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict


class ConfigParser(ABC):
    def __init__(self, run_cfg_file: Path, base_cfg_dir: Path) -> None:
        """Create a config parser.

        Args:
            run_cfg_file: path to the run config file.
            base_cfg_dir: path to the base configs directory.
        """
        self.run_cfg_file = run_cfg_file
        self.base_cfg_dir = base_cfg_dir

    @abstractmethod
    def load_cfg(self) -> Dict[str, Any]:
        ...
