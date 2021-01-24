from datetime import datetime
from pathlib import Path
from typing import cast

from asciimatics.widgets import Label, Text

from hesiod.ui.tui.widgets.custom.datepicker import CustomDatePicker
from hesiod.ui.tui.widgets.custom.dropdown import CustomDropdownList
from hesiod.ui.tui.widgets.custom.filebrowser import CustomFileBrowser
from hesiod.ui.tui.widgets.custom.radiobuttons import CustomRadioButtons
from hesiod.ui.tui.widgets.wgtfactory import BaseWidgetParser, BoolWidgetParser, DateWidgetParser
from hesiod.ui.tui.widgets.wgtfactory import FileWidgetParser, LiteralWidgetParser
from hesiod.ui.tui.widgets.wgtfactory import OptionsWidgetParser, RecursiveWidgetParser
from hesiod.ui.tui.widgets.wgtfactory import WidgetParser
from hesiod.ui.tui.widgets.wgthandler import BaseWidgetHandler, BoolWidgetHandler
from hesiod.ui.tui.widgets.wgthandler import OptionsWidgetHandler, WidgetHandler


def test_literal_widget_parser() -> None:
    cfgs = [
        ("cfg1", 1),
        ("cfg2", 1.2),
        ("cfg3", "test"),
        ("cfg4", True),
        ("cfg5", [1, 2, 3]),
        ("cfg6", (1, 2, 3)),
        ("cfg7", set((1, 2, 3))),
        ("cfg8", datetime.now().date()),
    ]

    prefix = "prefix"

    for cfg in cfgs:
        assert LiteralWidgetParser.can_handle(cfg[1])
        handler, widget = LiteralWidgetParser.parse(cfg[0], prefix, cfg[1], Path())[0]
        assert isinstance(handler, WidgetHandler)
        assert handler.cfg_key == cfg[0]
        assert widget.label == prefix + cfg[0] + ":"
        assert isinstance(widget, Text)
        assert widget.value == str(cfg[1])


def test_date_widget_parser() -> None:
    cfgs = [
        ("cfg1", "@DATE", True, None),
        ("cfg2", "@DATE(today)", True, datetime.today().date()),
        ("cfg3", "@DATE(Today)", True, datetime.today().date()),
        ("cfg4", "@DATE(TODAY)", True, datetime.today().date()),
        (
            "cfg5",
            "@DATE(2020-01-01)",
            True,
            datetime.strptime("2020-01-01", DateWidgetParser.FORMAT).date(),
        ),
        ("cfg6", "@DATE()", False, None),
        ("cfg7", "@Date", False, None),
        ("cfg8", "@date", False, None),
        ("cfg9", "something", False, None),
    ]

    prefix = "prefix"

    for cfg in cfgs:
        print(cfg)
        assert DateWidgetParser.can_handle(cfg[1]) == cfg[2]

        if cfg[2]:
            handler, widget = DateWidgetParser.parse(cfg[0], prefix, cfg[1], Path())[0]
            assert isinstance(handler, WidgetHandler)
            assert handler.cfg_key == cfg[0]
            assert widget.label == f"{prefix}{cfg[0]} {DateWidgetParser.HINT}:"
            assert isinstance(widget, CustomDatePicker)
            if cfg[3] is not None:
                assert widget.value == cfg[3]


def test_file_widget_parser(simple_template_file: Path) -> None:
    cfgs = [
        ("cfg1", "@FILE", True, str(Path(".").absolute())),
        ("cfg2", f"@FILE({str(simple_template_file)})", True, str(simple_template_file.absolute())),
        ("cfg3", "@FILE()", False, ""),
        ("cfg4", "@File", False, ""),
        ("cfg5", "@file", False, ""),
        ("cfg6", "something", False, ""),
    ]

    prefix = "prefix"

    for cfg in cfgs:
        assert FileWidgetParser.can_handle(cfg[1]) == cfg[2]

        if cfg[2]:
            handler, widget = FileWidgetParser.parse(cfg[0], prefix, cfg[1], Path())[0]
            assert isinstance(handler, WidgetHandler)
            assert handler.cfg_key == cfg[0]
            assert widget.label == f"{prefix}{cfg[0]} {FileWidgetParser.HINT}:"
            assert isinstance(widget, CustomFileBrowser)
            assert cast(CustomFileBrowser, widget).value == cfg[3]


def test_bool_widget_parser() -> None:
    cfgs = [
        ("cfg1", "@BOOL(true)", True, 0),
        ("cfg2", "@BOOL(True)", True, 0),
        ("cfg3", "@BOOL(TRUE)", True, 0),
        ("cfg4", "@BOOL(false)", True, 1),
        ("cfg5", "@BOOL(False)", True, 1),
        ("cfg6", "@BOOL(FALSE)", True, 1),
        ("cfg7", "@BOOL", False, None),
        ("cfg8", "@BOOL()", False, None),
        ("cfg9", "@bool", False, None),
    ]

    prefix = "prefix"

    for cfg in cfgs:
        print(cfg)
        assert BoolWidgetParser.can_handle(cfg[1]) == cfg[2]

        if cfg[2]:
            handler, widget = BoolWidgetParser.parse(cfg[0], prefix, cfg[1], Path())[0]
            assert isinstance(handler, BoolWidgetHandler)
            assert handler.cfg_key == cfg[0]
            assert widget.label == prefix + cfg[0] + ":"
            assert isinstance(widget, CustomRadioButtons)
            assert cast(CustomRadioButtons, widget)._options == [
                (BoolWidgetHandler.TRUE, 0),
                (BoolWidgetHandler.FALSE, 1),
            ]
            assert widget.value == cfg[3]


def test_options_widget_parser() -> None:
    cfgs = [
        (
            "cfg1",
            "@OPTIONS(1; 2.5; True; test)",
            True,
            [("1", 0), ("2.5", 1), ("True", 2), ("test", 3)],
        ),
        ("cfg2", "@OPTIONS()", False, None),
        ("cfg3", "@OPTIONS", False, None),
        ("cfg4", "@options", False, None),
        ("cfg5", "something", False, None),
    ]

    prefix = "prefix"

    for cfg in cfgs:
        assert OptionsWidgetParser.can_handle(cfg[1]) == cfg[2]

        if cfg[2]:
            handler, widget = OptionsWidgetParser.parse(cfg[0], prefix, cfg[1], Path())[0]
            assert isinstance(handler, OptionsWidgetHandler)
            assert handler.cfg_key == cfg[0]
            assert widget.label == prefix + cfg[0] + ":"
            assert isinstance(widget, CustomRadioButtons)
            assert cast(CustomRadioButtons, widget)._options == cfg[3]


def test_base_widget_parser(base_cfg_dir: Path) -> None:
    cfgs = [
        ("cfg1", "@BASE(dataset)", True, ["cifar10", "cifar100", "imagenet"]),
        ("cfg2", "@BASE(net.resnet)", True, ["resnet18", "resnet101"]),
        ("cfg3", "@BASE()", False, None),
        ("cfg4", "@BASE", False, None),
        ("cfg5", "@base", False, None),
        ("cfg6", "something", False, None),
    ]

    prefix = "prefix"

    for cfg in cfgs:
        assert BaseWidgetParser.can_handle(cfg[1]) == cfg[2]

        if cfg[2]:
            handler, widget = BaseWidgetParser.parse(cfg[0], prefix, cfg[1], base_cfg_dir)[0]
            assert isinstance(handler, BaseWidgetHandler)
            assert handler.cfg_key == cfg[0]
            assert widget.label == prefix + cfg[0] + " " + BaseWidgetParser.HINT + ":"
            assert isinstance(widget, CustomDropdownList)
            expected_options = [(option, i) for i, option in enumerate(sorted(cfg[3]))]
            assert cast(CustomDropdownList, widget).options == expected_options


def test_recursive_widget_parser(base_cfg_dir: Path) -> None:
    assert RecursiveWidgetParser.can_handle(1) is False
    assert RecursiveWidgetParser.can_handle(1.2) is False
    assert RecursiveWidgetParser.can_handle(True) is False
    assert RecursiveWidgetParser.can_handle("test") is False
    assert RecursiveWidgetParser.can_handle((1, 2, 3)) is False
    assert RecursiveWidgetParser.can_handle([1, 2, 3]) is False
    assert RecursiveWidgetParser.can_handle(set((1, 2, 3))) is False

    cfg = {
        "group": {
            "subgroup1": {
                "param1": 1,
                "param2": 1.234,
                "param3": False,
                "param4": "test",
                "param5": [1, 2, 3],
                "param6": (1, 2, 3),
                "param7": set((1, 2, 3)),
            },
            "subgroup2": {
                "subsubgroup": {
                    "param1": "@DATE(today)",
                    "param2": "@FILE",
                    "param3": "@BOOL(False)",
                    "param4": "@OPTIONS(1, 2, 3)",
                    "param5": "@BASE(dataset.cifar)",
                }
            },
        }
    }

    assert RecursiveWidgetParser.can_handle(cfg)

    widgets = RecursiveWidgetParser.parse("test", "", cfg, base_cfg_dir)
    assert len(widgets) == 17

    prefix = WidgetParser.PREFIX
    date_hint = DateWidgetParser.HINT
    file_hint = FileWidgetParser.HINT
    base_hint = BaseWidgetParser.HINT
    expected = [
        (None, "test", "test:", Label),
        (None, "test.group", f"{prefix}group:", Label),
        (None, "test.group.subgroup1", f"{prefix}{prefix}subgroup1:", Label),
        (WidgetHandler, "test.group.subgroup1.param1", f"{prefix}{prefix}{prefix}param1:", Text),
        (WidgetHandler, "test.group.subgroup1.param2", f"{prefix}{prefix}{prefix}param2:", Text),
        (WidgetHandler, "test.group.subgroup1.param3", f"{prefix}{prefix}{prefix}param3:", Text),
        (WidgetHandler, "test.group.subgroup1.param4", f"{prefix}{prefix}{prefix}param4:", Text),
        (WidgetHandler, "test.group.subgroup1.param5", f"{prefix}{prefix}{prefix}param5:", Text),
        (WidgetHandler, "test.group.subgroup1.param6", f"{prefix}{prefix}{prefix}param6:", Text),
        (WidgetHandler, "test.group.subgroup1.param7", f"{prefix}{prefix}{prefix}param7:", Text),
        (None, "test.group.subgroup2", f"{prefix}{prefix}subgroup2:", Label),
        (
            None,
            "test.group.subgroup2.subsubgroup",
            f"{prefix}{prefix}{prefix}subsubgroup:",
            Label,
        ),
        (
            WidgetHandler,
            "test.group.subgroup2.subsubgroup.param1",
            f"{prefix}{prefix}{prefix}{prefix}param1 {date_hint}:",
            CustomDatePicker,
        ),
        (
            WidgetHandler,
            "test.group.subgroup2.subsubgroup.param2",
            f"{prefix}{prefix}{prefix}{prefix}param2 {file_hint}:",
            CustomFileBrowser,
        ),
        (
            BoolWidgetHandler,
            "test.group.subgroup2.subsubgroup.param3",
            f"{prefix}{prefix}{prefix}{prefix}param3:",
            CustomRadioButtons,
        ),
        (
            OptionsWidgetHandler,
            "test.group.subgroup2.subsubgroup.param4",
            f"{prefix}{prefix}{prefix}{prefix}param4:",
            CustomRadioButtons,
        ),
        (
            BaseWidgetHandler,
            "test.group.subgroup2.subsubgroup.param5",
            f"{prefix}{prefix}{prefix}{prefix}param5 {base_hint}:",
            CustomDropdownList,
        ),
    ]

    for i, (handler, widget) in enumerate(widgets):
        if expected[i][0] is None:
            assert handler is None
        else:
            assert isinstance(handler, expected[i][0])
            assert handler.cfg_key == expected[i][1]
        label = widget.text if isinstance(widget, Label) else widget.label
        assert label == expected[i][2]
        assert isinstance(widget, expected[i][3])
