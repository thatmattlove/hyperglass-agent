"""Various formatting functions for supported platforms."""

# Project
from hyperglass_agent.nos_utils.bird import get_bird_version


def format_bird(ip_version, cmd, mode):
    """Prefixes BIRD command with the appropriate BIRD CLI command.

    Arguments:
        ip_version {int} -- IPv4/IPv6
        cmd {str} -- Unprefixed command
        mode {str} -- Agent mode

    Returns:
        {str} -- Prefixed command
    """
    if mode == "bird":
        bird_version = get_bird_version()
    else:
        bird_version = 2
    prefix_map = {1: {4: "birdc -r", 6: "birdc6 -r"}, 2: {4: "birdc -r", 6: "birdc -r"}}

    cmd_prefix = prefix_map[bird_version][ip_version]
    command = f'{cmd_prefix} "{cmd}"'

    return command


def format_frr(cmd):
    """Prefixes FRR command with the appropriate vtysh prefix.

    Arguments:
        cmd {str} -- Unprefixed command

    Returns:
        {str} -- Prefixed command
    """
    return f'vtysh -uc "{cmd}"'
