import re
from abc import ABC, abstractmethod
from ast import literal_eval
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from asciimatics.widgets import DatePicker, DropdownList, FileBrowser, Label, RadioButtons, Text
from asciimatics.widgets import Widget

from hesiod.cfgparse import CFG_T

# from hesiod.ui.tui.wgthandler import BaseWidgetHandler, BoolWidgetHandler, OptionsWidgetHandler
# from hesiod.ui.tui.wgthandler import WidgetHandler


class WidgetParser(ABC):
    PREFIX = "    "
    DATE_PATTERN = r"^@DATE$"
    DEFAULT_DATE_PATTERN = r"^@DATE\((today|Today|TODAY|\d{4}-\d{2}-\d{2})\)$"
    FILE_PATTERN = r"^@FILE$"
    DEFAULT_FILE_PATTERN = r"^@FILE\(.+\)$"
    BASE_PATTERN = r"^@BASE\([0-9A-Za-z_.]+\)$"
    OPTIONS_PATTERN = r"^@OPTIONS\(.+\)$"
    BOOL_PATTERN = r"^@BOOL\((true|True|TRUE|false|False|FALSE)\)$"

    @staticmethod
    def match(s: str, pattern: str) -> bool:
        """Check if a given string matches a pattern.

        Args:
            s: the string to be checked.
            pattern: the pattern to check.

        Returns:
            True if the given string matches the patter, False otherwise.
        """
        return bool(re.match(pattern, s))

    @staticmethod
    @abstractmethod
    def can_handle(x: Any) -> bool:
        """Check if the input config can be handled by this parser.

        Args:
            x: the input config.

        Returns:
            True if the input config is int, float, str or list.
        """
        ...

    @staticmethod
    @abstractmethod
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[Widget]:
        """Parse a literal config and return a list with the needed widgets.

        Args:
            cfg_key: name of the config.
            label_prefix: prefix for the name of the config.
            cfg_value: literal value of the config.
            base_cfg_dir: path to the base configs directory.

        Returns:
            A list with the widgets for the given config.
        """
        ...


class LiteralWidgetParser(WidgetParser):
    @staticmethod
    def can_handle(x: Any) -> bool:
        return type(x) in [int, float, str, bool, list, tuple, set, date]

    @staticmethod
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[Widget]:
        # handler = WidgetHandler(cfg_key)

        label = cfg_key.split(".")[-1]
        label = f"{label_prefix}{label}:"
        widget = Text(label=label, name=cfg_key)
        widget.value = str(cfg_value)

        return [widget]


class DateWidgetParser(WidgetParser):
    TODAY = "today"
    FORMAT = r"%Y-%M-%d"
    HINT = "(ENTER to select a date)"

    @staticmethod
    def can_handle(x: Any) -> bool:
        if isinstance(x, str):
            can_handle = WidgetParser.match(x, WidgetParser.DATE_PATTERN)
            can_handle = can_handle or WidgetParser.match(x, WidgetParser.DEFAULT_DATE_PATTERN)
            return can_handle
        return False

    @staticmethod
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[Widget]:
        # handler = WidgetHandler(cfg_key)

        label = cfg_key.split(".")[-1]
        label = f"{label_prefix}{label} {DateWidgetParser.HINT}:"

        widget = DatePicker(label=label, name=cfg_key)

        if WidgetParser.match(cfg_value, WidgetParser.DEFAULT_DATE_PATTERN):
            default = cfg_value.split("(")[-1].split(")")[0]
            default = default.lower()

            value = None
            if default == DateWidgetParser.TODAY:
                value = date.today()
            else:
                value = datetime.strptime(default, DateWidgetParser.FORMAT).date()

            if value is not None:
                widget.value = value

        return [widget]


class FileWidgetParser(WidgetParser):
    HINT = "(TAB for autocompletion)"

    @staticmethod
    def can_handle(x: Any) -> bool:
        if isinstance(x, str):
            can_handle = WidgetParser.match(x, WidgetParser.FILE_PATTERN)
            can_handle = can_handle or WidgetParser.match(x, WidgetParser.DEFAULT_FILE_PATTERN)
            return can_handle
        return False

    @staticmethod
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[Widget]:
        # handler = WidgetHandler(cfg_key)

        label = cfg_key.split(".")[-1]
        label = f"{label_prefix}{label} {FileWidgetParser.HINT}:"

        if WidgetParser.match(cfg_value, WidgetParser.DEFAULT_FILE_PATTERN):
            default = cfg_value.split("(")[-1].split(")")[0]
            value = default.lower()
        else:
            value = str(Path(".").absolute())

        widget = FileBrowser(2, value, name=cfg_key)

        return [widget]


class BoolWidgetParser(WidgetParser):
    TRUE = "true"
    FALSE = "false"

    @staticmethod
    def can_handle(x: Any) -> bool:
        return isinstance(x, str) and WidgetParser.match(x, WidgetParser.BOOL_PATTERN)

    @staticmethod
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[Widget]:
        # handler = BoolWidgetHandler(cfg_key)

        default = cfg_value.split("(")[-1].split(")")[0]
        default = str(default).lower()
        values = [(BoolWidgetParser.TRUE, 0), (BoolWidgetParser.FALSE, 1)]

        label = cfg_key.split(".")[-1]
        label = f"{label_prefix}{label}:"

        widget = RadioButtons(values, label=label, name=cfg_key)

        return [widget]


class OptionsWidgetParser(WidgetParser):
    @staticmethod
    def can_handle(x: Any) -> bool:
        return isinstance(x, str) and WidgetParser.match(x, WidgetParser.OPTIONS_PATTERN)

    @staticmethod
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[Widget]:
        # handler = OptionsWidgetHandler(cfg_key)

        options = cfg_value.split("(")[-1].split(")")[0]
        values = [(option.strip(), i) for i, option in enumerate(options.split(","))]

        label = cfg_key.split(".")[-1]
        label = f"{label_prefix}{label}:"

        widget = RadioButtons(values, label=label, name=cfg_key)

        return [widget]


class BaseWidgetParser(WidgetParser):
    @staticmethod
    def can_handle(x: Any) -> bool:
        return isinstance(x, str) and WidgetParser.match(x, WidgetParser.BASE_PATTERN)

    @staticmethod
    def get_files_list(dir: Path) -> List[Path]:
        """Returns the list of files contained in the given directory
        and in all its subdirectories.

        Args:
            dir: the directory to be searched.

        Returns:
            The list of files.
        """
        files: List[Path] = []
        children = [p for p in dir.glob("*")]
        for p in children:
            if p.is_file():
                files.append(p)
            elif p.is_dir():
                files.extend(BaseWidgetParser.get_files_list(p))
        return files

    @staticmethod
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[Widget]:
        base_key = cfg_value.split("(")[-1].split(")")[0]
        base_keys = base_key.split(".")

        root = base_cfg_dir
        for k in base_keys:
            subdirs = [d for d in root.glob(k) if d.is_dir()]
            if len(subdirs) != 1:
                raise ValueError(f"Cannot find base key {base_key}")
            root = subdirs[0]

        files = sorted(BaseWidgetParser.get_files_list(root))
        values = [(f.stem, i) for i, f in enumerate(files)]
        if len(values) == 0:
            raise ValueError(f"Cannot find any option for the base key {base_key}")

        base_keys = [str(f.relative_to(base_cfg_dir)) for f in files]
        base_keys = [k.split(".")[0] for k in base_keys]
        base_keys = [k.replace("/", ".") for k in base_keys]
        options = {files[i].stem: base_keys[i] for i in range(len(files))}

        # handler = BaseWidgetHandler(cfg_key, options)

        label = cfg_key.split(".")[-1]
        label = f"{label_prefix}{label}:"

        widget = DropdownList(values, label=label, name=cfg_key)

        return [widget]


class RecursiveWidgetParser(WidgetParser):
    @staticmethod
    def can_handle(x: Any) -> bool:
        return isinstance(x, dict)

    @staticmethod
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[Widget]:
        widgets: List[Widget] = []

        label = cfg_key.split(".")[-1]
        label = f"{label_prefix}{label}:"
        widgets.append(Label(label))

        children_prefix = f"{label_prefix}{WidgetParser.PREFIX}"
        children = WidgetFactory.get_widgets(
            cfg_value, base_cfg_dir, cfg_prefix=cfg_key, label_prefix=children_prefix
        )
        widgets.extend(children)

        return widgets


class WidgetFactory:
    @staticmethod
    def get_parsers() -> List[Type[WidgetParser]]:
        """Create a list of widget parsers.

        Important: parsers are checked in the same order in which they
        are inserted into the list.

        Returns:
            The list of widget parsers.
        """
        parsers: List[Type[WidgetParser]] = []

        # specials
        parsers.append(BoolWidgetParser)
        parsers.append(DateWidgetParser)
        parsers.append(FileWidgetParser)
        parsers.append(OptionsWidgetParser)
        parsers.append(BaseWidgetParser)

        # recursive
        parsers.append(RecursiveWidgetParser)

        # literal
        parsers.append(LiteralWidgetParser)

        return parsers

    @staticmethod
    def get_widgets(
        cfg: CFG_T,
        base_cfg_dir: Path,
        cfg_prefix: str = "",
        label_prefix: str = "",
    ) -> List[Widget]:
        """Prepare widgets for a given config.

        Args:
            cfg: the config.
            base_cfg_dir: path to the base configs directory.
            cfg_prefix: prefix for the config key of the returned widgets.
            label_prefix: prefix for the name of the returned widgets.

        Returns:
            The list of the widgets for the given config.
        """
        widgets: List[Widget] = []
        parsers = WidgetFactory.get_parsers()

        for k in cfg:
            for parser in parsers:
                if parser.can_handle(cfg[k]):
                    cfg_key = f"{cfg_prefix}.{k}" if len(cfg_prefix) > 0 else k
                    widgets.extend(parser.parse(cfg_key, label_prefix, cfg[k], base_cfg_dir))
                    break

        return widgets
