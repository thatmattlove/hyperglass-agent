"""Various formatting functions for supported platforms."""


def format_bird(ip_version, bird_version, cmd):
    """Prefixes BIRD command with the appropriate BIRD CLI command.

    Arguments:
        ip_version {int} -- IPv4/IPv6
        bird_version {int} -- BIRD version
        cmd {str} -- Unprefixed command

    Returns:
        {str} -- Prefixed command
    """
    cmd_prefix = "birdc"

    if bird_version == 1 and ip_version == 6:
        cmd_prefix = "birdc6"

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
