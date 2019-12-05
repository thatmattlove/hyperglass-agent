# Standard Library Imports
import json

# Third Party Imports
import responder
from authlib.jose import JWS
from authlib.jose import JWS_ALGORITHMS
from logzero import logger as log
from pydantic import ValidationError

# Project Imports
import stackprinter
from hyperglass_agent.config import params
from hyperglass_agent.exceptions import HyperglassAgentError
from hyperglass_agent.exceptions import QueryError
from hyperglass_agent.execute import run_query
from hyperglass_agent.models.request import Request

stackprinter.set_excepthook()

LOG_LEVEL = "info"
if params.debug:
    LOG_LEVEL = "debug"

api = responder.API()

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


@api.route("/query/{params}")
async def query_entrypoint(req, resp, params):
    try:
        decrypted_query = await decrypted_data(params)
        log.debug(decrypted_query)
        validated_query = Request(**decrypted_query)
        query_output = await run_query(validated_query)
        resp.media = query_output
    except ValidationError as err_validation:
        resp.status_code = 400
        resp.media = {"error": str(err_validation)}
    except HyperglassAgentError as err_agent:
        resp.status_code = err_agent.code
        resp.media = {"error": str(err_agent)}


if __name__ == "__main__":
    api.run(
        address=params.listen_address.compressed,
        port=params.port,
        log_level=LOG_LEVEL,
        debug=params.debug,
    )
