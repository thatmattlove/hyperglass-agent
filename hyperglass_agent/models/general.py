"""Validate application config parameters."""

from typing import Optional

# Third Party Imports
from pydantic import FilePath
from pydantic import IPvAnyAddress
from pydantic import SecretStr
from pydantic import StrictBool
from pydantic import StrictInt
from pydantic import StrictStr
from pydantic import validator

# Project Imports
from hyperglass_agent.constants import CERT_PATH
from hyperglass_agent.constants import DEFAULT_MODE
from hyperglass_agent.constants import KEY_PATH
from hyperglass_agent.constants import SUPPORTED_NOS
from hyperglass_agent.exceptions import ConfigError
from hyperglass_agent.models._utils import HyperglassModel


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
        if values["enable"] and value is None:
            if not CERT_PATH.exists():
                raise ValueError(f"{str(CERT_PATH)} does not exist.")
            value = CERT_PATH
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
        if values["enable"] and value is None:
            if not KEY_PATH.exists():
                raise ValueError(f"{str(KEY_PATH)} does not exist.")
            value = KEY_PATH
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
