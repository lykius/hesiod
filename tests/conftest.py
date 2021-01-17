from pathlib import Path

import pytest


@pytest.fixture
def cwd() -> Path:
    return Path(".").absolute()


@pytest.fixture
def base_cfg_dir(cwd: Path) -> Path:
    return cwd / "tests/configs/bases"


@pytest.fixture
def simple_run_file(cwd: Path) -> Path:
    return cwd / "tests/configs/runs/simple.yaml"


@pytest.fixture
def complex_run_file(cwd: Path) -> Path:
    return cwd / "tests/configs/runs/complex.yaml"


@pytest.fixture
def wrong_run_file(cwd: Path) -> Path:
    return cwd / "tests/configs/runs/wrong.yaml"


@pytest.fixture
def no_run_name_run_file(cwd: Path) -> Path:
    return cwd / "tests/configs/runs/no_run_name.yaml"


@pytest.fixture
def cifar100_cfg_file(cwd: Path) -> Path:
    return cwd / "tests/configs/bases/dataset/cifar/cifar100.yaml"


@pytest.fixture
def complex_template_file(cwd: Path) -> Path:
    return cwd / "tests/configs/templates/complex.yaml"


@pytest.fixture
def simple_template_file(cwd: Path) -> Path:
    return cwd / "tests/configs/templates/simple.yaml"
