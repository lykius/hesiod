import pytest
from typing import Tuple
from pathlib import Path

import hesiod


@pytest.fixture
def paths() -> Tuple[Path, Path]:
    cwd = Path(".").absolute()
    base_cfg_dir = cwd / "tests/cfg"
    runs_cfg_dir = cwd / "tests/runs"
    return base_cfg_dir, runs_cfg_dir


def test_version() -> None:
    assert hesiod.__version__ == "0.1.0"


def test_args_kwargs(paths: Tuple[Path, Path]) -> None:
    base_cfg_dir = paths[0]
    run_cfg_file = paths[1] / "run_simple.yaml"

    @hesiod.main(base_cfg_dir, run_cfg_file)
    def test(a: int, b: str, c: float = 3.4) -> Tuple[int, str, float]:
        return a, b, c

    ra, rb, rc = test(2, "param_b", c=1.23456)
    assert ra == 2
    assert rb == "param_b"
    assert rc == 1.23456


def test_load_config_simple(paths: Tuple[Path, Path]) -> None:
    base_cfg_dir = paths[0]
    run_cfg_file = paths[1] / "run_simple.yaml"

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


def test_load_config_complex(paths: Tuple[Path, Path]) -> None:
    base_cfg_dir = paths[0]
    run_cfg_file = paths[1] / "run_complex.yaml"

    @hesiod.main(base_cfg_dir, run_cfg_file)
    def test() -> None:
        assert hesiod.get_param("dataset.name") == "cifar10"
        assert hesiod.get_param("dataset.path") == "/path/to/cifar10"
        assert hesiod.get_param("dataset.splits") == [70, 20, 10]
        assert hesiod.get_param("dataset.classes") == [1, 5, 6]
        assert hesiod.get_param("net.name") == "efficientnet"
        assert hesiod.get_param("net.num_layers") == 20
        assert hesiod.get_param("net.ckpt_path") == "/path/to/efficientnet"
        assert hesiod.get_param("run_name") == "test"
        assert hesiod.get_param("lr") == 5e-3
        assert hesiod.get_param("optimizer") == "adam"

    test()


def test_load_config_wrong(paths: Tuple[Path, Path]) -> None:
    base_cfg_dir = paths[0]
    run_cfg_file = paths[1] / "run_wrong.yaml"

    @hesiod.main(base_cfg_dir, run_cfg_file)
    def test() -> None:
        pass

    with pytest.raises(ValueError):
        test()


def test_get_param(paths: Tuple[Path, Path]) -> None:
    base_cfg_dir = paths[0]
    run_cfg_file = paths[1] / "run_simple.yaml"

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
