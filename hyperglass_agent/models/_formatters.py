import asyncio
import re
from hyperglass_agent.exceptions import ExecutionError
from logzero import logger as log


def top_level_async(func):
    from functools import update_wrapper

    func = asyncio.coroutine(func)

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return update_wrapper(wrapper, func)


@top_level_async
async def get_bird_version():
    """
    Get BIRD version from command line, convert version to float for
    comparision.
    """
    from math import fsum

    proc = await asyncio.create_subprocess_shell(
        "bird --version", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        raw_output = stdout.decode("utf-8")
    if stderr and "BIRD version" in stderr:
        raw_output = stderr.decode("utf-8")
    elif stderr and "BIRD version" not in stderr:
        raise ExecutionError(stderr.decode("utf-8"))

    log.debug(f"Raw output: {raw_output}")
    # Extract numbers from string as list of numbers
    version_str = ".".join(re.findall(r"\d+", raw_output))
    # Convert number strings to floats
    version_float = [float(n) for n in version_str]
    # Add floats to produce whole number as version number
    version_sum = fsum(version_float)
    if version_sum < 2:
        version = 1
    else:
        version = 2

    log.debug(f"BIRD Major Version: {str(version)}")
    return version


def format_bird(ip_version, cmd):
    """
    Prefixes the configured BIRD command with the appropriate BIRD CLI
    command.
    """
    # bird_version = get_bird_version()
    bird_version = 2
    prefix_map = {1: {4: "birdc -r", 6: "birdc6 -r"}, 2: {4: "birdc -r", 6: "birdc -r"}}

    cmd_prefix = prefix_map[bird_version][ip_version]
    command = f"{cmd_prefix} {cmd}"

    log.debug(f"Constructed command: {command}")
    return command


def format_frr(cmd):
    return f'vtysh -c "{cmd}"'
