#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sys
import psutil
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argparse argument parser.
    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    parser = argparse.ArgumentParser(
        description="Checks resource-related configuration parameters against system limits and recommends adjustments."
    )

    parser.add_argument(
        "-c",
        "--config_file",
        help="Path to the configuration file (YAML or JSON).",
        required=True,
    )

    parser.add_argument(
        "-t",
        "--config_type",
        choices=["yaml", "json"],
        help="Type of configuration file (yaml or json).  If not specified, attempt to infer from file extension.",
    )

    parser.add_argument(
        "-l",
        "--log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO).",
    )
    
    parser.add_argument(
        "--cpu_limit_key",
        default="cpu_limit",
        help="Key in the config file for the CPU limit setting (default: cpu_limit)."
    )

    parser.add_argument(
        "--memory_limit_key",
        default="memory_limit",
        help="Key in the config file for the memory limit setting (default: memory_limit)."
    )

    return parser


def load_config(config_file, config_type=None):
    """
    Loads a configuration file (YAML or JSON).
    Args:
        config_file (str): Path to the configuration file.
        config_type (str, optional): Type of configuration file ("yaml" or "json"). If None, infers from file extension. Defaults to None.
    Returns:
        dict: The configuration data as a dictionary.
    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If the file type cannot be determined or if parsing fails.
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    if config_type is None:
        _, ext = os.path.splitext(config_file)
        if ext.lower() == ".yaml" or ext.lower() == ".yml":
            config_type = "yaml"
        elif ext.lower() == ".json":
            config_type = "json"
        else:
            raise ValueError(
                "Could not determine configuration file type. Please specify with --config_type."
            )

    try:
        with open(config_file, "r") as f:
            if config_type == "yaml":
                config_data = yaml.safe_load(f)
            elif config_type == "json":
                config_data = json.load(f)
            else:
                raise ValueError("Invalid configuration type. Must be 'yaml' or 'json'.")
        return config_data
    except Exception as e:
        raise ValueError(f"Error loading configuration file: {e}")


def validate_resource_limits(config, cpu_limit_key="cpu_limit", memory_limit_key="memory_limit"):
    """
    Validates resource limits against system limits.
    Args:
        config (dict): The configuration data.
        cpu_limit_key (str, optional): Key for CPU limit in config. Defaults to "cpu_limit".
        memory_limit_key (str, optional): Key for memory limit in config. Defaults to "memory_limit".
    Returns:
        dict: A dictionary containing validation results.
    """
    results = {}
    try:
        # Check CPU limit
        if cpu_limit_key in config:
            cpu_limit = config[cpu_limit_key]
            if not isinstance(cpu_limit, (int, float)):
                raise ValueError(f"Invalid CPU limit value: {cpu_limit}. Must be a number.")
            
            cpu_count = psutil.cpu_count()
            if cpu_limit > cpu_count:
                results["cpu"] = {
                    "status": "WARNING",
                    "message": f"CPU limit ({cpu_limit}) exceeds available CPU cores ({cpu_count}).",
                }
            else:
                results["cpu"] = {"status": "OK", "message": "CPU limit is within acceptable range."}
        else:
            results["cpu"] = {"status": "INFO", "message": "CPU limit not specified in configuration."}

        # Check memory limit
        if memory_limit_key in config:
            memory_limit = config[memory_limit_key]
            if not isinstance(memory_limit, (int, float)):
                raise ValueError(f"Invalid memory limit value: {memory_limit}. Must be a number.")

            # Convert memory limit to bytes if necessary (assuming it's in MB or GB)
            if isinstance(memory_limit, float) and memory_limit < 100: #arbitrary cutoff for potentially being in GB vs bytes.  Will need adjusted based on use case
                 memory_limit_bytes = int(memory_limit * 1024 * 1024 * 1024) #convert GB to bytes
            else:
                 memory_limit_bytes = int(memory_limit * 1024 * 1024) #convert MB to bytes

            virtual_memory = psutil.virtual_memory()
            total_memory = virtual_memory.total

            if memory_limit_bytes > total_memory:
                results["memory"] = {
                    "status": "WARNING",
                    "message": f"Memory limit ({memory_limit_bytes} bytes) exceeds available system memory ({total_memory} bytes).",
                }
            else:
                results["memory"] = {"status": "OK", "message": "Memory limit is within acceptable range."}
        else:
            results["memory"] = {"status": "INFO", "message": "Memory limit not specified in configuration."}

    except ValueError as e:
        logging.error(f"Validation error: {e}")
        results["error"] = str(e)
    except Exception as e:
        logging.exception("An unexpected error occurred during validation:")
        results["error"] = f"An unexpected error occurred: {e}"

    return results


def main():
    """
    Main function to execute the script.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    # Set logging level
    logging.getLogger().setLevel(args.log_level)

    try:
        # Load configuration
        config = load_config(args.config_file, args.config_type)

        # Validate resource limits
        results = validate_resource_limits(config, args.cpu_limit_key, args.memory_limit_key)

        # Print validation results
        for resource, result in results.items():
            logging.info(f"{resource.capitalize()} Check: {result['message']} ({result['status']})")

        # Offensive tool step (example) - placeholder to inject a vulnerability based on misconfiguration
        if any(result.get("status") == "WARNING" for result in results.values()):
            logging.warning("Potential misconfiguration detected. Consider further investigation.")
            # In a real offensive tool, this is where you would potentially trigger an action
            # based on the identified misconfiguration.  For example, if the CPU limit
            # is higher than available cores, a crafted request might be sent to try to exhaust
            # resources, causing a denial of service.  This is a placeholder only.
            # offensive_action(config)  # Placeholder for offensive action

    except FileNotFoundError as e:
        logging.error(e)
        sys.exit(1)
    except ValueError as e:
        logging.error(e)
        sys.exit(1)
    except Exception as e:
        logging.exception("An unexpected error occurred:")
        sys.exit(1)


if __name__ == "__main__":
    # Usage Example:
    # Create a config file (e.g., config.yaml)
    # Run the script: python misconfig_validator.py -c config.yaml
    # or: python misconfig_validator.py -c config.yaml -t yaml -l DEBUG

    main()