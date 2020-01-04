"""Constant definitions used throughout the application."""

# Standard Library Imports
import sys
from pathlib import Path

SUPPORTED_NOS = ("frr", "bird")

DEFAULT_MODE = "frr"

CERT_PATH = Path(__file__).parent / "agent_cert.pem"
KEY_PATH = Path(__file__).parent / "agent_key.pem"

SUPPORTED_QUERY = ("bgp_route", "bgp_aspath", "bgp_community", "ping", "traceroute")

AGENT_QUERY = ("bgp_route", "bgp_aspath", "bgp_community")

OS_QUERY = ("ping", "traceroute")

AFI_DISPLAY_MAP = {
    "ipv4_default": "IPv4",
    "ipv6_default": "IPv6",
    "ipv4_vpn": "IPv4 - {vrf}",
    "ipv6_vpn": "IPv6 - {vrf}",
}

LOG_FMT = (
    "<lvl><b>[{level}]</b> {time:YYYYMMDD} <lw>|</lw> {time:HH:mm:ss} {name} "
    "<lw>|</lw> {function}</lvl> <lvl><b>→</b></lvl> {message}"
)
LOG_LEVELS = [
    {"name": "DEBUG", "no": 10, "color": "<c>"},
    {"name": "INFO", "no": 20, "color": "<le>"},
    {"name": "SUCCESS", "no": 25, "color": "<g>"},
    {"name": "WARNING", "no": 30, "color": "<y>"},
    {"name": "ERROR", "no": 40, "color": "<y>"},
    {"name": "CRITICAL", "no": 50, "color": "<r>"},
]

LOG_HANDLER = {"sink": sys.stdout, "format": LOG_FMT, "level": "INFO"}
