import pytest
from pathlib import Path

from hesiod.cfgparse import YAMLConfigParser


def test_load_cfg_file(base_cfg_dir: Path, cifar10_cfg_file: Path) -> None:
    parser = YAMLConfigParser(Path(), base_cfg_dir)
    cfg = parser.load_cfg_file(cifar10_cfg_file)

    assert cfg["name"] == "cifar100"
    assert cfg["path"] == "/path/to/cifar100"
    assert isinstance(cfg["splits"], list)
    assert cfg["splits"][0] == 75
    assert cfg["splits"][1] == 15
    assert cfg["splits"][2] == 10


def test_load_cfg_file_exception(wrong_run_file: Path) -> None:
    parser = YAMLConfigParser(Path(), Path())

    with pytest.raises(ValueError):
        parser.load_cfg_file(wrong_run_file)


def test_load_cfg_dir(base_cfg_dir: Path) -> None:
    parser = YAMLConfigParser(Path(), Path())
    cfg = parser.load_cfg_dir(base_cfg_dir)

    assert isinstance(cfg, dict)

    expected_keys = ["var", "dataset", "net"]
    for key in expected_keys:
        assert key in cfg

    assert isinstance(cfg["var"], dict)
    assert cfg["var"]["optimizer"] == "adam"
    assert cfg["var"]["lr"] == 1e-3

    assert isinstance(cfg["dataset"], dict)
    expected_keys = ["cifar", "imagenet"]
    for key in expected_keys:
        assert key in cfg["dataset"]

    assert isinstance(cfg["dataset"]["imagenet"], dict)
    assert cfg["dataset"]["imagenet"]["name"] == "imagenet"
    assert cfg["dataset"]["imagenet"]["path"] == "/path/to/imagenet"
    assert isinstance(cfg["dataset"]["imagenet"]["splits"], list)
    assert cfg["dataset"]["imagenet"]["splits"][0] == 80
    assert cfg["dataset"]["imagenet"]["splits"][1] == 10
    assert cfg["dataset"]["imagenet"]["splits"][2] == 10

    assert isinstance(cfg["dataset"]["cifar"], dict)
    expected_keys = ["cifar10", "cifar100"]
    splits = {"cifar10": [70, 20, 10], "cifar100": [75, 15, 10]}
    for key in expected_keys:
        assert key in cfg["dataset"]["cifar"]
        assert isinstance(cfg["dataset"]["cifar"][key], dict)
        assert cfg["dataset"]["cifar"][key]["name"] == key
        assert cfg["dataset"]["cifar"][key]["path"] == "/path/to/" + key
        assert isinstance(cfg["dataset"]["cifar"][key]["splits"], list)
        assert cfg["dataset"]["cifar"][key]["splits"][0] == splits[key][0]
        assert cfg["dataset"]["cifar"][key]["splits"][1] == splits[key][1]
        assert cfg["dataset"]["cifar"][key]["splits"][2] == splits[key][2]

    assert isinstance(cfg["net"], dict)
    expected_keys = ["resnet", "efficientnet"]
    for key in expected_keys:
        assert key in cfg["net"]

    assert isinstance(cfg["net"]["efficientnet"], dict)
    assert cfg["net"]["efficientnet"]["name"] == "efficientnet"
    assert cfg["net"]["efficientnet"]["num_layers"] == 20
    assert cfg["net"]["efficientnet"]["ckpt_path"] == "/path/to/efficientnet"

    assert isinstance(cfg["net"]["resnet"], dict)
    expected_keys = ["resnet18", "resnet101"]
    num_layers = {"resnet18": 18, "resnet101": 101}
    for key in expected_keys:
        assert key in cfg["net"]["resnet"]
        assert cfg["net"]["resnet"][key]["name"] == key
        assert cfg["net"]["resnet"][key]["num_layers"] == num_layers[key]
        assert cfg["net"]["resnet"][key]["ckpt_path"] == "/path/to/" + key


def test_load_cfg(base_cfg_dir: Path, complex_run_file: Path) -> None:
    parser = YAMLConfigParser(complex_run_file, base_cfg_dir)
    cfg = parser.load_cfg()

    assert isinstance(cfg, dict)
    expected_keys = ["dataset", "run_name", "net", "optimizer", "lr"]
    for key in expected_keys:
        assert key in cfg

    assert cfg["optimizer"] == "adam"
    assert cfg["lr"] == 5e-3

    assert cfg["dataset"]["name"] == "cifar10"
    assert cfg["dataset"]["path"] == "/path/to/cifar10"
    assert cfg["dataset"]["splits"] == [70, 20, 10]
    assert cfg["dataset"]["classes"] == [1, 5, 6]

    assert cfg["net"]["name"] == "efficientnet"
    assert cfg["net"]["num_layers"] == 20
    assert cfg["net"]["ckpt_path"] == "/path/to/efficientnet"
    assert cfg["net"]["freeze"] is False


def test_replace_base() -> None:
    parser = YAMLConfigParser(Path(), Path())

    cfg = {"base": "cfg.a.b.c", "p1": 5}
    base_cfgs = {"cfg": {"a": {"b": {"c": {"p1": 1, "p2": 2, "p3": 3}}}}}
    parser.base_cfgs = base_cfgs
    new_cfg = parser.replace_base(cfg)

    expected_keys = ["p1", "p2", "p3"]
    for key in expected_keys:
        assert key in new_cfg
    assert new_cfg["p1"] == 5
    assert new_cfg["p2"] == 2
    assert new_cfg["p3"] == 3

    cfg = {"base": "cfg.a.b.c", "p1": 5}
    base_cfgs = {"cfg": {"a": {"b": {"c": {"p1": 1, "p2": 2, "p3": 3}}}}}
    parser.base_cfgs = base_cfgs
    new_cfg = parser.replace_base(cfg)

    expected_keys = ["p1", "p2", "p3"]
    for key in expected_keys:
        assert key in new_cfg
    assert new_cfg["p1"] == 5
    assert new_cfg["p2"] == 2
    assert new_cfg["p3"] == 3


def test_replace_base_exception() -> None:
    parser = YAMLConfigParser(Path(), Path())

    cfg = {"base": "cfg.a.b.d", "p1": 5}
    base_cfgs = {"cfg": {"a": {"b": {"c": {"p1": 1, "p2": 2, "p3": 3}}}}}
    parser.base_cfgs = base_cfgs

    with pytest.raises(ValueError):
        parser.replace_base(cfg)

    with pytest.raises(ValueError):
        parser.replace_base(cfg)

    with pytest.raises(ValueError):
        parser.replace_base(cfg)
