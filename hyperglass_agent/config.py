# Standard Library Imports
from pathlib import Path

# Third Party Imports
import yaml
from pydantic import ValidationError

# Project Imports
from hyperglass_agent.constants import LOG_HANDLER
from hyperglass_agent.constants import LOG_LEVELS
from hyperglass_agent.exceptions import ConfigError
from hyperglass_agent.exceptions import ConfigInvalid
from hyperglass_agent.models.commands import Commands
from hyperglass_agent.models.general import General
from hyperglass_agent.util import log

WORKING_DIR = Path(__file__).resolve().parent

CONFIG_FILE = WORKING_DIR / "config.yaml"

try:
    with CONFIG_FILE.open("r") as config_file:
        raw_config = yaml.safe_load(config_file)
except FileNotFoundError:
    raise ConfigError(
        "Config file not found. A config file is required for authentication at least."
    ) from None
except (yaml.YAMLError, yaml.MarkedYAMLError) as yaml_error:
    raise ConfigError(yaml_error) from None

try:
    raw_config_commands = raw_config.pop("commands", None)
    user_config = General(**raw_config)
    if raw_config_commands is not None:
        user_commands = Commands.import_params(
            mode=user_config.mode, **raw_config_commands
        )
    else:
        user_commands = Commands.import_params(mode=user_config.mode)
except ValidationError as validation_errors:
    errors = validation_errors.errors()
    for error in errors:
        raise ConfigInvalid(
            field=": ".join([str(item) for item in error["loc"]]),
            error_msg=error["msg"],
        )

LOG_LEVEL = "INFO"
if user_config.debug:
    LOG_LEVEL = "DEBUG"
    LOG_HANDLER["level"] = LOG_LEVEL
    log.remove()
    log.configure(handlers=[LOG_HANDLER], levels=LOG_LEVELS)

log.debug("Debug On")

params = user_config
commands = user_commands
