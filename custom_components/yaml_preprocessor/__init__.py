"""
YAML pre-processor for Home Assistant.

For more details about this integration, please refer to
https://github.com/huafu/HaYamlPreprocessor
"""

from __future__ import annotations

import yaml

from .const import LOGGER
from .include import include_constructor


async def async_setup() -> bool:
    """
    Set up the YAML Preprocessor integration.

    This function registers the !include YAML constructor and logs
    that the integration has been loaded.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        config (dict): The configuration dictionary.

    Returns:
        bool: True if the setup was successful.

    """
    # Register the !include YAML constructor for both scalar and mapping nodes.
    yaml.add_constructor("!include", include_constructor)
    LOGGER.info("YAML Preprocessor integration loaded - !include tag registered")
    return True
