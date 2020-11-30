from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Tuple, Type, Union
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
        ...

    @staticmethod
    @abstractmethod
    def parse(cfg_key: str, prefix: str, cfg_value: Any) -> List[WIDGET_T]:
        ...


class LiteralWidgetParser(WidgetParser):
    @staticmethod
    def can_handle(x: Any) -> bool:
        """Check if the input config can be handled by this parser.

        Args:
            x: the input config.

        Returns:
            True if the input config is int, float, str or list.
        """
        return type(x) in [int, float, str, list]

    @staticmethod
    def parse(cfg_key: str, prefix: str, cfg_value: Any) -> List[WIDGET_T]:
        """Parse a literal config and return a TitleText widget.

        Args:
            cfg_key: name of the config.
            prefix: prefix for the name of the config.
            cfg_value: literal value of the config.

        Returns:
            A list with the TitleText widget for the given config.
        """
        widgets: List[WIDGET_T] = []

        name = f"{prefix}{cfg_key}:"
        widgets.append(WidgetFactory.get_literal_widget(name, cfg_value))

        return widgets


class DateWidgetParser(WidgetParser):
    @staticmethod
    def can_handle(x: Any) -> bool:
        """Check if the input config can be handled by this parser.

        Args:
            x: the input config.

        Returns:
            True if the input config is a str that matches the DATE pattern.
        """
        return isinstance(x, str) and WidgetParser.match(x, WidgetParser.DATE_PATTERN)

    @staticmethod
    def parse(cfg_key: str, prefix: str, cfg_value: Any) -> List[WIDGET_T]:
        """Parse date config and returns a TitleDateCombo widget.

        Args:
            cfg_key: name of the config.
            prefix: prefix for the name of the config.
            cfg_value: the date config to be parsed.

        Returns:
            A list with the TitleDateCombo widget for the given config.
        """
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
        """Check if the input config can be handled by this parser.

        Args:
            x: the input config.

        Returns:
            True if the input config is a str that matches the FILE pattern.
        """
        return isinstance(x, str) and WidgetParser.match(x, WidgetParser.FILE_PATTERN)

    @staticmethod
    def parse(cfg_key: str, prefix: str, cfg_value: Any) -> List[WIDGET_T]:
        """Parse file config and returns a TitleDateCombo widget.

        Args:
            cfg_key: name of the config.
            prefix: prefix for the name of the config.
            cfg_value: the date config to be parsed.

        Returns:
            A list with the TitleDateCombo widget for the given config.
        """
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
        """Check if the input config can be handled by this parser.

        Args:
            x: the input config.

        Returns:
            True if the input config is a str that matches the OPTIONS pattern.
        """
        return isinstance(x, str) and WidgetParser.match(x, WidgetParser.OPTIONS_PATTERN)

    @staticmethod
    def parse(cfg_key: str, prefix: str, cfg_value: Any) -> List[WIDGET_T]:
        """Parse options config and returns a TitleSelectOne widget.

        Args:
            cfg_key: name of the config.
            prefix: prefix for the name of the config.
            cfg_value: the options config to be parsed.

        Returns:
            A list with the TitleSelectOne widget for the given config.
        """
        widgets: List[WIDGET_T] = []

        name = f"{prefix}{cfg_key}:"
        values = ["option1", "option2", "option3"]
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
        """Check if the input config can be handled by this parser.

        Args:
            x: the input config.

        Returns:
            True if the input config is a dict.
        """
        return isinstance(x, dict)

    @staticmethod
    def parse(cfg_key: str, prefix: str, cfg_value: Any) -> List[WIDGET_T]:
        """Parse a recursive config and returns the list of widgets associated to it.

        Args:
            cfg_key: name of the config.
            prefix: prefix for the name of the config (used for recursive calls).
            cfg_value: a dictionary with the config associated to cfg_key.

        Returns:
            A list with the widgets associated to the given recursive config.
        """
        widgets: List[WIDGET_T] = []

        kwargs = {"name": f"{prefix}{cfg_key}:", "use_two_lines": False, "editable": False}
        widgets.append((TitleText, kwargs))

        children_prefix = f"{prefix}{WidgetParser.PREFIX}"
        widgets.extend(WidgetFactory.get_widgets(cfg_value, prefix=children_prefix))

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
    def get_widgets(cfg: CFGT, prefix: str = "") -> List[WIDGET_T]:
        """Prepare widgets for a given config.

        Args:
            cfg: the config.
            prefix: prefix for the name of the returned widgets.

        Returns:
            The list of the widgets for the given config.
        """
        widgets: List[WIDGET_T] = []
        parsers = WidgetFactory.get_parsers()

        for k in cfg:
            for parser in parsers:
                if parser.can_handle(cfg[k]):
                    widgets.extend(parser.parse(k, prefix, cfg[k]))
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
