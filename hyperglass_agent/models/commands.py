"""Command definitions for supported platforms."""

# Third Party
from pydantic import validator

# Project
from hyperglass_agent.constants import AGENT_QUERY, DEFAULT_MODE
from hyperglass_agent.models._utils import HyperglassModel
from hyperglass_agent.models._formatters import format_frr, format_bird


class Command(HyperglassModel):
    """Class model for non-default commands."""

    class IPv4(HyperglassModel):
        """Class model for non-default dual afi commands."""

        mode: str = DEFAULT_MODE
        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    class IPv6(HyperglassModel):
        """Class model for non-default ipv4 commands."""

        mode: str = DEFAULT_MODE
        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    class VPNIPv4(HyperglassModel):
        """Class model for non-default ipv6 commands."""

        mode: str = DEFAULT_MODE
        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    class VPNIPv6(HyperglassModel):
        """Class model for non-default ipv6 commands."""

        mode: str = DEFAULT_MODE
        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    mode: str = DEFAULT_MODE
    ipv4_default: IPv4 = IPv4(mode=mode)
    ipv6_default: IPv6 = IPv6(mode=mode)
    ipv4_vpn: VPNIPv4 = VPNIPv4(mode=mode)
    ipv6_vpn: VPNIPv6 = VPNIPv6(mode=mode)


class Commands(HyperglassModel):
    """Base class for all commands."""

    @classmethod
    def import_params(cls, mode, input_params=None):
        """Import YAML config, dynamically set attributes for each NOS class.

        Arguments:
            mode {str} -- Agent mode

        Keyword Arguments:
            input_params {dict} -- Overidden commands (default: {None})

        Returns:
            {object} -- Validated command object
        """
        obj = Commands(mode=mode)
        if input_params is not None:
            for (nos, cmds) in input_params.items():
                setattr(Commands, nos, Command(mode=mode, **cmds))
        return obj

    class FRR(Command):
        """Class model for default cisco_ios commands."""

        class VPNIPv4(Command.VPNIPv4):
            """Default commands for dual afi commands."""

            bgp_community: str = "show bgp vrf {vrf} ipv4 unicast community {target}"
            bgp_aspath: str = "show bgp vrf {vrf} ipv4 unicast regexp {target}"
            bgp_route: str = "show bgp vrf {vrf} ipv4 unicast {target}"
            ping: str = "ping -4 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -4 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_frr(cls, value):  # noqa: N805
                """Prefix command if needed.

                Returns:
                    {str} -- Prefixed command
                """
                if "vtysh" not in value:
                    value = format_frr(value)
                return value

        class VPNIPv6(Command.VPNIPv6):
            """Default commands for dual afi commands."""

            bgp_community: str = "show bgp vrf {vrf} ipv6 unicast community {target}"
            bgp_aspath: str = "show bgp vrf {vrf} ipv6 unicast regexp {target}"
            bgp_route: str = "show bgp vrf {vrf} ipv6 unicast {target}"
            ping: str = "ping -6 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -6 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_frr(cls, value):  # noqa: N805
                """Prefix command if needed.

                Returns:
                    {str} -- Prefixed command
                """
                if "vtysh" not in value:
                    value = format_frr(value)
                return value

        class IPv4(Command.IPv4):
            """Default commands for ipv4 commands."""

            bgp_community: str = "show bgp ipv4 unicast community {target}"
            bgp_aspath: str = "show bgp ipv4 unicast regexp {target}"
            bgp_route: str = "show bgp ipv4 unicast {target}"
            ping: str = "ping -4 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -4 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_frr(cls, value):  # noqa: N805
                """Prefix command if needed.

                Returns:
                    {str} -- Prefixed command
                """
                if "vtysh" not in value:
                    value = format_frr(value)
                return value

        class IPv6(Command.IPv6):
            """Default commands for ipv6 commands."""

            bgp_community: str = "show bgp ipv6 unicast community {target}"
            bgp_aspath: str = "show bgp ipv6 unicast regexp {target}"
            bgp_route: str = "show bgp ipv6 unicast {target}"
            ping: str = "ping -6 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -6 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_frr(cls, value):  # noqa: N805
                """Prefix command if needed.

                Returns:
                    {str} -- Prefixed command
                """
                if "vtysh" not in value:
                    value = format_frr(value)
                return value

        mode: str = DEFAULT_MODE
        ipv4_default: IPv4 = IPv4(mode=mode)
        ipv6_default: IPv6 = IPv6(mode=mode)
        ipv4_vpn: VPNIPv4 = VPNIPv4(mode=mode)
        ipv6_vpn: VPNIPv6 = VPNIPv6(mode=mode)

    class BIRD(Command):
        """Class model for default cisco_ios commands."""

        class VPNIPv4(Command.VPNIPv4):
            """Default dual AFI commands."""

            mode: str
            bgp_community: str = "show route all where {target} ~ bgp_community"
            bgp_aspath: str = "show route all where bgp_path ~ {target}"
            bgp_route: str = "show route all where {target} ~ net"
            ping: str = "ping -4 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -4 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_bird(cls, value, values):  # noqa: N805
                """Prefix command if needed.

                Returns:
                    {str} -- Prefixed command
                """
                if "birdc" not in value:
                    value = format_bird(4, value, values["mode"])
                return value

        class VPNIPv6(Command.VPNIPv6):
            """Default dual AFI commands."""

            mode: str
            bgp_community: str = "show route all where {target} ~ bgp_community"
            bgp_aspath: str = "show route all where bgp_path ~ {target}"
            bgp_route: str = "show route all where {target} ~ net"
            ping: str = "ping -6 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -6 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_bird(cls, value, values):  # noqa: N805
                """Prefix command if needed.

                Returns:
                    {str} -- Prefixed command
                """
                if "birdc" not in value:
                    value = format_bird(6, value, values["mode"])
                return value

        class IPv4(Command.IPv4):
            """Default IPv4 commands."""

            mode: str
            bgp_community: str = "show route all where {target} ~ bgp_community"
            bgp_aspath: str = "show route all where bgp_path ~ {target}"
            bgp_route: str = "show route all where {target} ~ net"
            ping: str = "ping -4 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -4 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_bird(cls, value, values):  # noqa: N805
                """Prefix command if needed.

                Returns:
                    {str} -- Prefixed command
                """
                if "birdc" not in value:
                    value = format_bird(4, value, values["mode"])
                return value

        class IPv6(Command.IPv6):
            """Default IPv6 commands."""

            mode: str
            bgp_community: str = "show route all where {target} ~ bgp_community"
            bgp_aspath: str = "show route all where bgp_path ~ {target}"
            bgp_route: str = "show route all where {target} ~ net"
            ping: str = "ping -6 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -6 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_bird(cls, value, values):  # noqa: N805
                """Prefix command if needed.

                Returns:
                    {str} -- Prefixed command
                """
                if "birdc" not in value:
                    value = format_bird(6, value, values["mode"])
                return value

        mode: str = DEFAULT_MODE
        ipv4_default: IPv4 = IPv4(mode=mode)
        ipv6_default: IPv6 = IPv6(mode=mode)
        ipv4_vpn: VPNIPv4 = VPNIPv4(mode=mode)
        ipv6_vpn: VPNIPv6 = VPNIPv6(mode=mode)

    mode: str = DEFAULT_MODE
    bird: BIRD = BIRD(mode=mode)
    frr: FRR = FRR(mode=mode)
