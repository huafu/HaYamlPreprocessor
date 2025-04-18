"""
YAML Preprocessor for Home Assistant.

This custom component preprocesses YAML files by copying them from an input directory
to an output directory, applying transformations such as variable substitution in file
inclusion. It is designed to simplify YAML management in Home Assistant configurations.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from homeassistant.core import HomeAssistant, ServiceCall

import yaml

_LOGGER: logging.Logger = logging.getLogger(__package__)

DOMAIN: str = "yaml_preprocessor"

# Warning comment to prepend to each YAML file in the output directory
AUTO_GENERATED_WARNING: str = (
    "# WARNING: This file is auto-generated. Do not modify this file directly. "
    "Please edit the corresponding file in the input directory.\n\n"
)

# Content of the README file in the output directory
README_CONTENT: str = (
    "WARNING: This directory is wiped and regenerated entirely during each "
    "processing run.\n"
    "Do not modify the contents directly. Edit files in the input directory instead.\n"
)


def setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """
    Set up the custom component for Home Assistant.

    Args:
        hass: The Home Assistant instance.
        config: Configuration dictionary.

    Returns:
        True if the setup was successful, False otherwise.

    """
    conf = config.get(DOMAIN)
    if not conf:
        _LOGGER.error("Configuration missing for '%s'", DOMAIN)
        return False

    input_dir: str = conf.get("input_dir")
    output_dir: str = conf.get("output_dir")
    if not input_dir or not output_dir:
        _LOGGER.error(
            "'input_dir' and 'output_dir' must be defined in the configuration."
        )
        return False

    # we will complete the paths with the config dir
    input_dir = hass.config.path(input_dir)
    output_dir = hass.config.path(output_dir)

    # Register the process service
    def process_service(_call: ServiceCall) -> None:
        try:
            _process_yaml(input_dir, output_dir)
        except (FileNotFoundError, PermissionError, yaml.YAMLError):
            _LOGGER.exception("Error during YAML preprocessing")

    hass.services.register(DOMAIN, "process", process_service)
    _LOGGER.info(
        "Component '%s' loaded. Service '%s.process' is available.", DOMAIN, DOMAIN
    )
    return True


def _process_yaml(input_dir: str, output_dir: str) -> None:
    """
    Process YAML files by copying input_dir to output_dir and applying preprocessing.

    Args:
        input_dir: Path to the input directory.
        output_dir: Path to the output directory.

    """
    _prepare_output_directory(input_dir, output_dir)
    _create_readme(output_dir)
    _process_yaml_files(output_dir)


def _prepare_output_directory(input_dir: str, output_dir: str) -> None:
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)
    shutil.copytree(input_dir, output_dir)
    _LOGGER.info("Copied directory '%s' to '%s'", input_dir, output_dir)


def _create_readme(output_dir: str) -> None:
    """Create a README.md file in the output directory."""
    readme_path: Path = Path(output_dir) / "README.md"
    try:
        with readme_path.open("w", encoding="utf-8") as readme_file:
            readme_file.write(README_CONTENT)
    except OSError:
        _LOGGER.exception("Failed to create README.md in '%s'", output_dir)


def _process_yaml_files(output_dir: str) -> None:
    """Traverse output_dir and process YAML files."""

    class CustomLoader(yaml.SafeLoader):
        def __init__(self, stream: Any, base_dir: Path) -> None:
            super().__init__(stream)
            self.base_dir = base_dir

    def include_constructor(loader: CustomLoader, node: yaml.Node) -> Any:
        if isinstance(node, yaml.MappingNode):
            value = loader.construct_mapping(node, deep=True)
            if isinstance(value, dict) and "file" in value and "vars" in value:
                include_path: Path = loader.base_dir / value["file"]
                try:
                    with include_path.open("r", encoding="utf-8") as included_file:
                        file_content: str = included_file.read()
                except (FileNotFoundError, PermissionError, OSError):
                    _LOGGER.exception("Failed to open file '%s'", include_path)
                    file_content = ""

                def replace_var(match: re.Match) -> str:
                    var_name: str = match.group(1)
                    if var_name in value["vars"]:
                        return str(value["vars"][var_name])
                    _LOGGER.warning(
                        "Variable '%s' not found in '%s'. "
                        "Replacing with an empty string.",
                        var_name,
                        include_path,
                    )
                    return ""

                processed_content: str = re.sub(
                    r"\$\{(\w+)\}", replace_var, file_content
                )
                return processed_content
            _LOGGER.warning(
                "Invalid format for !include. Value must contain 'file' and 'vars'."
            )
            return value
        return loader.construct_object(node)

    CustomLoader.add_constructor("!include", include_constructor)

    def make_loader(base_dir: Path) -> type[yaml.SafeLoader]:
        """
        Return a Loader class with the provided base_dir pre-bound.

        This factory avoids the lambda typing problem by returning a proper type.
        """

        class LoaderWithBase(CustomLoader):  # type: ignore[misc]
            def __init__(self, stream: Any) -> None:
                super().__init__(stream, base_dir)

        return LoaderWithBase

    for root, dirs, files in os.walk(output_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.startswith(".") or not file.endswith((".yaml", ".yml")):
                continue
            file_path: Path = Path(root) / file
            _LOGGER.debug("Processing YAML file: %s", file_path)
            try:
                with file_path.open("r", encoding="utf-8") as yaml_file:
                    content: str = yaml_file.read()
                base_dir: Path = file_path.parent
                LoaderCls = make_loader(base_dir)  # noqa: N806
                data: Any = yaml.load(content, Loader=LoaderCls)  # noqa: S506
                new_content: str = yaml.safe_dump(
                    data, allow_unicode=True, default_flow_style=False
                )
                new_content = AUTO_GENERATED_WARNING + new_content
                with file_path.open("w", encoding="utf-8") as yaml_file:
                    yaml_file.write(new_content)
            except (yaml.YAMLError, FileNotFoundError, PermissionError, OSError):
                _LOGGER.exception("Failed to process file '%s'", file_path)

    _LOGGER.info(
        "YAML preprocessing completed. Processed files are available in '%s'.",
        output_dir,
    )
