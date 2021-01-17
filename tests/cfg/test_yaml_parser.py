from datetime import date, timedelta
from pathlib import Path

from hesiod.cfg.yamlparser import YAMLConfigParser


def test_yaml_parser() -> None:
    cfg = {
        "a": 1,
        "b": 1.2,
        "c": True,
        "d": "test",
        "e": date.today(),
        "f": [2, 2.3, False, "hello"],
        "g": (3, 1e-4, True, "bye"),
        "h": set((4, 4.5, False, "hi")),
        "i": {
            "j": {
                "k": 5,
                "l": False,
                "m": date.today() + timedelta(days=2),
                "n": (8, 8.9, True, "good morning"),
            },
            "o": {
                "p": 1e-6,
                "q": "test for testing",
                "r": [(1, 2, 3), date.today() + timedelta(days=5), [4.1, 5.1, 1e-8]],
                "s": set((True, False, "this is a set", 10)),
            },
        },
    }

    test_file = Path("./yaml_parser_test.yaml")

    YAMLConfigParser.write_cfg(cfg, test_file)

    read_cfg = YAMLConfigParser.read_cfg_file(test_file)

    assert cfg == read_cfg

    test_file.unlink()
