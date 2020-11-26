from pathlib import Path
import yaml


from hesiod.cfgparse.cfgparser import ConfigParser, CFGT


class YAMLConfigParser(ConfigParser):
    def read_cfg(self, cfg_file: Path) -> CFGT:
        with open(cfg_file, "rt") as f:
            cfg = yaml.safe_load(f)
        return cfg
