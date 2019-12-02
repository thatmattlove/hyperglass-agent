import operator
from logzero import logger as log
from config import params
from config import commands
from exceptions import QueryError, ExecutionError
import asyncio


async def run_query(query):
    log.debug(f"Query: {query}")
    command_raw = operator.attrgetter(
        ".".join([params.mode, query.afi, query.query_type])
    )(commands)
    command = command_raw.format(**query.dict())
    proc = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return stdout.decode()
    if stderr:
        raise ExecutionError(stderr.decode())
