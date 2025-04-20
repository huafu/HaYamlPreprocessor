"""
YAML Preprocessor for Home Assistant.

This custom component preprocesses YAML files by copying them from an input directory
to an output directory, applying transformations such as variable substitution in file
inclusion. It is designed to simplify YAML management in Home Assistant configurations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .const import CONFIG_SCHEMA, DOMAIN, LOGGER, SERVICE_PROCESS_SCHEMA  # noqa: F401
from .transformer import process_yaml_files

if TYPE_CHECKING:
    from typing import Any

    from homeassistant.core import HomeAssistant, ServiceCall

import yaml


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
        LOGGER.error("Configuration missing for '%s'", DOMAIN)
        return False

    input_dir: str = conf.get("input_dir")
    output_dir: str = conf.get("output_dir")
    if not input_dir or not output_dir:
        LOGGER.error(
            "'input_dir' and 'output_dir' must be defined in the configuration."
        )
        return False

    # Complete the paths relative to the config directory.
    input_dir = hass.config.path(input_dir)
    output_dir = hass.config.path(output_dir)

    # Register the process service.
    def process_service(call: ServiceCall) -> None:
        try:
            process_yaml_files(input_dir, output_dir)
            # if the processing is successful, reload the configuration
            on_success: str | None = call.data.get("on_success")
            if on_success == "reload":
                LOGGER.info(
                    "YAML processing completed successfully."
                    " Reloading Home Assistant configuration..."
                )
                hass.services.call("homeassistant", "reload_core_config", {})
            elif on_success == "restart":
                LOGGER.info(
                    "YAML processing completed successfully."
                    " Restarting Home Assistant..."
                )
                hass.services.call("homeassistant", "restart", {})
        except (FileNotFoundError, PermissionError, yaml.YAMLError):
            LOGGER.exception("Error during YAML preprocessing")

    hass.services.register(
        DOMAIN, "process", process_service, schema=SERVICE_PROCESS_SCHEMA
    )
    LOGGER.info(
        "Component '%s' loaded. Service '%s.process' is available.", DOMAIN, DOMAIN
    )
    return True
