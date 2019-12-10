def format_bird(bird_version, ip_version, cmd):
    """
    Prefixes the configured BIRD command with the appropriate BIRD CLI
    command.
    """
    # bird_version = get_bird_version()
    prefix_map = {1: {4: "birdc -r", 6: "birdc6 -r"}, 2: {4: "birdc -r", 6: "birdc -r"}}

    cmd_prefix = prefix_map[bird_version][ip_version]
    command = f'{cmd_prefix} "{cmd}"'

    return command


def format_frr(cmd):
    return f'vtysh -uc "{cmd}"'
