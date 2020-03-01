"""Agent utility fuctions."""

# Standard Library
import os

# Third Party
from loguru import logger as _loguru_logger

# Project
from hyperglass_agent.constants import APP_PATHS, LOG_LEVELS, LOG_HANDLER

_loguru_logger.remove()
_loguru_logger.configure(handlers=[LOG_HANDLER], levels=LOG_LEVELS)

log = _loguru_logger


def top_level_async(func):
    """Allow async functions to be executed synchronously.

    Arguments:
        func {function} -- Asynchronous function

    Returns:
        {function} -- Synchronous function
    """
    import asyncio
    from functools import update_wrapper

    func = asyncio.coroutine(func)

    def _wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return update_wrapper(_wrapper, func)


def find_app_path():
    """Verify the supported app paths exist, return the first found path.

    Raises:
        ConfigError: Raised if no path is found.

    Returns:
        {Path} -- Matched app path
    """
    app_path = None

    for path in APP_PATHS:
        if path.exists():
            app_path = path
            break
    if app_path is None:
        raise RuntimeError(
            "None of the supported paths for hyperglass-agent were found.\n"
            + "Checked:\n{one}\n{two}".format(one=APP_PATHS[0], two=APP_PATHS[1])
        )
    os.environ["hyperglass_agent_directory"] = str(app_path)
    return app_path


def set_app_path(required=False):
    """Find app directory and set value to environment variable."""
    import os
    from pathlib import Path
    from getpass import getuser

    matched_path = None

    config_paths = (Path.home() / "hyperglass-agent", Path("/etc/hyperglass-agent/"))

    for path in config_paths:
        try:
            if path.exists():
                tmp = path / "test.tmp"
                tmp.touch()
                if tmp.exists():
                    matched_path = path
                    tmp.unlink()
                    break
        except Exception:
            matched_path = None

    if required and matched_path is None:
        # Only raise an error if required is True
        raise RuntimeError(
            """
    No configuration directories were determined to both exist and be readable
    by hyperglass. hyperglass is running as user '{un}' (UID '{uid}'), and tried
    to access the following directories:
    {dir}""".format(
                un=getuser(),
                uid=os.getuid(),
                dir="\n".join([" - " + str(p) for p in config_paths]),
            )
        )

    if matched_path is not None:
        os.environ["hyperglass_agent_directory"] = str(matched_path)

    return True
