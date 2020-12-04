from typing import Dict, Type

from hesiod.cfgparse.cfgparser import BASE_KEY, CFG_T, RUN_NAME_KEY, ConfigParser
from hesiod.cfgparse.yamlparser import YAMLConfigParser


def get_parser(ext: str) -> Type[ConfigParser]:
    parsers = [YAMLConfigParser]
    parsers_table: Dict[str, Type[ConfigParser]] = {}
    for parser in parsers:
        for managed_ext in parser.get_managed_extensions():
            parsers_table[managed_ext] = parser

    ext = ext.strip()
    ext = ext[1:] if ext[0] == "." else ext
    return parsers_table[ext]


__all__ = ["get_parser", "CFG_T", "BASE_KEY", "RUN_NAME_KEY"]
