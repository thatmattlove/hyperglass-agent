"""hyperglass-agent CLI commands."""

# Standard Library
import sys
import platform
from pathlib import Path
from datetime import datetime, timedelta

# Third Party
from click import group, style, option, confirm, help_option

# Project
from hyperglass_agent.cli.echo import error, label, warning
from hyperglass_agent.cli.static import WARNING

# Define working directory
WORKING_DIR = Path(__file__).parent
MODULE_DIR = WORKING_DIR / "hyperglass_agent"

# Certificate parameters
CERT_START = datetime.utcnow()
CERT_END = datetime.utcnow() + timedelta(days=730)
CERT_FILE = MODULE_DIR / "agent_cert.pem"
KEY_FILE = MODULE_DIR / "agent_key.pem"

DEFAULT_CERT_CN = platform.node()
DEFAULT_CERT_O = "hyperglass"
DEFAULT_CERT_SIZE = 4096
DEFAULT_CERT_DURATION = 2
DEFAULT_CERT_SHOW = False

supports_color = "utf" in sys.getfilesystemencoding().lower()


def _print_version(ctx, param, value):
    from hyperglass_agent import __version__

    if not value or ctx.resilient_parsing:
        return
    label("hyperglass-agent version: {v}", v=__version__)
    ctx.exit()


@group(
    help="hyperglass agent CLI",
    context_settings={"help_option_names": ["-h", "--help"], "color": supports_color},
)
@option(
    "-v",
    "--version",
    is_flag=True,
    callback=_print_version,
    expose_value=False,
    is_eager=True,
    help="hyperglass version",
)
@help_option("-h", "--help", help="Show this help message")
def cli():
    """Click command group."""
    pass


@cli.command("secret", help="Generate Agent Secret")
@option("-l", "--length", default=32, help="Character Length")
def generate_secret(length):
    """Generate a secret for JWT encoding.

    Arguments:
        length {int} -- Secret character length
    """
    import secrets

    gen_secret = secrets.token_urlsafe(length)
    label("Secret: {s}", s=gen_secret)


@cli.command("cert", help="Generate SSL Certificate Key Pair")
@option(
    "-cn",
    "--name",
    required=False,
    type=str,
    default=DEFAULT_CERT_CN,
    help="Common Name",
)
@option(
    "-o",
    "--org",
    required=False,
    type=str,
    default=DEFAULT_CERT_O,
    help="Organization Name",
)
@option(
    "-s", "--size", required=False, type=int, default=DEFAULT_CERT_SIZE, help="Key Size"
)
@option(
    "-d", "--duration", required=False, type=int, default=2, help="Validity in Years"
)
@option("-v", "--view-key", "show", is_flag=True, help="Show Private Key in CLI Output")
@option("--get", is_flag=True, help="Get existing public key")
def gen_cert(name, org, duration, size, show, get):
    """Generate SSL certificate keypair.

    Arguments:
        name {str} -- Common Name
        org {str} -- Organization
        duration -- Validity in years
        size {int} -- Key Size
        show {bool} -- Show private key in CLI
    """
    from hyperglass_agent.cli.actions import write_cert, find_app_path

    if get:
        app_path = find_app_path()
        cert_path = app_path / "agent_cert.pem"
        if not cert_path.exists():
            warning("Certificate & key files have not been generated.")
            do_gen = confirm(style("Would you like to generate them now?", **WARNING))
            if not do_gen:
                error("Certificate & key files do not yet exist.")
            else:
                write_cert(name=name, org=org, duration=duration, size=size, show=show)
        else:
            with cert_path.open("r") as f:
                cert = f.read()

            label(f"Public Key:\n\n{cert}")
    else:
        write_cert(name=name, org=org, duration=duration, size=size, show=show)


@cli.command("start", help="Start the Web Server")
def start_server():
    """Start the hyperglass agent."""
    from hyperglass_agent.cli.actions import start_web_server

    start_web_server()


@cli.command("setup", help="Run the setup wizard")
@option("--config/--no-config", default=True, help="Don't regenerate config file")
@option("--certs/--no-certs", default=True, help="Don't regenerate certificates")
@option("--systemd/--no-systemd", default=True, help="Don't generate a systemd file")
@option(
    "--force", is_flag=True, default=False, help="Force regeneration of config file"
)
def run_setup(config, certs, force, systemd):
    """Run setup wizard.

    Checks/creates installation directory, generates and writes
    certificates & keys, copies example/default configuration file.
    """
    from hyperglass_agent.cli.actions import (
        find_app_path,
        migrate_config,
        write_cert,
        make_systemd,
    )

    find_app_path()

    if certs:
        write_cert(
            name=DEFAULT_CERT_CN,
            org=DEFAULT_CERT_O,
            duration=DEFAULT_CERT_DURATION,
            size=DEFAULT_CERT_SIZE,
            show=DEFAULT_CERT_SHOW,
        )

    if config:
        migrate_config(force)

    if systemd:
        make_systemd()
