"""
utilities used across several scripts
"""

import argparse
import importlib.util
from pathlib import Path


def parse_args():
    """
    Parse command-line arguments.

    This function sets up the argument parser for the script, specifying
    the expected arguments and their types. It expects a `--config` argument,
    which is required and should be a Path object pointing to the configuration
    file. The suffix '.py' can be omitted and will be appended automatically if
    missing.

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Script to run with user configuration."
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to the configuration file. The suffix '.py' can be omitted.",
    )
    return parser.parse_args()


def load_config(config_name):
    """
    Load a configuration module from the given file name.

    This function accepts the name of a configuration file, ensures it has the
    '.py' extension (adding it if necessary), resolves it to an absolute path,
    checks if the file exists, and loads it as a Python module.

    Args:
        config_name (str or Path): The name of the configuration file. Can be passed
                                   without the '.py' extension, which will be added
                                   automatically if not present.

    Returns:
        module: The loaded configuration module.

    Raises:
        ValueError: If the provided configuration file has an extension other than '.py'.
        FileNotFoundError: If the resolved configuration file does not exist.
    """
    config_file = Path(config_name)

    # Ensure the config file has the .py extension
    if config_file.suffix:
        # If a suffix is present and it's not '.py', raise an error
        if config_file.suffix != ".py":
            raise ValueError(
                f"The configuration file {config_file} must have a .py extension."
            )
    else:
        # If no suffix is present, add .py
        config_file = config_file.with_suffix(".py")

    # Create an absolute path
    config_path = config_file.resolve()

    # Ensure the file exists
    if not config_path.exists():
        raise FileNotFoundError(f"The configuration file {config_path} does not exist.")

    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config
