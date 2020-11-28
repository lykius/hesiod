from pathlib import Path
from typing import List
import yaml


from hesiod.cfgparse.cfgparser import ConfigParser, CFGT


class YAMLConfigParser(ConfigParser):
    @classmethod
    def get_managed_extensions(cls) -> List[str]:
        return ["yaml"]

    def read_cfg(self, cfg_file: Path) -> CFGT:
        with open(cfg_file, "rt") as f:
            cfg = yaml.safe_load(f)
        return cfg
