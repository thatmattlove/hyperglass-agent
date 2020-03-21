"""Handle JSON Web Token Encoding & Decoding."""

# Standard Library
import datetime

# Third Party
import jwt

# Project
from hyperglass_agent.config import params
from hyperglass_agent.exceptions import SecurityError


async def jwt_decode(*args, **kwargs):
    """Decode the request claim."""
    return _jwt_decode(*args, **kwargs)


async def jwt_encode(*args, **kwargs):
    """Encode the response claim."""
    return _jwt_encode(*args, **kwargs)


def _jwt_decode(payload):
    try:
        decoded = jwt.decode(
            payload, params.secret.get_secret_value(), algorithm="HS256"
        )
        decoded = decoded["payload"]
        return decoded
    except (KeyError, jwt.PyJWTError) as exp:
        raise SecurityError(str(exp)) from None


def _jwt_encode(response):
    payload = {
        "payload": response,
        "nbf": datetime.datetime.utcnow(),
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(seconds=params.valid_duration),
    }
    encoded = jwt.encode(
        payload, params.secret.get_secret_value(), algorithm="HS256"
    ).decode("utf-8")
    return encoded
