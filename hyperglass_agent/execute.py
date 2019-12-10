# Standard Library Imports
import asyncio
import operator
from hyperglass_agent.exceptions import ExecutionError
from hyperglass_agent.nos_utils.bird import parse_bird_output

# Third Party Imports
from logzero import logger as log

# Project Imports
from hyperglass_agent.config import commands
from hyperglass_agent.config import params

PARSER_MAP = {"bird": parse_bird_output, "frr": None}

PARSER = PARSER_MAP[params.mode]


async def run_query(query):
    log.debug(f"Query: {query}")
    command_raw = operator.attrgetter(
        ".".join([params.mode, query.afi, query.query_type])
    )(commands)

    log.debug(f"Raw Command: {command_raw}")

    command = command_raw.format(**query.dict())

    log.debug(f"Formatted Command: {command}")

    proc = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    if stdout:
        raw_output = stdout.decode()
        if PARSER is not None:
            output = await PARSER(raw=raw_output, query_data=query)
        else:
            output = raw_output
        return output

    if stderr:
        raise ExecutionError(stderr.decode())
