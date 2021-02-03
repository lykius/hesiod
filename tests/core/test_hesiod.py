import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest

import hesiod.core as hcore
from hesiod import get_cfg_copy, get_out_dir, get_run_name, hcfg, hmain
from hesiod.core import _parse_args


def test_args_kwargs(base_cfg_dir: Path, simple_run_file: Path) -> None:
    @hmain(base_cfg_dir, run_cfg_file=simple_run_file, create_out_dir=False, parse_cmd_line=False)
    def test(a: int, b: str, c: float = 3.4) -> Tuple[int, str, float]:
        return a, b, c

    ra, rb, rc = test(2, "param_b", c=1.23456)
    assert ra == 2
    assert rb == "param_b"
    assert rc == 1.23456


def test_load_config_simple(base_cfg_dir: Path, simple_run_file: Path) -> None:
    @hmain(base_cfg_dir, run_cfg_file=simple_run_file, create_out_dir=False, parse_cmd_line=False)
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
    @hmain(base_cfg_dir, run_cfg_file=complex_run_file, create_out_dir=False, parse_cmd_line=False)
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
    @hmain(base_cfg_dir, run_cfg_file=wrong_run_file, create_out_dir=False, parse_cmd_line=False)
    def test() -> None:
        pass

    with pytest.raises(ValueError):
        test()


def test_hcfg(base_cfg_dir: Path, simple_run_file: Path) -> None:
    @hmain(base_cfg_dir, run_cfg_file=simple_run_file, create_out_dir=False, parse_cmd_line=False)
    def test() -> None:
        g1pa = hcfg("group_1.param_a", int)
        assert g1pa == 1 and isinstance(g1pa, int)
        g1pb = hcfg("group_1.param_b", float)
        assert g1pb == 1.2 and isinstance(g1pb, float)
        g2pc = hcfg("group_2.param_c", bool)
        assert g2pc is True and isinstance(g2pc, bool)
        g2pd = hcfg("group_2.param_d", str)
        assert g2pd == "param_d" and isinstance(g2pd, str)
        g3 = hcfg("group_3", Dict[str, Any])
        assert isinstance(g3, dict)
        g4 = hcfg("group_4", Tuple[int, bool, str])  # type: ignore
        assert g4 == (1, True, "test") and isinstance(g4, tuple)
        g5 = hcfg("group_5", List[float])
        assert g5 == [0.1, 0.1, 0.1] and isinstance(g5, list)

        with pytest.raises(TypeError):
            hcfg("group_1.param_a", str)

        with pytest.raises(TypeError):
            hcfg("group_1.param_b", int)

        with pytest.raises(TypeError):
            hcfg("group_2.param_c", str)

        with pytest.raises(TypeError):
            hcfg("group_2.param_d", bool)

        with pytest.raises(TypeError):
            hcfg("group_3", Dict[str, int])

        with pytest.raises(TypeError):
            hcfg("group_4", Tuple[int, float, int])  # type: ignore

        with pytest.raises(TypeError):
            hcfg("group_5", List[str])

    test()


def test_cfg_copy(base_cfg_dir: Path, complex_run_file: Path) -> None:
    @hmain(base_cfg_dir, run_cfg_file=complex_run_file, create_out_dir=False, parse_cmd_line=False)
    def test() -> None:
        cfg_copy = get_cfg_copy()
        assert cfg_copy == hcore._CFG
        assert id(cfg_copy) != id(hcore._CFG)

        cfg_copy["dataset"]["name"] = "new_dataset"
        assert hcore._CFG["dataset"]["name"] == "cifar10"
        assert cfg_copy != hcore._CFG

    test()


def test_out_dir(base_cfg_dir: Path, complex_run_file: Path) -> None:
    @hmain(base_cfg_dir, run_cfg_file=complex_run_file, parse_cmd_line=False)
    def test1() -> None:
        out_dir = get_out_dir()
        assert out_dir.absolute() == Path("logs/test").absolute()

    @hmain(base_cfg_dir, run_cfg_file="logs/test/run.yaml", parse_cmd_line=False)
    def test2() -> None:
        out_dir = get_out_dir()
        assert out_dir.absolute() == Path("logs/test").absolute()

    test1()
    test2()
    shutil.rmtree("logs")


def test_no_run_name(base_cfg_dir: Path, no_run_name_run_file: Path) -> None:
    @hmain(
        base_cfg_dir,
        run_cfg_file=no_run_name_run_file,
        run_name_strategy=None,
        parse_cmd_line=False,
    )
    def test() -> None:
        pass

    with pytest.raises(ValueError):
        test()


def test_default_run_name(base_cfg_dir: Path, no_run_name_run_file: Path) -> None:
    @hmain(
        base_cfg_dir,
        run_cfg_file=no_run_name_run_file,
        run_name_strategy=hcore.RUN_NAME_STRATEGY_DATE,
        create_out_dir=False,
        parse_cmd_line=False,
    )
    def test() -> None:
        now = datetime.now()
        run_name = get_run_name()
        assert run_name == now.strftime(hcore.RUN_NAME_DATE_FORMAT)

    test()


def test_run_name(base_cfg_dir: Path, complex_run_file: Path) -> None:
    @hmain(base_cfg_dir, run_cfg_file=complex_run_file, create_out_dir=False, parse_cmd_line=False)
    def test() -> None:
        run_name = get_run_name()
        assert run_name == "test"

    test()


def test_parse_args(base_cfg_dir: Path, simple_run_file: Path) -> None:
    @hmain(
        base_cfg_dir=base_cfg_dir,
        run_cfg_file=simple_run_file,
        create_out_dir=False,
        parse_cmd_line=False,
    )
    def test() -> None:
        args = [
            "group_1.param_a=5",
            "group_1.param_c=1.2345",
            "group_1.param_d=1e-4",
            "group_1.param_e=False",
            "-group_3.param_e.param_i:this is a test",
            "--group_5=[1, 2, 3]",
            '---group_6.subgroup.subsubgroup.subsubsubgroup:(1.2, "test", True)',
            '----param_7=\\|!"£$%&/()=?^€[]*@#°§<>,;.:-_+=abcABC123àèìòùç',
            "param_8:{7, 8, 9}",
            "param_9:=value",
            "param_10=:value",
            "param_11==value",
            "param_12::value",
            "#param_13:value",
            "!param_14=value",
        ]

        _parse_args(args)

        assert hcfg("group_1.param_a") == 5
        assert hcfg("group_1.param_b") == 1.2
        assert hcfg("group_1.param_c") == 1.2345
        assert hcfg("group_1.param_d") == 1e-4
        assert hcfg("group_1.param_e") is False
        assert hcfg("group_2.param_c") is True
        assert hcfg("group_2.param_d") == "param_d"
        assert hcfg("group_3.param_e.param_f") == "param_f"
        assert hcfg("group_3.param_e.param_g") == 2
        assert hcfg("group_3.param_e.param_h") == 4.56
        assert hcfg("group_3.param_e.param_i") == "this is a test"
        assert hcfg("group_4") == (1, True, "test")
        assert hcfg("group_5") == [1, 2, 3]
        assert hcfg("group_6.subgroup.subsubgroup.subsubsubgroup") == (1.2, "test", True)
        assert hcfg("param_7") == '\\|!"£$%&/()=?^€[]*@#°§<>,;.:-_+=abcABC123àèìòùç'
        assert hcfg("param_8") == {7, 8, 9}
        assert hcfg("param_9") == "=value"
        assert hcfg("param_10") == ":value"
        assert hcfg("param_11") == "=value"
        assert hcfg("param_12") == ":value"
        assert hcfg("#param_13") == "value"
        assert hcfg("!param_14") == "value"

        wrong_args = [
            "key value",
            "keyvalue",
            "key-value",
            "key_value",
            "=",
            ":",
            "-=",
            "-:",
        ]

        for arg in wrong_args:
            with pytest.raises(ValueError):
                _parse_args([arg])

    test()


def test_parse_cmd_line(base_cfg_dir: Path, complex_run_file: Path) -> None:
    sys.argv = ["test"]
    sys.argv.append("--dataset.classes=[4, 7, 8]")
    sys.argv.append("--lr=1e-10")
    sys.argv.append('--new_group.new_sub_group.new_sub_param={"t", "e", "s", "t"}')

    def check_cfg() -> None:
        assert hcfg("dataset.name") == "cifar10"
        assert hcfg("dataset.path") == "/path/to/cifar10"
        assert hcfg("dataset.splits") == [70, 20, 10]
        assert hcfg("dataset.classes") == [4, 7, 8]
        assert hcfg("net.name") == "efficientnet"
        assert hcfg("net.num_layers") == 20
        assert hcfg("net.ckpt_path") == "/path/to/efficientnet"
        assert hcfg("run_name") == "test"
        assert hcfg("lr") == 1e-10
        assert hcfg("optimizer") == "adam"
        assert hcfg("new_group.new_sub_group.new_sub_param") == {"t", "e", "s", "t"}

    @hmain(base_cfg_dir, run_cfg_file=complex_run_file)
    def test1() -> None:
        check_cfg()

    @hmain(base_cfg_dir, run_cfg_file="logs/test/run.yaml", parse_cmd_line=False)
    def test2() -> None:
        check_cfg()

    test1()
    test2()
    shutil.rmtree("logs")
