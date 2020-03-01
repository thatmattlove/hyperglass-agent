"""Various BIRD Internet Routing Daemon (BIRD) utilities."""

# Standard Library
import re
import asyncio

# Project
from hyperglass_agent.util import log, top_level_async
from hyperglass_agent.constants import AFI_DISPLAY_MAP
from hyperglass_agent.exceptions import ExecutionError


@top_level_async
async def get_bird_version():
    """Get BIRD version from command line.

    Raises:
        ExecutionError: Raised when `birdc` is not found on the system.
        ExecutionError: Raised when the output is unreadable or contains errors.

    Returns:
        {int} -- Major BIRD version.
    """
    proc = await asyncio.create_subprocess_shell(
        cmd="bird --version",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if stdout:
        raw_output = stdout.decode("utf-8")

    if stderr and b"BIRD version" in stderr:
        raw_output = stderr.decode("utf-8")

    elif stderr and b"command not found" in stderr:
        raise ExecutionError(
            (
                "BIRD mode is configured, but bird does not appear to be "
                f'installed: {stderr.decode("utf-8")}'
            )
        )

    elif stderr and b"BIRD version" not in stderr:
        raise ExecutionError(stderr.decode("utf-8"))

    # Extract numbers from string as list of numbers
    version_str = re.findall(r"\d+", raw_output)

    # Filter major release number & convert to int
    version = int(version_str[0])

    log.debug(f"BIRD Major Version: {version_str[0]}")
    return version


async def parse_bird_output(raw, query_data, not_found):
    """Parse raw BIRD output and return parsed output.

    Arguments:
        raw {str} -- Raw BIRD output
        query_data {object} -- Validated query object
        not_found {str} -- Lookup not found message template

    Returns:
        str -- Parsed output
    """
    raw_split = re.split(r"(Table)", raw.strip())
    raw_joined = "".join(raw_split[1::])

    if not raw_joined:
        notfound_message = not_found.format(
            target=query_data.target, afi=AFI_DISPLAY_MAP[query_data.afi]
        )
        output = notfound_message
    else:
        output = raw_joined

    log.debug(f"Parsed output:\n{output}")
    return output
