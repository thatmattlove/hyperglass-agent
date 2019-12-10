import asyncio
import re
from hyperglass_agent.util import top_level_async
from hyperglass_agent.exceptions import ExecutionError
from logzero import logger as log


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
    if stderr and b"BIRD version" in stderr:
        raw_output = stderr.decode("utf-8")
    elif stderr and b"BIRD version" not in stderr:
        raise ExecutionError(stderr.decode("utf-8"))

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
