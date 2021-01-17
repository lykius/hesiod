from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

CFG_T = Dict[str, Any]


class ConfigParser(ABC):
    @staticmethod
    @abstractmethod
    def get_managed_extensions() -> List[str]:
        """Get file extensions managed by the parser.

        Returns:
            List of the managed extensions.
        """
        ...

    @staticmethod
    @abstractmethod
    def read_cfg_file(cfg_file: Path) -> CFG_T:
        """Read config from a file using a specific protocol.

        Args:
            cfg_file: the path to the file to be read.

        Returns:
            The config read from the given file.
        """
        ...

    @staticmethod
    @abstractmethod
    def write_cfg(cfg: CFG_T, cfg_file: Path) -> None:
        """Write config into the given file using a specific protocol.

        Args:
            cfg: the config to be saved.
            cfg_file: the path to the output file.
        """
        ...
