from pathlib import Path
from typing import Any, Dict, cast
import yaml

from hesiod.cfgparse.cfgparser import ConfigParser


class YAMLConfigParser(ConfigParser):
    def load_cfg(self) -> Dict[str, Any]:
        """Load config from YAML file.

        Raises:
            ValueError: if the loaded config is not of the expected type.

        Returns:
            The loaded config.
        """
        cfg: Dict[str, Any] = {}

        cfg_bases: Dict[str, Dict[str, Any]] = {}
        cfg_dirs = [p for p in self.cfg_dir_path.glob("*") if p.is_dir()]
        for cfg_dir in cfg_dirs:
            cfg_bases[cfg_dir.name] = self.load_cfg_dir(cfg_dir)

        _cfg = None
        with open(self.run_cfg_path, "rt") as f:
            _cfg = yaml.safe_load(f)

        if not self.check_cfg_type(_cfg):
            raise ValueError("Config should be a dictionary with string keys.")

        cfg = cast(Dict[str, Any], _cfg)

        for cfg_key in cfg:
            if "base" in cfg[cfg_key]:
                base_key = cfg[cfg_key]["base"]
                base_cfg = cfg_bases[cfg_key]
                for k in base_key.split("."):
                    base_cfg = base_cfg[k]

                for k in base_cfg:
                    cfg[cfg_key][k] = base_cfg[k]

                del cfg[cfg_key]["base"]

        return cfg

    def check_cfg_type(self, cfg: Any) -> bool:
        """Check if the given config is of the expected type.

        Args:
            cfg : the config to be analyzed.

        Returns:
            True if the config is the right type, False otherwise.
        """
        if not isinstance(cfg, dict):
            return False
        for key in cfg:
            if not isinstance(key, str):
                return False
        return True

    def load_cfg_dir(self, cfg_dir_path: Path) -> Dict[str, Dict[str, Any]]:
        """Load configs recursively from a given directory.

        Args:
            cfg_dir_path : the root directory.

        Returns:
            The loaded config.
        """
        cfg: Dict[str, Dict[str, Any]] = {}

        cfg_files = [p for p in cfg_dir_path.glob("*.yaml")]
        for cfg_file in cfg_files:
            with open(cfg_file, "rt") as f:
                cfg[cfg_file.stem] = yaml.safe_load(f)

        cfg_dirs = [p for p in cfg_dir_path.glob("*") if p.is_dir()]
        for cfg_dir in cfg_dirs:
            cfg[cfg_dir.name] = self.load_cfg_dir(cfg_dir)

        return cfg
