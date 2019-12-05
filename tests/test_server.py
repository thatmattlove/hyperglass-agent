import json
import asyncio
from functools import update_wrapper
import httpx
from authlib.jose import JWS
from authlib.jose import JWS_ALGORITHMS
from logzero import logger as log

TEST_QUERY_DATA = {
    "query_type": "bgp_route",
    "vrf": "default",
    "afi": "ipv4_default",
    "source": "192.0.2.1",
    "target": "1.1.1.1",
}

TEST_HOST = "localhost"
TEST_PORT = 8080
TEST_SECRET = "TestSecret12345"

jws = JWS(algorithms=JWS_ALGORITHMS)

encrypted_data = jws.serialize_compact(
    protected={"alg": "HS256"}, payload=json.dumps(TEST_QUERY_DATA), key=TEST_SECRET
)


def async_command(func):
    func = asyncio.coroutine(func)

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return update_wrapper(wrapper, func)


@async_command
async def send_req():
    raw_response = await httpx.get(
        f"http://{TEST_HOST}:{TEST_PORT}/query/" + encrypted_data.decode("utf-8")
    )
    if raw_response.status_code != 200:
        log.error(f"{raw_response.status_code}: {raw_response.text}")
    else:
        log.info(json.dumps(raw_response.json(), indent=4))


if __name__ == "__main__":
    send_req()
