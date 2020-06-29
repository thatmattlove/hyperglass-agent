"""Web server frontend, passes raw query to backend validation & execution."""

# Standard Library
import json

# Third Party
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Project
from hyperglass_agent import __title__, __version__, __description__
from hyperglass_agent.log import log
from hyperglass_agent.config import APP_PATH, params
from hyperglass_agent.execute import run_query
from hyperglass_agent.payload import jwt_decode, jwt_encode
from hyperglass_agent.exceptions import HyperglassAgentError
from hyperglass_agent.models.request import Request, EncodedRequest

CERT_PATH = APP_PATH / "agent_cert.pem"
KEY_PATH = APP_PATH / "agent_key.pem"


API_PARAMS = {
    "host": params.listen_address.compressed,
    "port": params.port,
    "debug": params.debug,
}

if params.ssl.enable:
    API_PARAMS.update({"ssl_certfile": CERT_PATH, "ssl_keyfile": KEY_PATH})

if params.debug:
    API_PARAMS.update({"log_level": "debug"})

api = FastAPI(
    title=__title__,
    description=__description__,
    version=__version__,
    docs_url=None,
    redoc_url="/docs",
)


@api.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Handle application errors.

    Arguments:
        request {object} -- Request object
        exc {object} -- Exception object

    Returns:
        {str} -- JSON response
    """
    log.error(str(exc.detail))
    return JSONResponse(content={"error": str(exc.detail)}, status_code=exc.status_code)


@api.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors.

    Arguments:
        request {object} -- Request object
        exc {object} -- Exception object

    Returns:
        {str} -- JSON response
    """
    log.error(str(exc))
    return JSONResponse(content={"error": str(exc)}, status_code=400)


@api.post("/query/", status_code=200, response_model=EncodedRequest)
async def query_entrypoint(query: EncodedRequest):
    """Validate and process input request.

    Arguments:
        query {dict} -- Encoded JWT

    Returns:
        {obj} -- JSON response
    """
    try:
        log.debug(f"Raw Query JSON: {query.json()}")

        decrypted_query = await jwt_decode(query.encoded)
        decrypted_query = json.loads(decrypted_query)

        log.debug(f"Decrypted Query: {decrypted_query}")

        validated_query = Request(**decrypted_query)
        query_output = await run_query(validated_query)

        log.debug(f"Query Output:\n{query_output}")

        encoded = await jwt_encode(query_output)
        return {"encoded": encoded}

    except ValidationError as err_validation:
        raise RequestValidationError(str(err_validation))

    except HyperglassAgentError as err_agent:
        raise HTTPException(status_code=err_agent.code, detail=str(err_agent))


def start():
    """Start the web server with Uvicorn ASGI."""
    import uvicorn

    uvicorn.run(api, **API_PARAMS)


if __name__ == "__main__":
    start()
