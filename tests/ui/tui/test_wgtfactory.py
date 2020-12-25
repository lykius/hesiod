from datetime import datetime
from pathlib import Path
from typing import cast

from npyscreen import TitleDateCombo, TitleFilename, TitleSelectOne, TitleText

from hesiod.ui.tui.wgtfactory import BaseWidgetParser, BoolWidgetParser, DateWidgetParser
from hesiod.ui.tui.wgtfactory import FileWidgetParser, LiteralWidgetParser, OptionsWidgetParser
from hesiod.ui.tui.wgtfactory import RecursiveWidgetParser, WidgetParser
from hesiod.ui.tui.wgthandler import BaseWidgetHandler, BoolWidgetHandler, OptionsWidgetHandler
from hesiod.ui.tui.wgthandler import WidgetHandler


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

    for cfg in cfgs:
        assert LiteralWidgetParser.can_handle(cfg[1])
        w = LiteralWidgetParser.parse(cfg[0], "", cfg[1], Path())[0]
        assert isinstance(w[0], WidgetHandler)
        assert isinstance(w[1], TitleText.__class__)
        assert isinstance(w[2], dict)
        assert cast(dict, w[2])["name"] == cfg[0] + ":"
        assert cast(dict, w[2])["value"] == str(cfg[1])
        assert cast(dict, w[2])["begin_entry_at"] == len(cfg[0] + ":") + 1
        assert cast(dict, w[2])["use_two_lines"] is False


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

    for cfg in cfgs:
        print(cfg)
        assert DateWidgetParser.can_handle(cfg[1]) == cfg[2]

        if cfg[2]:
            w = DateWidgetParser.parse(cfg[0], "", cfg[1], Path())[0]
            assert isinstance(w[0], WidgetHandler)
            assert isinstance(w[1], TitleDateCombo.__class__)
            assert isinstance(w[2], dict)
            name = f"{cfg[0]} {DateWidgetParser.HINT}:"
            assert cast(dict, w[2])["name"] == name
            assert cast(dict, w[2])["begin_entry_at"] == len(name) + 1
            assert cast(dict, w[2])["use_two_lines"] is False

            if cfg[3] is not None:
                assert cast(dict, w[2])["value"] == cfg[3]


def test_file_widget_parser() -> None:
    cfgs = [
        ("cfg1", "@FILE", True, ""),
        ("cfg2", "@FILE(/path/to/default)", True, "/path/to/default"),
        ("cfg3", "@FILE()", False, ""),
        ("cfg4", "@File", False, ""),
        ("cfg5", "@file", False, ""),
        ("cfg6", "something", False, ""),
    ]

    for cfg in cfgs:
        assert FileWidgetParser.can_handle(cfg[1]) == cfg[2]

        if cfg[2]:
            w = FileWidgetParser.parse(cfg[0], "", cfg[1], Path())[0]
            assert isinstance(w[0], WidgetHandler)
            assert isinstance(w[1], TitleFilename.__class__)
            assert isinstance(w[2], dict)
            name = f"{cfg[0]} {FileWidgetParser.HINT}:"
            assert cast(dict, w[2])["name"] == name
            assert cast(dict, w[2])["begin_entry_at"] == len(name) + 1
            assert cast(dict, w[2])["use_two_lines"] is False

            if cfg[3] != "":
                assert cast(dict, w[2])["value"] == cfg[3]


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

    for cfg in cfgs:
        print(cfg)
        assert BoolWidgetParser.can_handle(cfg[1]) == cfg[2]

        if cfg[2]:
            w = BoolWidgetParser.parse(cfg[0], "", cfg[1], Path())[0]
            assert isinstance(w[0], BoolWidgetHandler)
            assert isinstance(w[1], TitleSelectOne.__class__)
            assert isinstance(w[2], dict)
            assert cast(dict, w[2])["name"] == cfg[0] + ":"
            assert cast(dict, w[2])["begin_entry_at"] == len(cfg[0] + ":") + 1
            assert cast(dict, w[2])["values"] == [BoolWidgetHandler.TRUE, BoolWidgetHandler.FALSE]
            assert cast(dict, w[2])["value"] == [cfg[3]]
            assert cast(dict, w[2])["max_height"] == 2
            assert cast(dict, w[2])["use_two_lines"] is False
            assert cast(dict, w[2])["scroll_exit"] is True


def test_options_widget_parser() -> None:
    cfgs = [
        ("cfg1", "@OPTIONS(1, 2.5, True, test)", True, [1, 2.5, True, "test"]),
        ("cfg2", "@OPTIONS()", False, None),
        ("cfg3", "@OPTIONS", False, None),
        ("cfg4", "@options", False, None),
        ("cfg5", "something", False, None),
    ]

    for cfg in cfgs:
        assert OptionsWidgetParser.can_handle(cfg[1]) == cfg[2]

        if cfg[2]:
            w = OptionsWidgetParser.parse(cfg[0], "", cfg[1], Path())[0]
            assert isinstance(w[0], OptionsWidgetHandler)
            assert isinstance(w[1], TitleSelectOne.__class__)
            assert isinstance(w[2], dict)
            assert cast(dict, w[2])["name"] == cfg[0] + ":"
            assert cast(dict, w[2])["begin_entry_at"] == len(cfg[0] + ":") + 1
            assert cast(dict, w[2])["values"] == cfg[3]
            assert cast(dict, w[2])["value"] == [0]
            assert cast(dict, w[2])["max_height"] == len(cfg[3])
            assert cast(dict, w[2])["use_two_lines"] is False
            assert cast(dict, w[2])["scroll_exit"] is True


def test_base_widget_parser(base_cfg_dir: Path) -> None:
    cfgs = [
        ("cfg1", "@BASE(dataset)", True, ["cifar10", "cifar100", "imagenet"]),
        ("cfg2", "@BASE(net.resnet)", True, ["resnet18", "resnet101"]),
        ("cfg3", "@BASE()", False, None),
        ("cfg4", "@BASE", False, None),
        ("cfg5", "@base", False, None),
        ("cfg6", "something", False, None),
    ]

    for cfg in cfgs:
        assert BaseWidgetParser.can_handle(cfg[1]) == cfg[2]

        if cfg[2]:
            w = BaseWidgetParser.parse(cfg[0], "", cfg[1], base_cfg_dir)[0]
            assert isinstance(w[0], BaseWidgetHandler)
            assert isinstance(w[1], TitleSelectOne.__class__)
            assert isinstance(w[2], dict)
            assert cast(dict, w[2])["name"] == cfg[0] + ":"
            assert cast(dict, w[2])["begin_entry_at"] == len(cfg[0] + ":") + 1
            assert sorted(cast(dict, w[2])["values"]) == sorted(cfg[3])
            assert cast(dict, w[2])["value"] == [0]
            assert cast(dict, w[2])["max_height"] == len(cfg[3])
            assert cast(dict, w[2])["use_two_lines"] is False
            assert cast(dict, w[2])["scroll_exit"] is True


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
                    "param2": "@FILE(/path/to/default)",
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
    expected = [
        (None, TitleText.__class__, "test:"),
        (None, TitleText.__class__, f"{prefix}group:"),
        (None, TitleText.__class__, f"{prefix}{prefix}subgroup1:"),
        (WidgetHandler, TitleText.__class__, f"{prefix}{prefix}{prefix}param1:"),
        (WidgetHandler, TitleText.__class__, f"{prefix}{prefix}{prefix}param2:"),
        (WidgetHandler, TitleText.__class__, f"{prefix}{prefix}{prefix}param3:"),
        (WidgetHandler, TitleText.__class__, f"{prefix}{prefix}{prefix}param4:"),
        (WidgetHandler, TitleText.__class__, f"{prefix}{prefix}{prefix}param5:"),
        (WidgetHandler, TitleText.__class__, f"{prefix}{prefix}{prefix}param6:"),
        (WidgetHandler, TitleText.__class__, f"{prefix}{prefix}{prefix}param7:"),
        (None, TitleText.__class__, f"{prefix}{prefix}subgroup2:"),
        (None, TitleText.__class__, f"{prefix}{prefix}{prefix}subsubgroup:"),
        (
            WidgetHandler,
            TitleText.__class__,
            f"{prefix}{prefix}{prefix}{prefix}param1 {date_hint}:",
        ),
        (
            WidgetHandler,
            TitleText.__class__,
            f"{prefix}{prefix}{prefix}{prefix}param2 {file_hint}:",
        ),
        (BoolWidgetHandler, TitleText.__class__, f"{prefix}{prefix}{prefix}{prefix}param3:"),
        (OptionsWidgetHandler, TitleText.__class__, f"{prefix}{prefix}{prefix}{prefix}param4:"),
        (BaseWidgetHandler, TitleText.__class__, f"{prefix}{prefix}{prefix}{prefix}param5:"),
    ]

    for i in range(len(widgets)):
        if expected[i][0] is None:
            assert widgets[i][0] is None
        else:
            assert isinstance(widgets[i][0], expected[i][0])
        assert isinstance(widgets[i][1], expected[i][1])
        assert widgets[i][2]["name"] == expected[i][2]
