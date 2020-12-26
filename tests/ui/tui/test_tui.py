from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from time import sleep
from typing import List, Sequence, Union

from pynput.keyboard import Controller, Key, KeyCode

from hesiod.cfgparse import get_parser
from hesiod.cfgparse.cfgparser import CFG_T
from hesiod.ui.tui import TUI

INPUT_T = Union[KeyCode, str]
INPUTS_T = List[Sequence[INPUT_T]]


def show_tui(tui: TUI) -> CFG_T:
    cfg = tui.show()
    return cfg


def emulate_keyboard(keyboard: Controller, inputs: INPUTS_T, interval: float) -> CFG_T:
    sleep(2)
    for input in inputs:
        for key in input:
            keyboard.press(key)
        for key in input:
            keyboard.release(key)
        sleep(interval)
    return {}


def test_tui(base_cfg_dir: Path, complex_template_file: Path) -> None:
    def test() -> None:
        parser = get_parser(complex_template_file.suffix)
        template_cfg = parser.load_cfg(complex_template_file, base_cfg_dir)
        tui = TUI(template_cfg, base_cfg_dir, parser)
        keyboard = Controller()
        inputs = [
            (Key.down,),
            (Key.down,),
            (Key.ctrl_l, "s"),
            ("t",),
            ("e",),
            ("s",),
            ("t",),
            (Key.ctrl_l, "s"),
        ]

        with ThreadPoolExecutor(max_workers=100) as executor:
            tui_future = executor.submit(show_tui, tui)
            keyboard_future = executor.submit(emulate_keyboard, keyboard, inputs, 1)
            for future in as_completed([tui_future, keyboard_future]):
                print(future.result())

    test()


if __name__ == "__main__":
    test_tui(Path("tests/cfg"), Path("tests/templates/complex.yaml"))
