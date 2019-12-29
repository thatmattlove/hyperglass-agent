"""Web server frontend, passes raw query to backend validation & execution."""

# Standard Library Imports
import json
from pathlib import Path

# Third Party Imports
import responder
from pydantic import ValidationError

# Project Imports
from hyperglass_agent.config import LOG_LEVEL
from hyperglass_agent.config import params
from hyperglass_agent.exceptions import HyperglassAgentError
from hyperglass_agent.execute import run_query
from hyperglass_agent.models.request import Request
from hyperglass_agent.payload import jwt_decode
from hyperglass_agent.payload import jwt_encode
from hyperglass_agent.util import log

WORKING_DIR = Path(__file__).parent

CERT_FILE = WORKING_DIR / "agent_cert.pem"
KEY_FILE = WORKING_DIR / "agent_key.pem"

api = responder.API()


@api.route("/query")
async def query_entrypoint(req, resp):
    """Validate input request, decode, execute, and returns response."""
    try:
        query = await req.media()
        log.debug(f"Raw Query JSON: {query}")

        query_str = query["encoded"]
        decrypted_query = await jwt_decode(query_str)
        decrypted_query = json.loads(decrypted_query)

        log.debug(decrypted_query)

        validated_query = Request(**decrypted_query)
        query_output = await run_query(validated_query)

        log.debug(f"Query Output:\n{query_output}")

        encoded = await jwt_encode(query_output)
        resp.media = {"encoded": encoded}

    except ValidationError as err_validation:
        log.error(str(err_validation))
        resp.status_code = 400
        resp.media = {"error": str(err_validation)}

    except HyperglassAgentError as err_agent:
        log.error(str(err_agent))
        resp.status_code = err_agent.code
        resp.media = {"error": str(err_agent)}


if __name__ == "__main__":
    log.debug("Debugging Enabled")
    api.run(
        address=params.listen_address.compressed,
        port=params.port,
        log_level=LOG_LEVEL.lower(),
        debug=params.debug,
        ssl_keyfile=KEY_FILE,
        ssl_certfile=CERT_FILE,
    )
