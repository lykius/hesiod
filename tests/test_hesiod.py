import pytest
from typing import Tuple
from pathlib import Path

import hesiod


def test_version() -> None:
    assert hesiod.__version__ == "0.1.0"


def test_args_kwargs() -> None:
    cwd = Path(".").absolute()
    run_cfg_file = cwd / "tests/runs/run_simple.yaml"
    base_cfg_dir = cwd / "tests/cfg"

    @hesiod.main(base_cfg_dir, run_cfg_file)
    def test(a: int, b: str, c: float = 3.4) -> Tuple[int, str, float]:
        return a, b, c

    ra, rb, rc = test(2, "param_b", c=1.23456)
    assert ra == 2
    assert rb == "param_b"
    assert rc == 1.23456


def test_load_config() -> None:
    cwd = Path(".").absolute()
    run_cfg_file = cwd / "tests/runs/run_simple.yaml"
    base_cfg_dir = cwd / "tests/cfg"

    @hesiod.main(base_cfg_dir, run_cfg_file)
    def test() -> None:
        assert hesiod.get_param("group_1.param_a") == 1
        assert hesiod.get_param("group_1.param_b") == 1.2
        assert hesiod.get_param("group_2.param_c") is True
        assert hesiod.get_param("group_2.param_d") == "param_d"
        assert hesiod.get_param("group_3.param_e.param_f") == "param_f"
        assert hesiod.get_param("group_3.param_e.param_g") == 2
        assert hesiod.get_param("group_3.param_e.param_h") == 4.56

    test()


def test_get_param() -> None:
    cwd = Path(".").absolute()
    run_cfg_file = cwd / "tests/runs/run_simple.yaml"
    base_cfg_dir = cwd / "tests/cfg"

    @hesiod.main(base_cfg_dir, run_cfg_file)
    def test() -> None:
        g1pa = hesiod.get_param("group_1.param_a", int)
        assert g1pa == 1 and isinstance(g1pa, int)
        g1pb = hesiod.get_param("group_1.param_b", float)
        assert g1pb == 1.2 and isinstance(g1pb, float)
        g2pc = hesiod.get_param("group_2.param_c", bool)
        assert g2pc is True and isinstance(g2pc, bool)
        g2pd = hesiod.get_param("group_2.param_d", str)
        assert g2pd == "param_d" and isinstance(g2pd, str)

        with pytest.raises(ValueError):
            hesiod.get_param("group_1.param_a", float)

        with pytest.raises(ValueError):
            hesiod.get_param("group_1.param_b", int)

        with pytest.raises(ValueError):
            hesiod.get_param("group_2.param_c", str)

        with pytest.raises(ValueError):
            hesiod.get_param("group_2.param_d", bool)

    test()
