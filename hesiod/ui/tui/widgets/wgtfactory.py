import re
from abc import ABC, abstractmethod
from ast import literal_eval
from datetime import date, datetime
from pathlib import Path
from typing import Any, List, Optional, Tuple, Type

from asciimatics.widgets import Label, Text, Widget  # type: ignore

from hesiod.cfgparse import CFG_T
from hesiod.ui.tui.widgets.custom.datepicker import CustomDatePicker
from hesiod.ui.tui.widgets.custom.dropdown import CustomDropdownList
from hesiod.ui.tui.widgets.custom.filebrowser import CustomFileBrowser
from hesiod.ui.tui.widgets.custom.radiobuttons import CustomRadioButtons
from hesiod.ui.tui.widgets.wgthandler import BaseWidgetHandler, BoolWidgetHandler
from hesiod.ui.tui.widgets.wgthandler import OptionsWidgetHandler, WidgetHandler

WGT_T = Tuple[Optional[WidgetHandler], Widget]


class WidgetParser(ABC):
    PREFIX = "   "
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
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[WGT_T]:
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
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[WGT_T]:
        handler = WidgetHandler(cfg_key)

        label = cfg_key.split(".")[-1]
        label = f"{label_prefix}{label}:"

        widget = Text(label=label, name=cfg_key)
        widget.value = str(cfg_value)

        return [(handler, widget)]


class DateWidgetParser(WidgetParser):
    TODAY = "today"
    FORMAT = r"%Y-%M-%d"
    HINT = "(↲ to select)"

    @staticmethod
    def can_handle(x: Any) -> bool:
        if isinstance(x, str):
            can_handle = WidgetParser.match(x, WidgetParser.DATE_PATTERN)
            can_handle = can_handle or WidgetParser.match(x, WidgetParser.DEFAULT_DATE_PATTERN)
            return can_handle
        return False

    @staticmethod
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[WGT_T]:
        handler = WidgetHandler(cfg_key)

        label = cfg_key.split(".")[-1]
        label = f"{label_prefix}{label} {DateWidgetParser.HINT}:"

        widget = CustomDatePicker(label=label, name=cfg_key)

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

        return [(handler, widget)]


class FileWidgetParser(WidgetParser):
    HINT = "(↲ to select)"

    @staticmethod
    def can_handle(x: Any) -> bool:
        if isinstance(x, str):
            can_handle = WidgetParser.match(x, WidgetParser.FILE_PATTERN)
            can_handle = can_handle or WidgetParser.match(x, WidgetParser.DEFAULT_FILE_PATTERN)
            return can_handle
        return False

    @staticmethod
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[WGT_T]:
        handler = WidgetHandler(cfg_key)

        label = cfg_key.split(".")[-1]
        label = f"{label_prefix}{label} {FileWidgetParser.HINT}:"

        if WidgetParser.match(cfg_value, WidgetParser.DEFAULT_FILE_PATTERN):
            default = cfg_value.split("(")[-1].split(")")[0]
            path = default.lower()
        else:
            path = str(Path(".").absolute())

        widget = CustomFileBrowser(label, cfg_key, path)

        return [(handler, widget)]


class BoolWidgetParser(WidgetParser):
    @staticmethod
    def can_handle(x: Any) -> bool:
        return isinstance(x, str) and WidgetParser.match(x, WidgetParser.BOOL_PATTERN)

    @staticmethod
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[WGT_T]:
        handler = BoolWidgetHandler(cfg_key)

        label = cfg_key.split(".")[-1]
        label = f"{label_prefix}{label}:"

        values = [(BoolWidgetHandler.TRUE, 0), (BoolWidgetHandler.FALSE, 1)]
        widget = CustomRadioButtons(values, label=label, name=cfg_key)
        default = cfg_value.split("(")[-1].split(")")[0]
        default = str(default).lower()
        widget.value = 0 if default == BoolWidgetHandler.TRUE else 1

        return [(handler, widget)]


class OptionsWidgetParser(WidgetParser):
    @staticmethod
    def can_handle(x: Any) -> bool:
        return isinstance(x, str) and WidgetParser.match(x, WidgetParser.OPTIONS_PATTERN)

    @staticmethod
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[WGT_T]:
        options = cfg_value.split("(")[-1].split(")")[0]
        values = [(option.strip(), i) for i, option in enumerate(options.split(","))]

        label = cfg_key.split(".")[-1]
        label = f"{label_prefix}{label}:"

        widget = CustomRadioButtons(values, label=label, name=cfg_key)

        handler_values: List[Any] = []
        for v, _ in values:
            try:
                value = literal_eval(v)
            except ValueError:
                value = v
            handler_values.append(value)
        handler = OptionsWidgetHandler(cfg_key, handler_values)

        return [(handler, widget)]


class BaseWidgetParser(WidgetParser):
    HINT = "(↲ to select)"

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
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[WGT_T]:
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

        handler = BaseWidgetHandler(cfg_key, base_keys)

        label = cfg_key.split(".")[-1]
        label = f"{label_prefix}{label} {BaseWidgetParser.HINT}:"

        widget = CustomDropdownList(values, label=label, name=cfg_key)

        return [(handler, widget)]


class RecursiveWidgetParser(WidgetParser):
    @staticmethod
    def can_handle(x: Any) -> bool:
        return isinstance(x, dict)

    @staticmethod
    def parse(cfg_key: str, label_prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[WGT_T]:
        widgets: List[WGT_T] = []

        label = cfg_key.split(".")[-1]
        label = f"{label_prefix}{label}:"
        widgets.append((None, Label(label)))

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
    ) -> List[WGT_T]:
        """Prepare widgets for a given config.

        Args:
            cfg: the config.
            base_cfg_dir: path to the base configs directory.
            cfg_prefix: prefix for the config key of the returned widgets.
            label_prefix: prefix for the name of the returned widgets.

        Returns:
            The list of the widgets for the given config.
        """
        widgets: List[WGT_T] = []
        parsers = WidgetFactory.get_parsers()

        for k in cfg:
            for parser in parsers:
                if parser.can_handle(cfg[k]):
                    cfg_key = f"{cfg_prefix}.{k}" if len(cfg_prefix) > 0 else k
                    widgets.extend(parser.parse(cfg_key, label_prefix, cfg[k], base_cfg_dir))
                    break

        return widgets

    @staticmethod
    def get_recap_text(
        cfg: CFG_T,
        label_style: Tuple[int, int],
        text_style: Tuple[int, int],
    ) -> List[str]:
        """Create a recap text for a given config.

        Args:
            cfg: the config to recap.

        Returns:
            A list with the lines of the recap text.
        """
        recap: List[str] = []

        lbl = "${" + str(label_style[0]) + "," + str(label_style[1]) + "}"
        txt = "${" + str(text_style[0]) + "," + str(text_style[1]) + "}"

        for _, widget in WidgetFactory.get_widgets(cfg, Path()):
            label = widget.text if isinstance(widget, Label) else widget.label
            line = f"{lbl}{label}"
            if not isinstance(widget, Label):
                line += f"{txt} {widget.value}"
            recap.append(line)

        return recap
