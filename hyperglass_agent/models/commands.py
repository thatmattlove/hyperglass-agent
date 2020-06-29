"""Command definitions for supported platforms."""

# Third Party
from pydantic import conint, root_validator

# Project
from hyperglass_agent.constants import AGENT_QUERY
from hyperglass_agent.models._utils import HyperglassModel
from hyperglass_agent.nos_utils.bird import get_bird_version
from hyperglass_agent.models._formatters import format_frr, format_bird


class Command(HyperglassModel):
    """Class model for non-default dual afi commands."""

    bgp_route: str = ""
    bgp_aspath: str = ""
    bgp_community: str = ""
    ping: str = ""
    traceroute: str = ""


class FRRCommand(Command):
    """Class model for FRRouting commands."""

    @root_validator
    def prefix_frr(cls, values):
        """Prefix command if needed.

        Returns:
            {str} -- Prefixed command
        """
        for cmd in AGENT_QUERY:
            if "vtysh" not in values[cmd]:
                values[cmd] = format_frr(values[cmd])
        return values


class FRR(HyperglassModel):
    """Class model for default FRRouting commands."""

    class VPNIPv4(FRRCommand):
        """Default commands for dual afi commands."""

        bgp_community: str = "show bgp vrf {vrf} ipv4 unicast community {target}"
        bgp_aspath: str = "show bgp vrf {vrf} ipv4 unicast regexp {target}"
        bgp_route: str = "show bgp vrf {vrf} ipv4 unicast {target}"
        ping: str = "ping -4 -c 5 -I {source} {target}"
        traceroute: str = "traceroute -4 -w 1 -q 1 -s {source} {target}"

    class VPNIPv6(FRRCommand):
        """Default commands for dual afi commands."""

        bgp_community: str = "show bgp vrf {vrf} ipv6 unicast community {target}"
        bgp_aspath: str = "show bgp vrf {vrf} ipv6 unicast regexp {target}"
        bgp_route: str = "show bgp vrf {vrf} ipv6 unicast {target}"
        ping: str = "ping -6 -c 5 -I {source} {target}"
        traceroute: str = "traceroute -6 -w 1 -q 1 -s {source} {target}"

    class IPv4(FRRCommand):
        """Default commands for ipv4 commands."""

        bgp_community: str = "show bgp ipv4 unicast community {target}"
        bgp_aspath: str = "show bgp ipv4 unicast regexp {target}"
        bgp_route: str = "show bgp ipv4 unicast {target}"
        ping: str = "ping -4 -c 5 -I {source} {target}"
        traceroute: str = "traceroute -4 -w 1 -q 1 -s {source} {target}"

    class IPv6(FRRCommand):
        """Default commands for ipv6 commands."""

        bgp_community: str = "show bgp ipv6 unicast community {target}"
        bgp_aspath: str = "show bgp ipv6 unicast regexp {target}"
        bgp_route: str = "show bgp ipv6 unicast {target}"
        ping: str = "ping -6 -c 5 -I {source} {target}"
        traceroute: str = "traceroute -6 -w 1 -q 1 -s {source} {target}"

    ipv4_default: IPv4 = IPv4()
    ipv6_default: IPv6 = IPv6()
    ipv4_vpn: VPNIPv4 = VPNIPv4()
    ipv6_vpn: VPNIPv6 = VPNIPv6()


class BIRDCommand(Command):
    """Class model for BIRD commands."""

    bird_version: int
    ip_version: int

    @root_validator
    def prefix_bird(cls, values):
        """Prefix command if needed.

        Returns:
            {str} -- Prefixed command
        """
        for cmd in AGENT_QUERY:
            if "birdc" not in values[cmd]:
                values[cmd] = format_bird(
                    values["ip_version"], values["bird_version"], values[cmd],
                )
        return values


class BIRD(HyperglassModel):
    """Class model for default BIRD commands."""

    class VPNIPv4(BIRDCommand):
        """Default dual AFI commands."""

        bgp_community: str = "show route all where {target} ~ bgp_community"
        bgp_aspath: str = "show route all where bgp_path ~ {target}"
        bgp_route: str = "show route all where {target} ~ net"
        ping: str = "ping -4 -c 5 -I {source} {target}"
        traceroute: str = "traceroute -4 -w 1 -q 1 -s {source} {target}"

    class VPNIPv6(BIRDCommand):
        """Default dual AFI commands."""

        bgp_community: str = "show route all where {target} ~ bgp_community"
        bgp_aspath: str = "show route all where bgp_path ~ {target}"
        bgp_route: str = "show route all where {target} ~ net"
        ping: str = "ping -6 -c 5 -I {source} {target}"
        traceroute: str = "traceroute -6 -w 1 -q 1 -s {source} {target}"

    class IPv4(BIRDCommand):
        """Default IPv4 commands."""

        bgp_community: str = "show route all where {target} ~ bgp_community"
        bgp_aspath: str = "show route all where bgp_path ~ {target}"
        bgp_route: str = "show route all where {target} ~ net"
        ping: str = "ping -4 -c 5 -I {source} {target}"
        traceroute: str = "traceroute -4 -w 1 -q 1 -s {source} {target}"

    class IPv6(BIRDCommand):
        """Default IPv6 commands."""

        bgp_community: str = "show route all where {target} ~ bgp_community"
        bgp_aspath: str = "show route all where bgp_path ~ {target}"
        bgp_route: str = "show route all where {target} ~ net"
        ping: str = "ping -6 -c 5 -I {source} {target}"
        traceroute: str = "traceroute -6 -w 1 -q 1 -s {source} {target}"

    bird_version: conint(ge=1, le=2) = 2
    ipv4_default: IPv4 = IPv4(ip_version=4, bird_version=bird_version)
    ipv6_default: IPv6 = IPv6(ip_version=6, bird_version=bird_version)
    ipv4_vpn: VPNIPv4 = VPNIPv4(ip_version=4, bird_version=bird_version)
    ipv6_vpn: VPNIPv6 = VPNIPv6(ip_version=6, bird_version=bird_version)


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
        cmd_kwargs = {}
        if mode == "bird":
            bird_version = get_bird_version()
            cmd_kwargs.update({"bird_version": bird_version})

        obj = Commands()

        if input_params is not None:
            for (nos, cmds) in input_params.items():
                setattr(Commands, nos, Command(**cmd_kwargs, **cmds))
        return obj

    bird: BIRD = BIRD()
    frr: FRR = FRR()
