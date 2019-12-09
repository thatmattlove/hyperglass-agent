# Standard Library Imports
import asyncio
import operator
from hyperglass_agent.exceptions import ExecutionError
from hyperglass_agent.exceptions import QueryError

# Third Party Imports
from logzero import logger as log

# Project Imports
from hyperglass_agent.config import commands
from hyperglass_agent.config import params


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
        return stdout.decode()
    if stderr:
        raise ExecutionError(stderr.decode())
