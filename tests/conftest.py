from pathlib import Path

import pytest


@pytest.fixture
def cwd() -> Path:
    return Path(".").absolute()


@pytest.fixture
def base_cfg_dir(cwd: Path) -> Path:
    return cwd / "tests/cfg"


@pytest.fixture
def simple_run_file(cwd: Path) -> Path:
    return cwd / "tests/runs/run_simple.yaml"


@pytest.fixture
def complex_run_file(cwd: Path) -> Path:
    return cwd / "tests/runs/run_complex.yaml"


@pytest.fixture
def wrong_run_file(cwd: Path) -> Path:
    return cwd / "tests/runs/run_wrong.yaml"


@pytest.fixture
def cifar10_cfg_file(cwd: Path) -> Path:
    return cwd / "tests/cfg/dataset/cifar/cifar100.yaml"
