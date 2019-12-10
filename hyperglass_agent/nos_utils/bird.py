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
    version_str = re.findall(r"\d+", raw_output)

    # Filter major release number & convert to int
    version = int(version_str[0])

    log.debug(f"BIRD Major Version: {version_str[0]}")
    return version


async def parse_bird_output(raw):
    raw_split = re.split(r"(Table)", raw.strip())
    raw_joined = "".join(raw_split[1::])
    log.debug(f"Parsed output:\n{raw_joined}")
    return raw_joined
