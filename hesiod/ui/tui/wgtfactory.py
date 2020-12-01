from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Tuple, Type, Union
from pathlib import Path
import re
from npyscreen import TitleText, TitleDateCombo, TitleFilename, TitleSelectOne  # type: ignore
from npyscreen.wgwidget import Widget  # type: ignore

from hesiod.cfgparse import CFGT

WIDGET_T = Tuple[Callable[..., Widget], Dict[str, Any]]


class WidgetParser(ABC):
    PREFIX = "    "
    DATE_PATTERN = "@DATE"
    FILE_PATTERN = "@FILE"
    OPTIONS_PATTERN = "@OPTION([0-9A-Za-z_]+)"

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
    def parse(cfg_key: str, prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[WIDGET_T]:
        """Parse a literal config and return a list with the needed widgets.

        Args:
            cfg_key: name of the config.
            prefix: prefix for the name of the config.
            cfg_value: literal value of the config.
            base_cfg_dir: path to the base configs directory.

        Returns:
            A list with the widgets for the given config.
        """
        ...


class LiteralWidgetParser(WidgetParser):
    @staticmethod
    def can_handle(x: Any) -> bool:
        return type(x) in [int, float, str, list]

    @staticmethod
    def parse(cfg_key: str, prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[WIDGET_T]:
        widgets: List[WIDGET_T] = []

        name = f"{prefix}{cfg_key}:"
        widgets.append(WidgetFactory.get_literal_widget(name, cfg_value))

        return widgets


class DateWidgetParser(WidgetParser):
    @staticmethod
    def can_handle(x: Any) -> bool:
        return isinstance(x, str) and WidgetParser.match(x, WidgetParser.DATE_PATTERN)

    @staticmethod
    def parse(cfg_key: str, prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[WIDGET_T]:
        widgets: List[WIDGET_T] = []

        name = f"{prefix}{cfg_key} (ENTER to select one):"
        begin_entry_at = len(name) + 1
        kwargs = {
            "name": name,
            "begin_entry_at": begin_entry_at,
            "use_two_lines": False,
        }
        widgets.append((TitleDateCombo, kwargs))

        return widgets


class FileWidgetParser(WidgetParser):
    @staticmethod
    def can_handle(x: Any) -> bool:
        return isinstance(x, str) and WidgetParser.match(x, WidgetParser.FILE_PATTERN)

    @staticmethod
    def parse(cfg_key: str, prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[WIDGET_T]:
        widgets: List[WIDGET_T] = []

        name = f"{prefix}{cfg_key} (TAB for autocompletion):"
        begin_entry_at = len(name) + 1
        kwargs = {
            "name": name,
            "begin_entry_at": begin_entry_at,
            "use_two_lines": False,
        }
        widgets.append((TitleFilename, kwargs))

        return widgets


class OptionsWidgetParser(WidgetParser):
    @staticmethod
    def can_handle(x: Any) -> bool:
        return isinstance(x, str) and WidgetParser.match(x, WidgetParser.OPTIONS_PATTERN)

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
                files.extend(OptionsWidgetParser.get_files_list(p))
        return files

    @staticmethod
    def parse(cfg_key: str, prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[WIDGET_T]:
        widgets: List[WIDGET_T] = []

        base_key = cfg_value.split("(")[-1].split(")")[0]
        if len(base_key) == 0:
            raise ValueError("Base key inside @OPTIONS cannot be empty.")
        base_keys = base_key.split(".")

        root = base_cfg_dir
        for k in base_keys:
            subdirs = [d for d in root.glob(k) if d.is_dir()]
            if len(subdirs) != 1:
                raise ValueError(f"Cannot find base key {base_key}")
            root = subdirs[0]

        files = sorted(OptionsWidgetParser.get_files_list(root))
        values = [f.stem for f in files]
        if len(values) == 0:
            raise ValueError(f"Cannot find any option for the base key {base_key}")

        name = f"{prefix}{cfg_key}:"
        kwargs = {
            "name": name,
            "values": values,
            "value": [0],
            "max_height": len(values),
            "begin_entry_at": len(name) + 1,
            "use_two_lines": False,
            "scroll_exit": True,
        }
        widgets.append((TitleSelectOne, kwargs))

        return widgets


class RecursiveWidgetParser(WidgetParser):
    @staticmethod
    def can_handle(x: Any) -> bool:
        return isinstance(x, dict)

    @staticmethod
    def parse(cfg_key: str, prefix: str, cfg_value: Any, base_cfg_dir: Path) -> List[WIDGET_T]:
        widgets: List[WIDGET_T] = []

        kwargs = {"name": f"{prefix}{cfg_key}:", "use_two_lines": False, "editable": False}
        widgets.append((TitleText, kwargs))

        children_prefix = f"{prefix}{WidgetParser.PREFIX}"
        widgets.extend(WidgetFactory.get_widgets(cfg_value, base_cfg_dir, prefix=children_prefix))

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
        parsers.append(DateWidgetParser)
        parsers.append(FileWidgetParser)
        parsers.append(OptionsWidgetParser)
        # recursive
        parsers.append(RecursiveWidgetParser)
        # literal
        parsers.append(LiteralWidgetParser)

        return parsers

    @staticmethod
    def get_widgets(cfg: CFGT, base_cfg_dir: Path, prefix: str = "") -> List[WIDGET_T]:
        """Prepare widgets for a given config.

        Args:
            cfg: the config.
            base_cfg_dir: path to the base configs directory.
            prefix: prefix for the name of the returned widgets.

        Returns:
            The list of the widgets for the given config.
        """
        widgets: List[WIDGET_T] = []
        parsers = WidgetFactory.get_parsers()

        for k in cfg:
            for parser in parsers:
                if parser.can_handle(cfg[k]):
                    widgets.extend(parser.parse(k, prefix, cfg[k], base_cfg_dir))
                    break

        return widgets

    @staticmethod
    def get_literal_widget(name: str, value: Union[int, float, str, list]) -> WIDGET_T:
        """Get a TitleText widget for a literal config.

        Args:
            name: name of the config.
            value: value for the config.

        Returns:
            The TitleText widget for the given config.
        """
        begin_entry_at = len(name) + 1
        kwargs = {
            "name": name,
            "value": str(value),
            "begin_entry_at": begin_entry_at,
            "use_two_lines": False,
        }
        return (TitleText, kwargs)
