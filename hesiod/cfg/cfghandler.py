from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Type

from hesiod.cfg.cfgparser import CFG_T, ConfigParser
from hesiod.cfg.yamlparser import YAMLConfigParser

BASE_KEY = "base"
RUN_NAME_KEY = "run_name"


class ConfigHandler:
    @staticmethod
    def get_parser(ext: str) -> Type["ConfigParser"]:
        """Return the proper parser given the extension of the file to parse.

        Args:
            ext: the extension of the file to parse.

        Returns:
            The proper parser for the given extension.
        """
        parsers = [YAMLConfigParser]
        parsers_table: Dict[str, Type[ConfigParser]] = {}
        for parser in parsers:
            for managed_ext in parser.get_managed_extensions():
                parsers_table[managed_ext] = parser

        ext = ext.strip()
        ext = ext[1:] if ext[0] == "." else ext
        return parsers_table[ext]

    @staticmethod
    def load_cfg(run_cfg_file: Path, base_cfg_dir: Path) -> CFG_T:
        """Load config replacing "bases" with proper values.

        Args:
            run_cfg_file: path to the run config file.
            base_cfg_dir: path to the base configs directory.

        Returns:
            The loaded config.
        """

        cfg = ConfigHandler.load_cfg_file(run_cfg_file)

        base_cfgs = ConfigHandler.load_base_cfgs(base_cfg_dir)

        cfg = ConfigHandler.replace_bases(cfg, base_cfgs)

        return cfg

    @staticmethod
    def load_cfg_file(cfg_file: Path) -> CFG_T:
        """Load config from a given file.

        Args:
            cfg_file: the file with the config.

        Raises:
            ValueError: if the config is not of the expected type.

        Returns:
            The loaded config.
        """
        parser = ConfigHandler.get_parser(cfg_file.suffix)
        cfg = parser.read_cfg_file(cfg_file)

        if not isinstance(cfg, dict):
            raise ValueError(f"Error in {cfg_file.name}: Config should be a dictionary.")

        for key in cfg:
            if not isinstance(key, str):
                raise ValueError("Error in {cfg_file.name}: Config keys should be strings.")

        return cfg

    @staticmethod
    def load_cfg_dir(cfg_dir: Path) -> Dict[str, CFG_T]:
        """Load configs recursively from a given directory.

        Args:
            cfg_dir: the config directory.

        Returns:
            The loaded config.
        """
        cfg: Dict[str, Dict[str, Any]] = {}

        cfg_files = [p for p in cfg_dir.glob("*.yaml")]
        for cfg_file in cfg_files:
            cfg[cfg_file.stem] = ConfigHandler.load_cfg_file(cfg_file)

        cfg_subdirs = [p for p in cfg_dir.glob("*") if p.is_dir()]
        for cfg_subdir in cfg_subdirs:
            cfg[cfg_subdir.name] = ConfigHandler.load_cfg_dir(cfg_subdir)

        return cfg

    @staticmethod
    def load_base_cfgs(base_cfg_dir: Path) -> Dict[str, CFG_T]:
        base_cfgs: Dict[str, CFG_T] = {}
        cfg_files = [p for p in base_cfg_dir.glob("*.yaml")]
        for cfg_file in cfg_files:
            base_cfgs[cfg_file.stem] = ConfigHandler.load_cfg_file(cfg_file)
        cfg_dirs = [p for p in base_cfg_dir.glob("*") if p.is_dir()]
        for cfg_dir in cfg_dirs:
            base_cfgs[cfg_dir.name] = ConfigHandler.load_cfg_dir(cfg_dir)

        return base_cfgs

    @staticmethod
    def replace_base(
        cfg: CFG_T,
        base_cfgs: Dict[str, CFG_T],
        base_key: str = BASE_KEY,
    ) -> CFG_T:
        """Replace base placeholder in a given config.

        Args:
            cfg: the config with base placeholder.
            base_cfgs: the available base configs.
            base_key: the string used as base key.

        Raises:
            ValueError: if it is not possible to retrieve the base config.

        Returns:
            The config with the base placeholder replaced.
        """
        new_cfg = deepcopy(cfg)
        base_id = new_cfg[base_key]
        base_cfg = base_cfgs

        for k in base_id.split("."):
            if k not in base_cfg:
                raise ValueError(f"Config error: cannot find base {base_id}")
            base_cfg = base_cfg[k]

        del new_cfg[base_key]

        for k in base_cfg:
            if k not in new_cfg:
                new_cfg[k] = base_cfg[k]

        return new_cfg

    @classmethod
    def replace_bases(
        cls,
        cfg: CFG_T,
        base_cfgs: Dict[str, CFG_T],
        base_key: str = BASE_KEY,
    ) -> CFG_T:
        """Replace all the bases in a given config recursively.

        Args:
            cfg: the config to process.
            base_cfgs: the available base configs.
            base_key: the string used as base key.

        Returns:
            The config with all bases resolved.
        """
        new_cfg = deepcopy(cfg)

        # replace base in main cfg
        while base_key in new_cfg:
            new_cfg = cls.replace_base(new_cfg, base_cfgs, base_key=base_key)

        # replace bases in sub cfgs
        for cfg_key in new_cfg:
            if isinstance(new_cfg[cfg_key], dict):
                new_cfg[cfg_key] = cls.replace_bases(new_cfg[cfg_key], base_cfgs, base_key=base_key)

        return new_cfg

    @staticmethod
    def save_cfg(cfg: CFG_T, cfg_file: Path) -> None:
        """Save config into the given file.

        Args:
            cfg: the config to be saved.
            cfg_file: the path to the output file.
        """
        parser = ConfigHandler.get_parser(cfg_file.suffix)
        parser.write_cfg(cfg, cfg_file)
