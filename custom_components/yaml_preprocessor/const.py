"""
Constants and logger setup for the YAML Preprocessor integration.

This module defines:
- LOGGER: A logger instance for the integration.
- DOMAIN: The domain name for the YAML Preprocessor integration.
"""

import logging

import voluptuous as vol

# Service schema: an optional "on_success" parameter must be either "reload" or
# "restart".
SERVICE_PROCESS_SCHEMA = vol.Schema(
    {
        vol.Optional("on_success"): vol.In(["reload", "restart"]),
    },
    extra=vol.ALLOW_EXTRA,
)

# The logger for the YAML Preprocessor integration.
LOGGER: logging.Logger = logging.getLogger(__package__)

# The domain name for the YAML Preprocessor integration.
DOMAIN: str = "yaml_preprocessor"


# Warning comment to prepend to each YAML file in the output directory
AUTO_GENERATED_WARNING: str = (
    "# WARNING: This file is auto-generated. Do not modify this file directly.\n"
    "# Please edit the corresponding file in the input directory.\n\n"
)

# Content of the README file in the output directory
README_CONTENT: str = (
    "WARNING: This directory is wiped and regenerated entirely during each "
    "processing run.\n"
    "Do not modify the contents directly. Edit files in the input directory "
    "instead.\n"
)
