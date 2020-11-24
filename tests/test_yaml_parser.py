from pathlib import Path

from hesiod.cfgparse import get_parser


def test_load_cfg_dir() -> None:
    cwd = Path(".").absolute()
    run_cfg_path = cwd / "tests/run_with_base.yaml"
    cfg_dir_path = cwd / "tests/cfg"

    parser = get_parser(".yaml")(run_cfg_path, cfg_dir_path)
    parser.load_cfg()
    assert True
