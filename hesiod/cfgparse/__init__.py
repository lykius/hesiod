from typing import Callable, Dict

from hesiod.cfgparse.cfgparser import ConfigParser, CFGT
from hesiod.cfgparse.yamlparser import YAMLConfigParser


def get_parser(ext: str) -> Callable[..., ConfigParser]:
    parsers = [YAMLConfigParser]
    parsers_table: Dict[str, Callable[..., ConfigParser]] = {}
    for parser in parsers:
        for managed_ext in parser.get_managed_extensions():
            parsers_table[managed_ext] = parser

    ext = ext.strip()
    ext = ext[1:] if ext[0] == "." else ext
    return parsers_table[ext]


__all__ = ["get_parser", "CFGT"]
