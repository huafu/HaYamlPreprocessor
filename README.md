# YAML Pre-processor

[![HACS Badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://hacs.xyz/)
[![GitHub release](https://img.shields.io/github/release/huafu/HaYamlPreprocessor.svg)](https://github.com/huafu/HaYamlPreprocessor/releases)

**Yaml Preprocessor** is a custom Home Assistant integration that brings ESPHome‑style YAML preprocessing to your configuration. It registers a custom YAML constructor for the `!include` tag—allowing you to include external YAML files with variable substitution (e.g. replacing any instance of `${var_name}` with its provided value).

## Usage

1. Install the integration via HACS or manually.
2. Add the integration to your configuration.yaml file:
    ```yaml
    yaml_preprocessor:
      input_dir: packages/input
      output_dir: packages/output
    # Example of using the integration with Home Assistant packages
    # but you can use it with any other !include_dir tag.
    homeassistant:
      packages: !include_dir_named packages/output
    ```
3. Restart Home Assistant to load the integration.
4. Create a directory for your YAML files (e.g. `packages/input`).
5. Within the `input_dir`, create YAML files using (or not) the `!include` tag. For example:
    ```yaml
    # packages/input/hello.yaml
    sensors:
    - platform: template
        sensors:
        hello_world: !include
          file: hello/.sensor.yaml
            vars:
            name: "World"
            id: "one"
        hello_huafu: !include
          file: hello/.sensor.yaml
            vars:
            name: "Huafu"
            id: "two"
    ```

    ```yaml
    # packages/input/hello/.sensor.yaml
    unique_id: hello_${id}
    friendly_name: Hello ${name}
    value_template: >
      {% if is_state('sensor.hello_${id}', 'on') %}
        Hello ${name}!
      {% else %}
        Goodbye ${name}!
      {% endif %}
    ```
6. Call the `yaml_preprocessor.process` service to process the input files and generate the output files.
7. Reload Home Assistant configuration to see the changes.

## What?

This repository contains multiple files, here is a overview:

File | Purpose | Documentation
-- | -- | --
`.devcontainer.json` | Used for development/testing with Visual Studio Code. | [Documentation](https://code.visualstudio.com/docs/remote/containers)
`.github/ISSUE_TEMPLATE/*.yml` | Templates for the issue tracker | [Documentation](https://help.github.com/en/github/building-a-strong-community/configuring-issue-templates-for-your-repository)
`custom_components/yaml_preprocessor/*` | Integration files, this is where everything happens. | [Documentation](https://developers.home-assistant.io/docs/creating_component_index)
`CONTRIBUTING.md` | Guidelines on how to contribute. | [Documentation](https://help.github.com/en/github/building-a-strong-community/setting-guidelines-for-repository-contributors)
`LICENSE` | The license file for the project. | [Documentation](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/licensing-a-repository)
`README.md` | The file you are reading now, should contain info about the integration, installation and configuration instructions. | [Documentation](https://help.github.com/en/github/writing-on-github/basic-writing-and-formatting-syntax)
`requirements.txt` | Python packages used for development/lint/testing this integration. | [Documentation](https://pip.pypa.io/en/stable/user_guide/#requirements-files)

## Next steps

These are some next steps you may want to look into:
- Add tests to your integration, [`pytest-homeassistant-custom-component`](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component) can help you get started.
- Add brand images (logo/icon) to https://github.com/home-assistant/brands.
- Create your first release.
- Share your integration on the [Home Assistant Forum](https://community.home-assistant.io/).
- Submit your integration to [HACS](https://hacs.xyz/docs/publish/start).
