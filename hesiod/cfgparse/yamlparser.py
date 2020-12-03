from pathlib import Path
from typing import List

import yaml

from hesiod.cfgparse.cfgparser import CFG_T, ConfigParser


class YAMLConfigParser(ConfigParser):
    @staticmethod
    def get_managed_extensions() -> List[str]:
        return ["yaml"]

    def read_cfg_file(self, cfg_file: Path) -> CFG_T:
        with open(cfg_file, "rt") as f:
            cfg = yaml.safe_load(f)
        return cfg
