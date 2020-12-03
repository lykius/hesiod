from abc import ABC, abstractmethod
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

CFG_T = Dict[str, Any]
BASE_KEY = "base"
RUN_NAME_KEY = "run_name"


class ConfigParser(ABC):
    def __init__(self, run_cfg_file: Path, base_cfg_dir: Path) -> None:
        """Create a config parser.

        Args:
            run_cfg_file: path to the run config file.
            base_cfg_dir: path to the base configs directory.
        """
        ABC.__init__(self)
        self.run_cfg_file = run_cfg_file
        self.base_cfg_dir = base_cfg_dir

    @staticmethod
    @abstractmethod
    def get_managed_extensions() -> List[str]:
        """Get file extensions managed by the parser.

        Returns:
            List of the managed extensions.
        """
        ...

    @abstractmethod
    def read_cfg_file(self, cfg_file: Path) -> CFG_T:
        """Read config from a file using a specific protocol.

        Args:
            cfg_file: the path to the file to be read.

        Returns:
            The config read from the given file.
        """
        ...

    def load_cfg(self) -> CFG_T:
        """Load config replacing "bases" with proper values.

        Returns:
            The loaded config.
        """
        cfg = self.load_cfg_file(self.run_cfg_file)

        self.base_cfgs: Dict[str, CFG_T] = {}
        cfg_files = [p for p in self.base_cfg_dir.glob("*.yaml")]
        for cfg_file in cfg_files:
            self.base_cfgs[cfg_file.stem] = self.load_cfg_file(cfg_file)
        cfg_dirs = [p for p in self.base_cfg_dir.glob("*") if p.is_dir()]
        for cfg_dir in cfg_dirs:
            self.base_cfgs[cfg_dir.name] = self.load_cfg_dir(cfg_dir)

        if BASE_KEY in cfg:
            cfg = self.replace_base(cfg)

        for cfg_key in cfg:
            if isinstance(cfg[cfg_key], dict) and BASE_KEY in cfg[cfg_key]:
                cfg[cfg_key] = self.replace_base(cfg[cfg_key])

        return cfg

    def load_cfg_file(self, cfg_file: Path) -> CFG_T:
        """Load config from a given file.

        Args:
            cfg_file: the file with the config.

        Raises:
            ValueError: if the config is not of the expected type.

        Returns:
            The loaded config.
        """
        cfg = self.read_cfg_file(cfg_file)

        if not isinstance(cfg, dict):
            raise ValueError(f"Error in {cfg_file.name}: Config should be a dictionary.")

        for key in cfg:
            if not isinstance(key, str):
                raise ValueError("Error in {cfg_file.name}: Config keys should be strings.")

        return cfg

    def load_cfg_dir(self, cfg_dir: Path) -> Dict[str, CFG_T]:
        """Load configs recursively from a given directory.

        Args:
            cfg_dir: the config directory.

        Returns:
            The loaded config.
        """
        cfg: Dict[str, Dict[str, Any]] = {}

        cfg_files = [p for p in cfg_dir.glob("*.yaml")]
        for cfg_file in cfg_files:
            cfg[cfg_file.stem] = self.load_cfg_file(cfg_file)

        cfg_subdirs = [p for p in cfg_dir.glob("*") if p.is_dir()]
        for cfg_subdir in cfg_subdirs:
            cfg[cfg_subdir.name] = self.load_cfg_dir(cfg_subdir)

        return cfg

    def replace_base(self, cfg: CFG_T) -> CFG_T:
        """Replace base placeholder in a given config.

        Args:
            cfg: config with base placeholder.

        Raises:
            ValueError: if it is not possible to retrieve the base config.

        Returns:
            The config with the base placeholder replaced.
        """
        new_cfg = deepcopy(cfg)
        base_key = new_cfg[BASE_KEY]
        base_cfg = self.base_cfgs

        for k in base_key.split("."):
            if k not in base_cfg:
                raise ValueError(f"Config error: cannot find base {base_key}")
            base_cfg = base_cfg[k]

        for k in base_cfg:
            if k not in new_cfg:
                new_cfg[k] = base_cfg[k]

        del new_cfg[BASE_KEY]

        return new_cfg
