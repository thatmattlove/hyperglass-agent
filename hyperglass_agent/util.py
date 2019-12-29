"""Agent utility fuctions."""

# Third Party Imports
from loguru import logger as _loguru_logger

# Project Imports
from hyperglass_agent.constants import LOG_HANDLER
from hyperglass_agent.constants import LOG_LEVELS

_loguru_logger.remove()
_loguru_logger.configure(handlers=[LOG_HANDLER], levels=LOG_LEVELS)

log = _loguru_logger


def top_level_async(func):
    """Allow async functions to be executed syncronously.

    Arguments:
        func {function} -- Asyncronous function

    Returns:
        {function} -- Syncronous function
    """
    import asyncio
    from functools import update_wrapper

    func = asyncio.coroutine(func)

    def _wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return update_wrapper(_wrapper, func)
