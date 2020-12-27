import subprocess
from pathlib import Path


def test_tui(cwd: Path) -> None:
    py_script = cwd / "tests/ui/tui/emulate_tui.py"
    result = subprocess.run(["python3", str(py_script)])
    assert result.returncode == 0
