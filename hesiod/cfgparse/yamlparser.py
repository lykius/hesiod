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

        _cfg = None
        with open(self.run_cfg_path, "rt") as f:
            _cfg = yaml.safe_load(f)

        if not self.check_cfg_type(_cfg):
            raise ValueError("Config should be a dictionary with string keys.")

        cfg = cast(Dict[str, Any], _cfg)

        return cfg

    def check_cfg_type(self, cfg: Any) -> bool:
        return True
