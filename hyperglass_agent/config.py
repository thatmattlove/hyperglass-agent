"""Read YAML config file, validate, and set defaults."""

# Standard Library Imports
import asyncio
from pathlib import Path

# Third Party Imports
import yaml
from aiofile import AIOFile
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


async def get_config():
    """Read config file & load YAML to dict.

    Raises:
        ConfigError: Raised if file is not found.
        ConfigError: Raised if there is a YAML parsing error.

    Returns:
        {dict} -- Loaded config
    """
    try:
        async with AIOFile(CONFIG_FILE, "r") as file:
            config_file = await file.read()
            raw_config = yaml.safe_load(config_file)

    except FileNotFoundError:
        raise ConfigError("Config file not found.") from None

    except (yaml.YAMLError, yaml.MarkedYAMLError) as yaml_error:
        raise ConfigError(yaml_error) from None
    return raw_config


raw_config = asyncio.run(get_config())

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
    log.debug("Debugging Enabled")

params = user_config
commands = user_commands

log.debug(params.json())
log.debug(commands.json())
