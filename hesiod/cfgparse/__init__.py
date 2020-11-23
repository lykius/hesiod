from typing import Callable, Dict

from hesiod.cfgparse.cfgparser import ConfigParser
from hesiod.cfgparse.yamlparser import YAMLConfigParser


def get_parser(ext: str) -> Callable[..., ConfigParser]:
    parsers: Dict[str, Callable[..., ConfigParser]] = {"yaml": YAMLConfigParser}
    ext = ext.strip()
    ext = ext[1:] if ext[0] == "." else ext
    return parsers[ext]


__all__ = ["get_parser"]
