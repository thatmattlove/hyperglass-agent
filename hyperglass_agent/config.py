"""Read YAML config file, validate, and set defaults."""

# Standard Library
import os
from pathlib import Path

# Third Party
import yaml
from pydantic import ValidationError

# Project
from hyperglass_agent.util import log, set_app_path
from hyperglass_agent.constants import LOG_LEVELS, LOG_HANDLER
from hyperglass_agent.exceptions import ConfigError, ConfigInvalid
from hyperglass_agent.models.general import General
from hyperglass_agent.models.commands import Commands

if os.environ.get("hyperglass_agent_directory") is None:
    set_app_path(required=True)

try:
    APP_PATH = Path(os.environ["hyperglass_agent_directory"])
except KeyError:
    raise ConfigError(
        "No application path was found. Please consult the setup documentation."
    )

CONFIG_FILE = APP_PATH / "config.yaml"


def _get_config():
    """Read config file & load YAML to dict.

    Raises:
        ConfigError: Raised if file is not found.
        ConfigError: Raised if there is a YAML parsing error.

    Returns:
        {dict} -- Loaded config
    """
    try:
        with CONFIG_FILE.open("r") as file:
            config_file = file.read()
            raw_config = yaml.safe_load(config_file)

    except FileNotFoundError:
        raise ConfigError("Config file not found.") from None

    except (yaml.YAMLError, yaml.MarkedYAMLError) as yaml_error:
        raise ConfigError(yaml_error) from None
    return raw_config


_raw_config = _get_config()

try:
    _commands = _raw_config.pop("commands", None)
    _user_config = General(**_raw_config)

    if _commands is not None:
        _user_commands = Commands.import_params(mode=_user_config.mode, **_commands)
    else:
        _user_commands = Commands.import_params(mode=_user_config.mode)

except ValidationError as validation_errors:
    _errors = validation_errors.errors()
    for error in _errors:
        raise ConfigInvalid(
            field=": ".join([str(item) for item in error["loc"]]),
            error_msg=error["msg"],
        )

LOG_LEVEL = "INFO"
if _user_config.debug:
    LOG_LEVEL = "DEBUG"
    LOG_HANDLER["level"] = LOG_LEVEL
    log.remove()
    log.configure(handlers=[LOG_HANDLER], levels=LOG_LEVELS)
    log.debug("Debugging Enabled")

params = _user_config
commands = _user_commands

log.debug(params.json())
log.debug(commands.json())
