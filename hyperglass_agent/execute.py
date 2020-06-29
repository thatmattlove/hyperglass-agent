"""Construct, execute, parse, and return the requested query."""

# Standard Library
import asyncio
import operator

# Project
from hyperglass_agent.log import log
from hyperglass_agent.config import params, commands
from hyperglass_agent.exceptions import ResponseEmpty, ExecutionError
from hyperglass_agent.nos_utils.frr import parse_frr_output
from hyperglass_agent.nos_utils.bird import (
    parse_bird_output,
    format_bird_bgp_aspath,
    format_bird_bgp_community,
)

target_format_map = {
    "bird": {
        "bgp_community": format_bird_bgp_community,
        "bgp_aspath": format_bird_bgp_aspath,
    },
    "frr": {},
}
parser_map = {"bird": parse_bird_output, "frr": parse_frr_output}


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

    parser = parser_map[params.mode]

    target_formatter = target_format_map[params.mode].get(query.query_type)

    if target_formatter is not None:
        query.target = target_formatter(query.target)

    command_raw = operator.attrgetter(
        ".".join([params.mode, query.afi, query.query_type])
    )(commands)

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
        raise ResponseEmpty("Command ran successfully, but the response was empty.")

    return output
