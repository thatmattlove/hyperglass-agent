SUPPORTED_NOS = ("frr", "bird")

SUPPORTED_QUERY = ("bgp_route", "bgp_aspath", "bgp_community", "ping", "traceroute")

AGENT_QUERY = ("bgp_route", "bgp_aspath", "bgp_community")

OS_QUERY = ("ping", "traceroute")

AFI_DISPLAY_MAP = {
    "ipv4_default": "IPv4",
    "ipv6_default": "IPv6",
    "ipv4_vpn": "IPv4 - {vrf}",
    "ipv6_vpn": "IPv6 - {vrf}",
}
