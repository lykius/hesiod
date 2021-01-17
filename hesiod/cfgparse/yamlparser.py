from pathlib import Path
from typing import Any, List, Tuple

from ruamel.yaml import YAML
from ruamel.yaml.constructor import SafeConstructor

from hesiod.cfgparse.cfgparser import CFG_T, ConfigParser


def construct_python_tuple(constructor: SafeConstructor, node: Any) -> Tuple:
    return tuple(constructor.construct_sequence(node))


SafeConstructor.add_constructor("tag:yaml.org,2002:python/tuple", construct_python_tuple)


class YAMLConfigParser(ConfigParser):
    @staticmethod
    def get_managed_extensions() -> List[str]:
        return ["yaml"]

    @staticmethod
    def read_cfg_file(cfg_file: Path) -> CFG_T:
        yaml = YAML(typ="safe")
        return yaml.load(cfg_file)

    @staticmethod
    def save_cfg(cfg: CFG_T, cfg_file: Path) -> None:
        yaml = YAML()
        yaml.dump(cfg, cfg_file)
