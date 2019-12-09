import jwt
import datetime
import asyncio
from functools import update_wrapper
from hyperglass_agent.config import params
from hyperglass_agent.exceptions import SecurityError


def sync_compatible(func):
    func = asyncio.coroutine(func)

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return update_wrapper(wrapper, func)


async def decode(payload):
    try:
        decoded = jwt.decode(
            payload, params.secret.get_secret_value(), algorithm="HS256"
        )
        decoded = decoded["payload"]
        return decoded
    except (KeyError, jwt.PyJWTError) as exp:
        raise SecurityError(str(exp)) from None


async def encode(response):
    payload = {
        "payload": response,
        "nbf": datetime.datetime.utcnow(),
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(seconds=params.valid_duration),
    }
    encoded = jwt.encode(payload, params.secret.get_secret_value(), algorithm="HS256")
    return encoded
