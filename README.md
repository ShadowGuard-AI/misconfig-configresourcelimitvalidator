![Banner](banner.png)

# misconfig-ConfigResourceLimitValidator
Checks resource-related configuration parameters (e.g., memory allocation, CPU cores) against system limits and recommends adjustments to prevent resource exhaustion. Uses psutil to query system resource limits. - Focused on Check for misconfigurations in configuration files or infrastructure definitions

## Memory unit
`memory_limit` is a number, and its unit is explicit, never guessed from the value type or size. The config may set `memory_limit_unit` to `MB` or `GB`. When `memory_limit_unit` is absent, the unit is MB. The same number therefore always means the same amount of memory, whether it is written as `50` or as `50.0`. A unit other than MB or GB is an invalid value.

## Exit codes
A run exits 1 when any check reports WARNING, when a limit value is invalid, or when neither limit key is present and nothing was validated. A run with at least one limit checked and no WARNING exits 0, including a run where only one of the two limits is specified. Zero, negative, and boolean limit values are invalid and exit 1.

## Install
`git clone https://github.com/ShadowGuardAI/misconfig-configresourcelimitvalidator`
`pip install -r requirements.txt`

## Usage
`python3 main.py -c CONFIG_FILE [-t {yaml,json}] [-l LOG_LEVEL] [--cpu_limit_key CPU_LIMIT_KEY] [--memory_limit_key MEMORY_LIMIT_KEY]`

## Parameters
- `-h, --help`: Show help message and exit
- `-c, --config_file`: Path to the configuration file (YAML or JSON) (required).
- `-t, --config_type`: Type of configuration file (yaml or json). If not specified, attempt to infer from file extension.
- `-l, --log_level`: Set the logging level (default: INFO). One of DEBUG, INFO, WARNING, ERROR, CRITICAL.
- `--cpu_limit_key`: Key in the config file for the CPU limit setting (default: cpu_limit).
- `--memory_limit_key`: Key in the config file for the memory limit setting (default: memory_limit).

## License
Copyright (c) ShadowGuardAI
