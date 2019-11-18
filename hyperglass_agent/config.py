from pathlib import Path
import yaml
from pydantic import ValidationError
from hyperglass_agent.exceptions import ConfigError, ConfigInvalid
from hyperglass_agent.models.commands import Commands
from hyperglass_agent.models.general import General

CONFIG_FILE = Path().cwd() / "config.yaml"

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
    raw_config_commands = {"commands": raw_config.pop("commands", None)}
    user_config = General(**raw_config)
    if raw_config_commands is not None:
        user_commands = Commands.import_params(**raw_config_commands)
except ValidationError as validation_errors:
    errors = validation_errors.errors()
    for error in errors:
        raise ConfigInvalid(
            field=": ".join([str(item) for item in error["loc"]]),
            error_msg=error["msg"],
        )

params = user_config
commands = user_commands
