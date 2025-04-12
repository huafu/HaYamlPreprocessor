"""
Provide a custom YAML constructor for the !include tag.

The !include tag allows including external YAML files and supports variable
substitution for dynamic content loading.
"""

import re
from pathlib import Path
from typing import Any

import yaml


def include_constructor(
    loader: yaml.Loader | yaml.FullLoader | yaml.UnsafeLoader, node: yaml.Node
) -> Any:
    """
    Construct an !include tag parser.

    Supports two syntaxes:

    1. Scalar syntax:
       automation: !include automations.yaml

    2. Mapping syntax:
       script: !include
         file: scripts.yaml
         vars:
           greeting: "Hello World"

    It loads the target file, performs variable substitution (replacing any
    instance of ${var_name} with its value from the provided vars), and returns
    the parsed YAML content.
    """
    # If the node is a scalar, use its value as the file path.
    if isinstance(node, yaml.ScalarNode):
        file_path = loader.construct_scalar(node)
        vars_dict = {}
    # If the node is a mapping, expect a file key and optionally a vars key.
    elif isinstance(node, yaml.MappingNode):
        mapping = loader.construct_mapping(node, deep=True)
        file_path = mapping.get("file")
        vars_dict = mapping.get("vars", {})
    else:
        msg = "Unsupported node type in !include"
        raise yaml.YAMLError(msg)

    # If file_path is not provided or is not a string, raise an error.
    if not file_path:
        msg = "!include tag must include a file path"
        raise yaml.YAMLError(msg)
    if not isinstance(file_path, str):
        msg = f"File path must be a string: {file_path}"
        raise yaml.YAMLError(msg)

    # If vars_dict is not a dictionary, raise an error.
    if not isinstance(vars_dict, dict):
        msg = f"Vars must be a dictionary: {vars_dict}"
        raise yaml.YAMLError(msg)

    path = Path(file_path)
    try:
        with path.open("r") as f:
            file_text = f.read()
    except (FileNotFoundError, PermissionError, OSError) as e:
        msg = f"Error reading file {file_path}: {e}"
        raise yaml.YAMLError(msg) from e

    # Replace any ${var_name} with the value from vars_dict.
    pattern = re.compile(r"\$\{(\w+)\}")

    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        return str(vars_dict.get(var_name, match.group(0)))

    substituted_text = pattern.sub(replacer, file_text)

    try:
        data = yaml.safe_load(substituted_text)
    except yaml.YAMLError as e:
        msg = f"Error parsing YAML from {file_path}: {e}"
        raise yaml.YAMLError(msg) from e
    return data
