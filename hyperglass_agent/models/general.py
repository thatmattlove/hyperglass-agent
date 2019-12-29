"""Validate application config parameters."""

# Standard Library Imports
from ipaddress import IPv4Address
from ipaddress import IPv6Address
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
    """Validate config parameters."""

    debug: bool = False
    listen_address: Union[IPv4Address, IPv6Address] = "0.0.0.0"  # noqa: S104
    port: int = 8080
    mode: str = DEFAULT_MODE
    secret: SecretStr
    valid_duration: int = 60
    not_found_message: str = "{target} not found. ({afi})"

    @validator("mode")
    def validate_mode(cls, value):  # noqa: N805
        """Pydantic validator: validate mode is supported.

        Raises:
            ConfigError: Raised if mode is not supported.

        Returns:
            {str} -- Sets mode attribute if valid.
        """
        if value not in SUPPORTED_NOS:
            raise ConfigError(
                f"mode must be one of '{', '.join(SUPPORTED_NOS)}'. Received '{value}'"
            )
        return value
