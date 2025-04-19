"""
Provides functionality for processing YAML files with custom constructors.

It includes:
- A custom YAML constructor for the `!include` tag to include external YAML files with
  variable substitution.
- A function to process YAML files from an input directory and save the processed files
  to an output directory.
"""

import re
import shutil
from pathlib import Path
from typing import Any

import yaml

from .const import AUTO_GENERATED_WARNING, LOGGER, README_CONTENT


class MissingFileKeyError(ValueError):
    """
    Exception raised when the 'file' key is missing in a !include node.

    This error is used to indicate that the required 'file' key is not provided
    in the dictionary associated with a !include YAML tag.
    """

    def __init__(self) -> None:
        """
        Initialize the MissingFileKeyError with a default error message.

        This constructor sets a predefined error message indicating that the
        'file' key is required in a !include node.
        """
        super().__init__("'file' key is required in !include node")


# Helper class to carry a tag with its associated value
class _RawTag:
    def __init__(self, tag: str, value: Any) -> None:
        self.tag = tag
        self.value = value

    def __repr__(self) -> str:
        return f"RawTag(tag={self.tag!r}, value={self.value!r})"


# Custom representer for our RawTag object,
# ensuring that the original tag (e.g. "!include_dir_list") is maintained.
def _raw_tag_representer(dumper: yaml.Dumper, data: _RawTag) -> yaml.Node:
    if isinstance(data.value, str):
        # Represent a scalar with its original tag.
        return dumper.represent_scalar(data.tag, data.value)
    if isinstance(data.value, list):
        return dumper.represent_sequence(data.tag, data.value)
    if isinstance(data.value, dict):
        return dumper.represent_mapping(data.tag, data.value)
    node = dumper.represent_data(data.value)
    node.tag = data.tag
    return node


# Register the representer for RawTag objects.
yaml.add_representer(_RawTag, _raw_tag_representer)


# Fallback constructor for unrecognized tags, with type hints.
def _fallback_constructor(loader: yaml.Loader, tag: str, node: yaml.Node) -> _RawTag:
    if isinstance(node, yaml.ScalarNode):
        value: Any = node.value  # Simply get the scalar value.
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node)
    elif isinstance(node, yaml.MappingNode):
        value = loader.construct_mapping(node)
    else:
        value = loader.construct_object(node)
    return _RawTag(tag, value)


# Register the fallback constructor for any unrecognized tags
yaml.Loader.add_multi_constructor("", _fallback_constructor)


# Define the custom constructor for !include
def _include_constructor(
    loader: yaml.Loader | yaml.UnsafeLoader | yaml.FullLoader, node: yaml.Node
) -> Any:
    # Load the value of the !include tag
    if not isinstance(node, yaml.MappingNode):
        return node

    # Construct the mapping from the node
    value = loader.construct_mapping(node, deep=True)

    # Extract the file path and variables from the dictionary
    file_path = value.get("file")
    vars_substitutions = value.get("vars", {})

    if not file_path:
        raise MissingFileKeyError

    # Resolve the file path relative to the current directory
    current_file_dir = Path(loader.name).parent  # Get the current file's directory
    resolved_file_path = current_file_dir / file_path

    # Load the content of the referenced YAML file (B)
    with resolved_file_path.open("r", encoding="utf-8") as f:
        file_content = f.read()

    # Replace variables (${xxx}) in the content with values from `vars`, defaulting to
    # an empty string
    file_content = re.sub(
        r"\$\{(\w+)\}",
        lambda match: str(vars_substitutions.get(match.group(1), "")),
        file_content,
    )

    # Parse the substituted content back as YAML
    return yaml.load(file_content, Loader=yaml.Loader)  # noqa: S506


# Register the custom constructor
yaml.add_constructor("!include", _include_constructor)


# Process YAML files with the custom constructor
def process_yaml_files(input_dir: str, output_dir: str) -> None:
    """
    Process YAML files from the input dir and save processed files to the output dir.

    This function processes YAML files by applying custom constructors and ensures
    the output directory is cleaned before saving the processed files.

    Args:
        input_dir: Path to the input directory containing YAML files.
        output_dir: Path to the output directory where processed files will be saved.

    """
    # Create paths objects
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    # Wipe the output directory
    if output_path.exists():
        LOGGER.debug("Wiping output directory: %s", output_path)
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # Copy all files from input dir to output dir except yaml files
    LOGGER.debug("Copying files from %s to %s", input_path, output_path)
    shutil.copytree(
        input_path,
        output_path,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("*.yaml", "*.yml"),
    )

    # Create a README.md file in the output directory
    _create_readme(output_path)

    # Process each YAML file in the input directory except the ones starting with "."
    for file in input_path.glob("**/*.y[a]ml"):
        if file.is_file() and not file.name.startswith("."):
            LOGGER.debug("Processing YAML file: %s", file)
            with file.open("r") as infile:
                # Pass the file name to the loader for relative path resolution
                loader = yaml.Loader(infile)
                loader.name = (
                    # Custom attribute to hold the current file full path
                    file.resolve().as_posix()
                )
                data = loader.get_data()

            # Construct the output file path
            relative_path = file.relative_to(input_path)
            output_file = output_path / relative_path
            with output_file.open("w") as outfile:
                # Add a warning comment to the top of the file
                outfile.write(AUTO_GENERATED_WARNING)
                # Write the processed data to the output file
                yaml.dump(data, outfile, sort_keys=False, encoding="utf-8")


def _create_readme(output_dir: Path) -> None:
    """Create a README.md file in the output directory."""
    readme_path: Path = output_dir / "README.md"
    try:
        with readme_path.open("w", encoding="utf-8") as readme_file:
            readme_file.write(README_CONTENT)
    except OSError:
        LOGGER.exception("Failed to create README.md in '%s'", output_dir)
