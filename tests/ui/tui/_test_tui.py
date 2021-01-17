from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path
from time import sleep
from typing import Dict, List, Sequence, Union

from pynput.keyboard import Controller, Key, KeyCode

from hesiod.cfg import get_parser
from hesiod.cfg.cfgparser import CFG_T
from hesiod.ui.tui import TUI

INPUT_T = Union[KeyCode, str]
INPUTS_T = List[Sequence[INPUT_T]]

keymap: Dict[str, INPUT_T] = {
    "@bck": (Key.backspace,),
    "@enter": (Key.enter,),
    "@down": (Key.down,),
    "@left": (Key.left,),
    "@right": (Key.right,),
    "@tab": (Key.tab,),
    "@ctrl+s": (Key.ctrl_l, "s"),
}


def show_tui(tui: TUI) -> CFG_T:
    cfg = tui.show()
    return cfg


def emulate_keyboard(keyboard: Controller, inputs: INPUTS_T, interval: float) -> CFG_T:
    sleep(1)
    for input in inputs:
        for key in input:
            keyboard.press(key)
        for key in input:
            keyboard.release(key)
        sleep(interval)
    return {}


def test() -> None:
    cwd = Path(".").absolute()
    base_cfg_dir = Path("tests/cfg")
    complex_template_file = Path("tests/templates/complex.yaml")

    parser = get_parser(complex_template_file.suffix)
    template_cfg = parser.load_cfg(complex_template_file, base_cfg_dir)
    tui = TUI(template_cfg, base_cfg_dir, parser)

    keyboard = Controller()
    with open("tests/ui/tui/inputs.txt") as f:
        inputs = [keymap.get(s.strip(), (s.strip(),)) for s in f.readlines()]

    cfgs: List[CFG_T] = []

    with ThreadPoolExecutor(max_workers=100) as executor:
        tui_future = executor.submit(show_tui, tui)
        keyboard_future = executor.submit(emulate_keyboard, keyboard, inputs, 0.1)
        for future in as_completed([tui_future, keyboard_future]):
            cfgs.append(future.result())

    cfg = cfgs[0]
    assert cfg["optimizer"] == "adam"
    assert cfg["dataset"]["name"] == "cifar100"
    assert cfg["dataset"]["path"] == "/path/to/cifar100"
    assert cfg["dataset"]["splits"] == [75, 15, 10]
    assert cfg["net"]["name"] == "efficientnet"
    assert cfg["net"]["num_layers"] == 100
    assert cfg["net"]["ckpt_path"] == "/path/to/efficientnet"
    assert cfg["group"]["subgroupa"]["p1"] == 2
    assert cfg["group"]["subgroupa"]["p2"] == str(cwd)
    assert cfg["group"]["subgroupa"]["p3"] == str(cwd / "hesiod/ui/tui/__init__.py")
    assert cfg["group"]["subgroupb"]["p1"] == 3.2
    assert cfg["group"]["subgroupb"]["p2"]["ca"] == date.today() + timedelta(days=3)
    assert cfg["group"]["subgroupb"]["p2"]["cb"] == "b"
    assert cfg["group"]["subgroupb"]["p2"]["cc"] == (1, 4, 3)
    assert cfg["group"]["subgroupb"]["p2"]["cd"] is False
    assert cfg["today"] == date.today()
    assert cfg["date"] == date(2020, 1, 1) + timedelta(days=-2)
    assert cfg["lr"] == 0.05
    assert cfg["run_name"] == "test"

    print("Passed!")


if __name__ == "__main__":
    test()
