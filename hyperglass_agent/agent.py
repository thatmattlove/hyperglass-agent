"""Web server frontend, passes raw query to backend validation & execution."""

# Standard Library Imports
import json
from pathlib import Path

# Third Party Imports
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

# Project Imports
from hyperglass_agent.config import LOG_LEVEL
from hyperglass_agent.config import params
from hyperglass_agent.exceptions import HyperglassAgentError
from hyperglass_agent.execute import run_query
from hyperglass_agent.models.request import EncodedRequest
from hyperglass_agent.models.request import Request
from hyperglass_agent.payload import jwt_decode
from hyperglass_agent.payload import jwt_encode
from hyperglass_agent.util import log

WORKING_DIR = Path(__file__).parent

CERT_FILE = WORKING_DIR / "agent_cert.pem"
KEY_FILE = WORKING_DIR / "agent_key.pem"

API_PARAMS = {
    "host": params.listen_address.compressed,
    "port": params.port,
    "log_level": LOG_LEVEL.lower(),
    "debug": params.debug,
    "ssl_keyfile": KEY_FILE,
    "ssl_certfile": CERT_FILE,
}

api = FastAPI()


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
        raise HTTPException(status_code=err_agent.status, detail=str(err_agent))


def start():
    """Start the web server with Uvicorn ASGI."""
    import uvicorn

    uvicorn.run(api, **API_PARAMS)


if __name__ == "__main__":
    start()
