from pathlib import Path
from typing import Any, Dict, cast
import yaml
from copy import deepcopy

from hesiod.cfgparse.cfgparser import ConfigParser

CFGT = Dict[str, Any]


class YAMLConfigParser(ConfigParser):
    def load_cfg(self) -> CFGT:
        """Load config from YAML file.

        Returns:
            The loaded config.
        """
        cfg = self.load_cfg_file(self.run_cfg_file)

        self.base_cfgs: Dict[str, CFGT] = {}
        cfg_files = [p for p in self.base_cfg_dir.glob("*.yaml")]
        for cfg_file in cfg_files:
            self.base_cfgs[cfg_file.stem] = self.load_cfg_file(cfg_file)
        cfg_dirs = [p for p in self.base_cfg_dir.glob("*") if p.is_dir()]
        for cfg_dir in cfg_dirs:
            self.base_cfgs[cfg_dir.name] = self.load_cfg_dir(cfg_dir)

        if "base" in cfg:
            cfg = self.replace_base(cfg, "")

        for cfg_key in cfg:
            if isinstance(cfg[cfg_key], dict) and "base" in cfg[cfg_key]:
                cfg[cfg_key] = self.replace_base(cfg[cfg_key], cfg_key)

        return cfg

    def load_cfg_file(self, cfg_file: Path) -> CFGT:
        """Load config from a given file.

        Args:
            cfg_file: the file with the config.

        Raises:
            ValueError: if the config is not of the expected type.

        Returns:
            The loaded config.
        """
        cfg = None
        with open(cfg_file, "rt") as f:
            cfg = yaml.safe_load(f)

        if not isinstance(cfg, dict):
            raise ValueError(f"Error in {cfg_file.name}: Config should be a dictionary.")

        for key in cfg:
            if not isinstance(key, str):
                raise ValueError("Error in {cfg_file.name}: Config keys should be strings.")

        return cast(Dict[str, Any], cfg)

    def load_cfg_dir(self, cfg_dir: Path) -> Dict[str, CFGT]:
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

    def replace_base(self, cfg: CFGT, cfg_name: str) -> CFGT:
        """Replace base placeholder in a given config.

        Args:
            cfg: config with base placeholder.
            cfg_name: name of the config.

        Raises:
            ValueError: if it is not possible to retrieve the base config.

        Returns:
            The config with the base placeholder replaced.
        """
        if len(cfg_name) > 0:
            if cfg_name not in self.base_cfgs:
                raise ValueError(f"Config error: cannot find base {cfg_name}")
            base_cfg = self.base_cfgs[cfg_name]
        else:
            base_cfg = self.base_cfgs

        new_cfg = deepcopy(cfg)
        base_key = new_cfg["base"]

        for k in base_key.split("."):
            if k not in base_cfg:
                base_name = f"{cfg_name}.{base_key}" if len(cfg_name) > 0 else base_key
                raise ValueError(f"Config error: cannot find base {base_name}")
            base_cfg = base_cfg[k]

        for k in base_cfg:
            if k not in new_cfg:
                new_cfg[k] = base_cfg[k]

        del new_cfg["base"]

        return new_cfg
