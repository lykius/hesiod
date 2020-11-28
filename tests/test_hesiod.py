import pytest
from typing import Tuple
from pathlib import Path

from hesiod import __version__, hmain, hcfg, get_cfg_copy
import hesiod.core as hcore


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_args_kwargs(base_cfg_dir: Path, simple_run_file: Path) -> None:
    @hmain(base_cfg_dir, simple_run_file)
    def test(a: int, b: str, c: float = 3.4) -> Tuple[int, str, float]:
        return a, b, c

    ra, rb, rc = test(2, "param_b", c=1.23456)
    assert ra == 2
    assert rb == "param_b"
    assert rc == 1.23456


def test_load_config_simple(base_cfg_dir: Path, simple_run_file: Path) -> None:
    @hmain(base_cfg_dir, simple_run_file)
    def test() -> None:
        assert hcfg("group_1.param_a") == 1
        assert hcfg("group_1.param_b") == 1.2
        assert hcfg("group_2.param_c") is True
        assert hcfg("group_2.param_d") == "param_d"
        assert hcfg("group_3.param_e.param_f") == "param_f"
        assert hcfg("group_3.param_e.param_g") == 2
        assert hcfg("group_3.param_e.param_h") == 4.56

    test()


def test_load_config_complex(base_cfg_dir: Path, complex_run_file: Path) -> None:
    @hmain(base_cfg_dir, complex_run_file)
    def test() -> None:
        assert hcfg("dataset.name") == "cifar10"
        assert hcfg("dataset.path") == "/path/to/cifar10"
        assert hcfg("dataset.splits") == [70, 20, 10]
        assert hcfg("dataset.classes") == [1, 5, 6]
        assert hcfg("net.name") == "efficientnet"
        assert hcfg("net.num_layers") == 20
        assert hcfg("net.ckpt_path") == "/path/to/efficientnet"
        assert hcfg("run_name") == "test"
        assert hcfg("lr") == 5e-3
        assert hcfg("optimizer") == "adam"

    test()


def test_load_config_wrong(base_cfg_dir: Path, wrong_run_file: Path) -> None:
    @hmain(base_cfg_dir, wrong_run_file)
    def test() -> None:
        pass

    with pytest.raises(ValueError):
        test()


def test_hcfg(base_cfg_dir: Path, simple_run_file: Path) -> None:
    @hmain(base_cfg_dir, simple_run_file)
    def test() -> None:
        g1pa = hcfg("group_1.param_a", int)
        assert g1pa == 1 and isinstance(g1pa, int)
        g1pb = hcfg("group_1.param_b", float)
        assert g1pb == 1.2 and isinstance(g1pb, float)
        g2pc = hcfg("group_2.param_c", bool)
        assert g2pc is True and isinstance(g2pc, bool)
        g2pd = hcfg("group_2.param_d", str)
        assert g2pd == "param_d" and isinstance(g2pd, str)

        with pytest.raises(ValueError):
            hcfg("group_1.param_a", float)

        with pytest.raises(ValueError):
            hcfg("group_1.param_b", int)

        with pytest.raises(ValueError):
            hcfg("group_2.param_c", str)

        with pytest.raises(ValueError):
            hcfg("group_2.param_d", bool)

    test()


def test_cfg_copy(base_cfg_dir: Path, complex_run_file: Path) -> None:
    @hmain(base_cfg_dir, complex_run_file)
    def test() -> None:
        cfg_copy = get_cfg_copy()
        assert cfg_copy == hcore._CFG
        assert id(cfg_copy) != id(hcore._CFG)

        cfg_copy["dataset"]["name"] = "new_dataset"
        assert hcore._CFG["dataset"]["name"] == "cifar10"
        assert cfg_copy != hcore._CFG

    test()
