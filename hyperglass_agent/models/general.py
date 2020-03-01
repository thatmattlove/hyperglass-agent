"""Validate application config parameters."""
# Standard Library
import os
from typing import Optional
from pathlib import Path

# Third Party
# Third Party Imports
from pydantic import (
    FilePath,
    SecretStr,
    StrictInt,
    StrictStr,
    StrictBool,
    IPvAnyAddress,
    validator,
)

# Project
# Project Imports
from hyperglass_agent.constants import DEFAULT_MODE, SUPPORTED_NOS
from hyperglass_agent.exceptions import ConfigError
from hyperglass_agent.models._utils import HyperglassModel

APP_PATH = Path(os.environ["hyperglass_agent_directory"])


class Ssl(HyperglassModel):
    """Validate SSL config parameters."""

    enable: StrictBool = True
    cert: Optional[FilePath]
    key: Optional[FilePath]

    @validator("cert")
    def validate_cert(cls, value, values):
        """Pydantic validator: set default cert path if ssl is enabled.

        Arguments:
            value {Path|None} -- Path to cert file
            values {dict} -- Other values

        Returns:
            {Path} -- Path to cert file
        """
        cert_path = APP_PATH / "agent_cert.pem"
        if values["enable"] and value is None:
            if not cert_path.exists():
                raise ValueError(f"{str(cert_path)} does not exist.")
            value = cert_path
        return value

    @validator("key")
    def validate_key(cls, value, values):
        """Pydantic validator: set default key path if ssl is enabled.

        Arguments:
            value {Path|None} -- Path to key file
            values {dict} -- Other values

        Returns:
            {Path} -- Path to key file
        """
        key_path = APP_PATH / "agent_key.pem"

        if values["enable"] and value is None:
            if not key_path.exists():
                raise ValueError(f"{str(key_path)} does not exist.")
            value = key_path
        return value


class General(HyperglassModel):
    """Validate config parameters."""

    debug: StrictBool = False
    listen_address: IPvAnyAddress = "0.0.0.0"  # noqa: S104
    ssl: Ssl = Ssl()
    port: StrictInt = None
    mode: StrictStr = DEFAULT_MODE
    secret: SecretStr
    valid_duration: StrictInt = 60
    not_found_message: StrictStr = "{target} not found. ({afi})"

    @validator("port", pre=True, always=True)
    def validate_port(cls, value, values):
        """Pydantic validator: set default port based on SSL state.

        Arguments:
            value {int|None} -- Port
            values {dict} -- Other values

        Returns:
            {int} -- Port
        """
        if value is None and values["ssl"].enable:
            value = 8443
        elif value is None and not values["ssl"].enable:
            value = 8080
        return value

    @validator("mode")
    def validate_mode(cls, value):
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
