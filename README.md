[![GitHub Stars](https://img.shields.io/github/stars/huafu/HaYamlPreprocessor?style=social)](https://github.com/huafu/HaYamlPreprocessor/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/huafu/HaYamlPreprocessor)](https://github.com/huafu/HaYamlPreprocessor/issues)
[![Validate Status](https://img.shields.io/github/actions/workflow/status/huafu/HaYamlPreprocessor/validate.yml?branch=main)](https://github.com/huafu/HaYamlPreprocessor/actions)
[![License](https://img.shields.io/github/license/huafu/HaYamlPreprocessor)](https://github.com/huafu/HaYamlPreprocessor/blob/main/LICENSE)
[![HACS](https://img.shields.io/badge/HACS-Custom-blue.svg)](https://hacs.xyz/)

# YAML Preprocessor for Home Assistant
The YAML Preprocessor is a tool designed to enhance the YAML configuration experience in Home Assistant. It allows you to preprocess your YAML files, enabling features like variable substitution, making your configurations cleaner and more maintainable.

## Warning
This is an experimental project and should be used with caution. It is not officially supported by Home Assistant, and there may be bugs or issues that arise during use. Always back up your configuration files before using the preprocessor.
Pre-processing the core configuration file is not handled by this preprocessor. It is recommended to use the preprocessor only for included files, such as packages or custom components. The preprocessor will not work with the main configuration file (`configuration.yaml`) directly.

## Installation
You can install the YAML Preprocessor in two ways:
1. **Using HACS (Home Assistant Community Store)**:
    - Open HACS in your Home Assistant instance.
    - Go to the "Integrations" section.
    - Search for "YAML Preprocessor".
    - Click on "Install".
    - Restart Home Assistant to apply the changes.
2. **Manual Installation**:
    - Download the latest release from the [GitHub repository](https://github.com/huafu/HaYamlPreprocessor/releases).
    - Extract the contents of the downloaded file.
    - Copy the `custom_components/yaml_preprocessor` folder into your Home Assistant `custom_components` directory.
    - Restart Home Assistant to apply the changes.

## Configuration
To configure the YAML Preprocessor, you need to add the following lines to your `configuration.yaml` file:

```yaml
yaml_preprocessor:
  # Dot-files in the input directory will be ignored but can be used as reusable snippets
  input_dir: packages/input
  # be careful, this directory will be deleted each time you run the preprocessor
  output_dir: packages/output

# Example for using the preprocessor in your configuration
homeassistant:
  packages: !include_dir_named packages/output
```

## Usage
The YAML Preprocessor allows you to create reusable YAML snippets and include them in your main configuration. Here is an example of how to use it following the previous configuration:

1. Create a file named `packages/input/.light.yaml` with the following content:
   ```yaml
    unique_id: light_${id}_has_red
    name: ${name} Light has some red
    state: >
      {% if is_state('light.light_${id}', 'on') %}
        {% set rgb = state_attr('light.light_${id}', 'rgb_color') %}
        {{ rgb and rgb[0] > 0 }}
      {% else %}
        false
      {% endif %}
    ```
2. Create a file named `packages/input/lights.yaml` with the following content:
    ```yaml
    template:
      - binary_sensor:
          - !include
              file: ./.light.yaml
              vars:
                id: living_room
                name: Living Room
          - !include
              file: ./.light.yaml
              vars:
                id: kitchen
                name: Kitchen
    ```
3. Call the preprocessor to generate the output: in Home Assistant, go to Developer Tools > Services and call the `yaml_preprocessor.preprocess` service. This will generate `packages/output/lights.yaml` with the following content:
    ```yaml
    template:
      - binary_sensor:
          - unique_id: light_living_room_has_red
            name: Living Room Light has some red
            state: >
              {% if is_state('light.light_living_room', 'on') %}
                {% set rgb = state_attr('light.light_living_room', 'rgb_color') %}
                {{ rgb and rgb[0] > 0 }}
              {% else %}
                false
              {% endif %}
          - unique_id: light_kitchen_has_red
            name: Kitchen Light has some red
            state: >
              {% if is_state('light.light_kitchen', 'on') %}
                {% set rgb = state_attr('light.light_kitchen', 'rgb_color') %}
                {{ rgb and rgb[0] > 0 }}
              {% else %}
                false
              {% endif %}
    ```

## Contributing
We welcome contributions to the YAML Preprocessor project! If you have suggestions, bug reports, or would like to contribute code, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with clear messages.
4. Push your changes to your forked repository.
5. Create a pull request to the main repository.
6. Ensure your code adheres to the project's coding standards and passes all tests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Credits
This project is maintained by [huafu](https://github.com/huafu) and contributors. Special thanks to the Home Assistant community for their support and feedback.