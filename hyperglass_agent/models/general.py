import ipaddress
from typing import Union
from pydantic import validator, SecretStr
from exceptions import ConfigError
from constants import SUPPORTED_NOS
from models._utils import HyperglassModel


class General(HyperglassModel):
    debug: bool = False
    listen_address: Union[ipaddress.IPv4Address, ipaddress.IPv6Address] = "0.0.0.0"
    port: int = 8080
    mode: str
    secret: SecretStr

    @validator("mode")
    def validate_mode(cls, value):
        if value not in SUPPORTED_NOS:
            raise ConfigError(
                f"mode must be one of '{', '.join(SUPPORTED_NOS)}'. Received '{value}'"
            )
        return value
