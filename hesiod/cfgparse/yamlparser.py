from pathlib import Path
from typing import Any, List, Tuple

import yaml

from hesiod.cfgparse.cfgparser import CFG_T, ConfigParser


class SafeLoader(yaml.SafeLoader):
    def construct_python_tuple(self, node: Any) -> Tuple:
        return tuple(self.construct_sequence(node))  # type: ignore


tuple_key = "tag:yaml.org,2002:python/tuple"
SafeLoader.add_constructor(tuple_key, SafeLoader.construct_python_tuple)  # type: ignore


class YAMLConfigParser(ConfigParser):
    @staticmethod
    def get_managed_extensions() -> List[str]:
        return ["yaml"]

    @staticmethod
    def read_cfg_file(cfg_file: Path) -> CFG_T:
        with open(cfg_file, "rt") as f:
            cfg = yaml.load(f, Loader=SafeLoader)
        return cfg

    @staticmethod
    def save_cfg(cfg: CFG_T, cfg_file: Path) -> None:
        with open(cfg_file, "wt") as f:
            yaml.dump(cfg, f)
