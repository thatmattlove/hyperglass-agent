# Standard Library Imports
import ipaddress
from typing import Union

# Third Party Imports
from pydantic import SecretStr
from pydantic import validator

# Project Imports
from hyperglass_agent.constants import DEFAULT_MODE
from hyperglass_agent.constants import SUPPORTED_NOS
from hyperglass_agent.exceptions import ConfigError
from hyperglass_agent.models._utils import HyperglassModel


class General(HyperglassModel):
    debug: bool = False
    listen_address: Union[ipaddress.IPv4Address, ipaddress.IPv6Address] = "0.0.0.0"
    port: int = 8080
    mode: str = DEFAULT_MODE
    secret: SecretStr
    valid_duration: int = 60
    not_found_message: str = "{target} not found. ({afi})"

    @validator("mode")
    def validate_mode(cls, value):
        if value not in SUPPORTED_NOS:
            raise ConfigError(
                f"mode must be one of '{', '.join(SUPPORTED_NOS)}'. Received '{value}'"
            )
        return value
