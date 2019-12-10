# Project Imports
from pydantic import validator
from hyperglass_agent.constants import AGENT_QUERY
from hyperglass_agent.models._utils import HyperglassModel
from hyperglass_agent.models._formatters import format_bird, format_frr
from hyperglass_agent.nos_utils.bird import BIRD_VERSION


class Command(HyperglassModel):
    """Class model for non-default commands"""

    class IPv4(HyperglassModel):
        """Class model for non-default dual afi commands"""

        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    class IPv6(HyperglassModel):
        """Class model for non-default ipv4 commands"""

        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    class VPNIPv4(HyperglassModel):
        """Class model for non-default ipv6 commands"""

        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    class VPNIPv6(HyperglassModel):
        """Class model for non-default ipv6 commands"""

        bgp_route: str = ""
        bgp_aspath: str = ""
        bgp_community: str = ""
        ping: str = ""
        traceroute: str = ""

    ipv4_default: IPv4 = IPv4()
    ipv6_default: IPv6 = IPv6()
    ipv4_vpn: VPNIPv4 = VPNIPv4()
    ipv6_vpn: VPNIPv6 = VPNIPv6()


class Commands(HyperglassModel):
    """Base class for commands class"""

    @classmethod
    def import_params(cls, input_params):
        """
        Imports passed dict from YAML config, dynamically sets
        attributes for the commands class.
        """
        obj = Commands()
        for (nos, cmds) in input_params.items():
            setattr(Commands, nos, Command(**cmds))
        return obj

    class FRR(Command):
        """Class model for default cisco_ios commands"""

        class VPNIPv4(Command.VPNIPv4):
            """Default commands for dual afi commands"""

            bgp_community: str = "show bgp vrf {vrf} ipv4 unicast community {target}"
            bgp_aspath: str = "show bgp vrf {vrf} ipv4 unicast regexp {target}"
            bgp_route: str = "show bgp vrf {vrf} ipv4 unicast {target}"
            ping: str = "ping -4 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -4 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_frr(cls, value):
                if "vtysh" not in value:
                    value = format_frr(value)
                return value

        class VPNIPv6(Command.VPNIPv6):
            """Default commands for dual afi commands"""

            bgp_community: str = "show bgp vrf {vrf} ipv6 unicast community {target}"
            bgp_aspath: str = "show bgp vrf {vrf} ipv6 unicast regexp {target}"
            bgp_route: str = "show bgp vrf {vrf} ipv6 unicast {target}"
            ping: str = "ping -6 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -6 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_frr(cls, value):
                if "vtysh" not in value:
                    value = format_frr(value)
                return value

        class IPv4(Command.IPv4):
            """Default commands for ipv4 commands"""

            bgp_community: str = "show bgp ipv4 unicast community {target}"
            bgp_aspath: str = "show bgp ipv4 unicast regexp {target}"
            bgp_route: str = "show bgp ipv4 unicast {target}"
            ping: str = "ping -4 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -4 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_frr(cls, value):
                if "vtysh" not in value:
                    value = format_frr(value)
                return value

        class IPv6(Command.IPv6):
            """Default commands for ipv6 commands"""

            bgp_community: str = "show bgp ipv6 unicast community {target}"
            bgp_aspath: str = "show bgp ipv6 unicast regexp {target}"
            bgp_route: str = "show bgp ipv6 unicast {target}"
            ping: str = "ping -6 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -6 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_frr(cls, value):
                if "vtysh" not in value:
                    value = format_frr(value)
                return value

        ipv4_default: IPv4 = IPv4()
        ipv6_default: IPv6 = IPv6()
        ipv4_vpn: VPNIPv4 = VPNIPv4()
        ipv6_vpn: VPNIPv6 = VPNIPv6()

    class BIRD(Command):
        """Class model for default cisco_ios commands"""

        class VPNIPv4(Command.VPNIPv4):
            """Default commands for dual afi commands"""

            bgp_community: str = "show route all where {target} ~ bgp_community"
            bgp_aspath: str = "show route all where bgp_path ~ {target}"
            bgp_route: str = "show route all where {target} ~ net"
            ping: str = "ping -4 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -4 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_bird(cls, value):
                if "birdc" not in value:
                    value = format_bird(BIRD_VERSION, 4, value)
                return value

        class VPNIPv6(Command.VPNIPv6):
            """Default commands for dual afi commands"""

            bgp_community: str = "show route all where {target} ~ bgp_community"
            bgp_aspath: str = "show route all where bgp_path ~ {target}"
            bgp_route: str = "show route all where {target} ~ net"
            ping: str = "ping -6 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -6 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_bird(cls, value):
                if "birdc" not in value:
                    value = format_bird(BIRD_VERSION, 6, value)
                return value

        class IPv4(Command.IPv4):
            """Default commands for ipv4 commands"""

            bgp_community: str = "show route all where {target} ~ bgp_community"
            bgp_aspath: str = "show route all where bgp_path ~ {target}"
            bgp_route: str = "show route all where {target} ~ net"
            ping: str = "ping -4 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -4 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_bird(cls, value):
                if "birdc" not in value:
                    value = format_bird(BIRD_VERSION, 4, value)
                return value

        class IPv6(Command.IPv6):
            """Default commands for ipv6 commands"""

            bgp_community: str = "show route all where {target} ~ bgp_community"
            bgp_aspath: str = "show route all where bgp_path ~ {target}"
            bgp_route: str = "show route all where {target} ~ net"
            ping: str = "ping -6 -c 5 -I {source} {target}"
            traceroute: str = "traceroute -6 -w 1 -q 1 -s {source} {target}"

            @validator(*AGENT_QUERY, allow_reuse=True)
            def prefix_bird(cls, value):
                if "birdc" not in value:
                    value = format_bird(BIRD_VERSION, 6, value)
                return value

        ipv4_default: IPv4 = IPv4()
        ipv6_default: IPv6 = IPv6()
        ipv4_vpn: VPNIPv4 = VPNIPv4()
        ipv6_vpn: VPNIPv6 = VPNIPv6()

    bird: BIRD = BIRD()
    frr: FRR = FRR()
