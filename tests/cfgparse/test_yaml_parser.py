from pathlib import Path

import pytest

from hesiod.cfgparse import YAMLConfigParser


def test_load_cfg_file(cifar100_cfg_file: Path) -> None:
    parser = YAMLConfigParser
    cfg = parser.load_cfg_file(cifar100_cfg_file)

    expected_keys = set(["name", "path", "splits"])
    assert expected_keys == set(cfg.keys())

    assert cfg["name"] == "cifar100"
    assert cfg["path"] == "/path/to/cifar100"
    assert isinstance(cfg["splits"], list)
    assert cfg["splits"][0] == 75
    assert cfg["splits"][1] == 15
    assert cfg["splits"][2] == 10


def test_load_cfg_file_exception(wrong_run_file: Path) -> None:
    parser = YAMLConfigParser

    with pytest.raises(ValueError):
        parser.load_cfg_file(wrong_run_file)


def test_load_cfg_dir(base_cfg_dir: Path) -> None:
    parser = YAMLConfigParser
    cfg = parser.load_cfg_dir(base_cfg_dir)

    assert isinstance(cfg, dict)
    expected_keys = set(["var", "dataset", "net", "params"])
    assert expected_keys == set(cfg.keys())

    assert isinstance(cfg["var"], dict)
    expected_keys = set(["optimizer", "lr"])
    assert expected_keys == set(cfg["var"].keys())

    assert cfg["var"]["optimizer"] == "adam"
    assert cfg["var"]["lr"] == 1e-3

    assert isinstance(cfg["dataset"], dict)
    expected_keys = set(["cifar", "imagenet"])
    assert expected_keys == set(cfg["dataset"].keys())

    assert isinstance(cfg["dataset"]["imagenet"], dict)
    expected_keys = set(["name", "path", "splits"])
    assert expected_keys == set(cfg["dataset"]["imagenet"].keys())

    assert cfg["dataset"]["imagenet"]["name"] == "imagenet"
    assert cfg["dataset"]["imagenet"]["path"] == "/path/to/imagenet"
    assert isinstance(cfg["dataset"]["imagenet"]["splits"], list)
    assert cfg["dataset"]["imagenet"]["splits"][0] == 80
    assert cfg["dataset"]["imagenet"]["splits"][1] == 10
    assert cfg["dataset"]["imagenet"]["splits"][2] == 10

    assert isinstance(cfg["dataset"]["cifar"], dict)
    expected_keys = set(["cifar10", "cifar100"])
    assert expected_keys == set(cfg["dataset"]["cifar"].keys())

    splits = {"cifar10": [70, 20, 10], "cifar100": [75, 15, 10]}
    for key in expected_keys:
        assert isinstance(cfg["dataset"]["cifar"][key], dict)
        sub_expected_keys = set(["name", "path", "splits"])
        assert sub_expected_keys == set(cfg["dataset"]["cifar"][key].keys())

        assert cfg["dataset"]["cifar"][key]["name"] == key
        assert cfg["dataset"]["cifar"][key]["path"] == "/path/to/" + key
        assert isinstance(cfg["dataset"]["cifar"][key]["splits"], list)
        assert cfg["dataset"]["cifar"][key]["splits"][0] == splits[key][0]
        assert cfg["dataset"]["cifar"][key]["splits"][1] == splits[key][1]
        assert cfg["dataset"]["cifar"][key]["splits"][2] == splits[key][2]

    assert isinstance(cfg["net"], dict)
    expected_keys = set(["resnet", "efficientnet"])
    assert expected_keys == set(cfg["net"].keys())

    assert isinstance(cfg["net"]["efficientnet"], dict)
    expected_keys = set(["name", "num_layers", "ckpt_path", "use_skip"])
    assert expected_keys == set(cfg["net"]["efficientnet"].keys())

    assert cfg["net"]["efficientnet"]["name"] == "efficientnet"
    assert cfg["net"]["efficientnet"]["num_layers"] == 20
    assert cfg["net"]["efficientnet"]["ckpt_path"] == "/path/to/efficientnet"
    assert cfg["net"]["efficientnet"]["use_skip"] is True

    assert isinstance(cfg["net"]["resnet"], dict)
    expected_keys = set(["resnet18", "resnet101"])
    assert expected_keys == set(cfg["net"]["resnet"].keys())

    num_layers = {"resnet18": 18, "resnet101": 101}
    for key in expected_keys:
        assert isinstance(cfg["net"]["resnet"][key], dict)
        sub_expected_keys = set(["name", "num_layers", "ckpt_path", "base"])
        assert sub_expected_keys == set(cfg["net"]["resnet"][key].keys())

        assert cfg["net"]["resnet"][key]["name"] == key
        assert cfg["net"]["resnet"][key]["num_layers"] == num_layers[key]
        assert cfg["net"]["resnet"][key]["ckpt_path"] == "/path/to/" + key
        assert cfg["net"]["resnet"][key]["base"] == "net.efficientnet"

    assert isinstance(cfg["params"], dict)
    expected_keys = set(["default", "test", "train"])
    assert expected_keys == set(cfg["params"].keys())

    assert isinstance(cfg["params"]["default"], dict)
    expected_keys = set(["use_bn", "use_dropout"])
    assert expected_keys == set(cfg["params"]["default"].keys())

    assert cfg["params"]["default"]["use_bn"] is True
    assert cfg["params"]["default"]["use_dropout"] is False

    assert isinstance(cfg["params"]["test"], dict)
    expected_keys = set(["base", "use_augmentation"])
    assert expected_keys == set(cfg["params"]["test"].keys())

    assert cfg["params"]["test"]["base"] == "params.default"
    assert cfg["params"]["test"]["use_augmentation"] is False

    assert isinstance(cfg["params"]["train"], dict)
    expected_keys = set(["base", "use_augmentation"])
    assert expected_keys == set(cfg["params"]["train"].keys())

    assert cfg["params"]["train"]["base"] == "params.default"
    assert cfg["params"]["train"]["use_augmentation"] is True


def test_load_cfg(base_cfg_dir: Path, complex_run_file: Path) -> None:
    parser = YAMLConfigParser
    cfg = parser.load_cfg(complex_run_file, base_cfg_dir)

    assert isinstance(cfg, dict)
    expected_keys = set(["dataset", "run_name", "net", "optimizer", "lr", "params"])
    assert expected_keys == set(cfg.keys())

    assert cfg["optimizer"] == "adam"
    assert cfg["lr"] == 5e-3
    assert cfg["run_name"] == "test"

    assert isinstance(cfg["dataset"], dict)
    expected_keys = set(["name", "path", "splits", "classes"])
    assert expected_keys == set(cfg["dataset"].keys())
    assert cfg["dataset"]["name"] == "cifar10"
    assert cfg["dataset"]["path"] == "/path/to/cifar10"
    assert cfg["dataset"]["splits"] == [70, 20, 10]
    assert cfg["dataset"]["classes"] == [1, 5, 6]

    assert isinstance(cfg["net"], dict)
    expected_keys = set(["name", "num_layers", "ckpt_path", "freeze", "use_skip"])
    assert expected_keys == set(cfg["net"].keys())
    assert cfg["net"]["name"] == "efficientnet"
    assert cfg["net"]["num_layers"] == 20
    assert cfg["net"]["ckpt_path"] == "/path/to/efficientnet"
    assert cfg["net"]["freeze"] is False
    assert cfg["net"]["use_skip"] is True

    assert isinstance(cfg["params"], dict)
    expected_keys = set(["use_bn", "use_dropout", "use_augmentation"])
    assert expected_keys == set(cfg["params"].keys())
    assert cfg["params"]["use_bn"] is True
    assert cfg["params"]["use_dropout"] is False
    assert cfg["params"]["use_augmentation"] is True


def test_replace_base() -> None:
    parser = YAMLConfigParser

    cfg = {"base": "cfg.a.b.c", "p1": 5}
    base_cfgs = {"cfg": {"a": {"b": {"c": {"p1": 1, "p2": 2, "p3": 3}}}}}
    new_cfg = parser.replace_base(cfg, base_cfgs)

    expected_keys = set(["p1", "p2", "p3"])
    assert expected_keys == set(new_cfg.keys())
    assert new_cfg["p1"] == 5
    assert new_cfg["p2"] == 2
    assert new_cfg["p3"] == 3


def test_replace_base_exception() -> None:
    parser = YAMLConfigParser

    cfg = {"base": "cfg.a.b.d", "p1": 5}
    base_cfgs = {"cfg": {"a": {"b": {"c": {"p1": 1, "p2": 2, "p3": 3}}}}}

    with pytest.raises(ValueError):
        parser.replace_base(cfg, base_cfgs)


def test_replace_bases() -> None:
    parser = YAMLConfigParser

    cfg = {"base": "bases.a", "p1": 1}
    base_cfgs = {
        "bases": {
            "a": {
                "base": "bases.b",
                "p2": 1.23,
            },
            "b": {
                "base": "bases.c",
                "p3": True,
            },
            "c": {
                "p4": (1, 2, 3),
            },
        }
    }

    new_cfg = parser.replace_bases(cfg, base_cfgs)

    expected_keys = set(["p1", "p2", "p3", "p4"])
    assert expected_keys == set(new_cfg.keys())

    assert new_cfg["p1"] == 1
    assert new_cfg["p2"] == 1.23
    assert new_cfg["p3"] is True
    assert new_cfg["p4"] == (1, 2, 3)
