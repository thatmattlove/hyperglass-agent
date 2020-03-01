"""Construct, execute, parse, and return the requested query."""

# Standard Library
import asyncio
import operator

# Project
from hyperglass_agent.util import log
from hyperglass_agent.config import params, commands
from hyperglass_agent.exceptions import ExecutionError
from hyperglass_agent.nos_utils.frr import parse_frr_output
from hyperglass_agent.nos_utils.bird import parse_bird_output


async def run_query(query):
    """Execute validated query & parse the results.

    Arguments:
        query {object} -- Validated query object

    Raises:
        ExecutionError: If stderr exists

    Returns:
        {str} -- Parsed output string
    """
    log.debug(f"Query: {query}")

    parser_map = {"bird": parse_bird_output, "frr": parse_frr_output}
    parser = parser_map[params.mode]

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

    if stderr:
        err_output = stderr.decode()
        log.error(err_output)
        raise ExecutionError(err_output)

    output = ""

    if stdout:
        log.debug(f"Parser: {parser.__name__}")

        raw_output = stdout.decode()
        output += await parser(
            raw=raw_output, query_data=query, not_found=params.not_found_message
        )
        return output

    if not output and proc.returncode == 0:
        output = await parser(
            raw="", query_data=query, not_found=params.not_found_message
        )
    return output
