from fastapi import FastAPI
import json
import uvicorn
from logzero import logger as log
from authlib.jose import JWS
from authlib.jose import JWS_ALGORITHMS

import stackprinter

from config import params
from models.request import Request
from execute import run_query
from exceptions import HyperglassAgentError, QueryError
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

stackprinter.set_excepthook()

LOG_LEVEL = "info"
if params.debug:
    LOG_LEVEL = "debug"

app = FastAPI()

jws = JWS(algorithms=JWS_ALGORITHMS)


async def decrypted_data(data):
    try:
        jws_decrypted = jws.deserialize_compact(data, params.secret.get_secret_value())
        log.debug(jws_decrypted)
        return json.loads(jws_decrypted["payload"])
    except Exception as e:
        log.error(e)
        raise QueryError(
            "Invalid Payload Error: {error}", error=e
        )  # TODO: Tighten this up


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.exception_handler(ValidationError)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.exception_handler(HyperglassAgentError)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.code, content={"error": exc.message})


@app.get("/query/{request}")
async def query_entrypoint(request):
    decrypted_query = await decrypted_data(request)
    log.debug(decrypted_query)
    validated_query = Request(**decrypted_query)
    query_output = await run_query(validated_query)
    return query_output


if __name__ == "__main__":
    uvicorn.run(
        "agent:app",
        host=params.listen_address.compressed,
        port=params.port,
        log_level=LOG_LEVEL,
        reload=params.debug,
    )
