import jwt
import datetime
from hyperglass_agent.config import params
from hyperglass_agent.exceptions import SecurityError


async def jwt_decode(payload):
    try:
        decoded = jwt.decode(
            payload, params.secret.get_secret_value(), algorithm="HS256"
        )
        decoded = decoded["payload"]
        return decoded
    except (KeyError, jwt.PyJWTError) as exp:
        raise SecurityError(str(exp)) from None


async def jwt_encode(response):
    payload = {
        "payload": response,
        "nbf": datetime.datetime.utcnow(),
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(seconds=params.valid_duration),
    }
    encoded = jwt.encode(payload, params.secret.get_secret_value(), algorithm="HS256")
    return encoded.decode("utf-8")
