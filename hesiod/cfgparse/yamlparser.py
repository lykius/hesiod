from pathlib import Path
from typing import List

import yaml

from hesiod.cfgparse.cfgparser import CFG_T, ConfigParser


class YAMLConfigParser(ConfigParser):
    @staticmethod
    def get_managed_extensions() -> List[str]:
        return ["yaml"]

    @staticmethod
    def read_cfg_file(cfg_file: Path) -> CFG_T:
        with open(cfg_file, "rt") as f:
            cfg = yaml.safe_load(f)
        return cfg

    @staticmethod
    def save_cfg(cfg: CFG_T, cfg_file: Path) -> None:
        with open(cfg_file, "wt") as f:
            yaml.safe_dump(cfg, f)
