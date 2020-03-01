"""Handle JSON Web Token Encoding & Decoding."""

# Standard Library
# Standard Library Imports
import datetime

# Third Party
# Third Party Imports
import jwt

# Project
# Project Imports
from hyperglass_agent.config import params
from hyperglass_agent.exceptions import SecurityError


async def jwt_decode(payload):
    """Decode the request claim."""
    try:
        decoded = jwt.decode(
            payload, params.secret.get_secret_value(), algorithm="HS256"
        )
        decoded = decoded["payload"]
        return decoded
    except (KeyError, jwt.PyJWTError) as exp:
        raise SecurityError(str(exp)) from None


async def jwt_encode(response):
    """Encode the response claim."""
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
