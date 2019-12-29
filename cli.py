#!/usr/bin/env python3
"""CLI for hyperglass-agent."""

# Standard Library Imports
import asyncio
import datetime
import json
import platform
import shutil
from functools import update_wrapper
from pathlib import Path

# Third Party Imports
import click
import httpx
import jwt
import stackprinter

stackprinter.set_excepthook(style="darkbg2")

# Click Helpers
NL = "\n"

TEST_QUERY_DATA = {
    "query_type": "bgp_route",
    "vrf": "default",
    "afi": "ipv4_default",
    "source": "192.0.2.1",
    "target": "1.1.1.1",
}
TEST_SECRET = "TestSecret12345"  # noqa: S105

# Initialize shutil copy function
cp = shutil.copyfile

# Define working directory
WORKING_DIR = Path(__file__).parent
MODULE_DIR = WORKING_DIR / "hyperglass_agent"

# Certificate parameters
CERT_START = datetime.datetime.utcnow()
CERT_END = datetime.datetime.utcnow() + datetime.timedelta(days=730)
CERT_FILE = MODULE_DIR / "agent_cert.pem"
KEY_FILE = MODULE_DIR / "agent_key.pem"


def async_command(func):
    """Allow async functions to be executed syncronously.

    Arguments:
        func {function} -- Asyncronous function

    Returns:
        {function} -- Syncronous function
    """
    func = asyncio.coroutine(func)

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return update_wrapper(wrapper, func)


@click.group()
def cli():
    """Click command group."""
    pass


async def decode(payload, secret):
    """Decode JWT payloads."""
    try:
        decoded = jwt.decode(payload, secret, algorithm="HS256")
        decoded = decoded["payload"]
        return decoded
    except (KeyError, jwt.ExpiredSignature, jwt.ExpiredSignatureError) as exp:
        raise click.ClickException(click.style(str(exp)), fg="red") from None


async def encode(response, secret):
    """Encode JWT responses."""
    payload = {
        "payload": response,
        "nbf": datetime.datetime.utcnow(),
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=60),
    }
    encoded = jwt.encode(payload, secret, algorithm="HS256")
    return encoded


@cli.command(help="Test a running hyperglass-agent instance")
@click.option(
    "-h",
    "--host",
    type=str,
    default="localhost",
    help="Hostname/IP of hyperglass_agent to test",
)
@click.option(
    "-p", "--port", type=int, default=8080, help="TCP Port of hyperglass_agent to test"
)
@click.option("-s", "--secret", type=str, default=TEST_SECRET, help="Secret key")
@click.option(
    "-q",
    "--query-data",
    "query_data",
    type=dict,
    default=TEST_QUERY_DATA,
    help="Query data to test",
)
@click.option("--ssl", is_flag=True, default=False, help="Use HTTPS")
@async_command
async def test_agent(host, port, secret, query_data, ssl):
    """Test a running hyperglass-agent instance.

    Arguments:
        host {str} -- IP address or hostname
        port {int} -- Port
        secret {str} -- JWT encoding secret
        query_data {dict} -- Query data
        ssl {bool} -- Use HTTPS
    """
    encoded = await encode(query_data, secret)
    if ssl:
        protocol = "https"
    else:
        protocol = "http"
    raw_response = await httpx.post(
        f"{protocol}://{host}:{port}/query",
        data={"encoded": encoded.decode("utf-8")},
        verify=CERT_FILE,
    )
    if raw_response.status_code != 200:
        click.secho(f"{raw_response.status_code}: {raw_response.text}", fg="red")
    else:
        decoded_response = await decode(raw_response.content.decode("utf-8"))
        click.secho(json.dumps(decoded_response, indent=4), fg="green")


@cli.command("cert", help="Generate SSL Certificate Key Pair")
@click.option("--cn", required=False, default=platform.node(), help="Common Name")
@click.option("--o", required=False, default="hyperglass", help="Organization Name")
@click.option(
    "--end", required=False, default=CERT_END, help="Certificate Validity End"
)
@click.option(
    "--start", required=False, default=CERT_START, help="Certificate Validity Start"
)
@click.option("--show", is_flag=True, help="Show Private Key in CLI Output")
def gen_cert(cn, o, start, end, show):
    """Generate SSL certificate keypair.

    Arguments:
        cn {str} -- Common Name
        o {str} -- Organization
        start {str} -- Start Time
        end {str} -- End Time
        show {bool} -- Show private key in CLI
    """
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes

    key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, cn),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, o),
        ]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(start)
        .not_valid_after(end)
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(cn)]), critical=False)
        .sign(key, hashes.SHA256(), default_backend())
    )
    cert = cert.public_bytes(serialization.Encoding.PEM)
    key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    if show:
        click.echo(
            NL
            + "Your public key is:"
            + NL
            + click.style(cert.decode("utf8"), fg="blue")
        )
        click.echo(
            NL
            + "Your private key is:"
            + NL
            + click.style(key.decode("utf-8"), fg="red")
        )
    with CERT_FILE.open("wb") as cf:
        cf.write(cert)
    click.echo(
        "Wrote public key to file: "
        + click.style(str(CERT_FILE.absolute()), fg="green", bold=True)
    )
    with KEY_FILE.open("wb") as kf:
        kf.write(key)
    click.echo(
        "Wrote private key to file: "
        + click.style(str(KEY_FILE.absolute()), fg="green", bold=True)
    )


@cli.command("dev-server", help="Start development web server")
@click.option(
    "-h", "--host", type=str, default="0.0.0.0", help="Listening IP"  # noqa: S104
)
@click.option("-p", "--port", type=int, default=8080, help="TCP Port")
def dev_server(host, port):
    """Start the development web server.

    Arguments:
        host {str} -- Listening IP address
        port {int} -- TCP port

    Raises:
        click.ClickException: Any raised exception message
    """
    try:
        from hyperglass_agent.agent import api

        api.run(address=host, port=port, debug=True, log_level="debug")
    except Exception as e:
        raise click.ClickException(click.style(str(e), fg="red", bold=True))


@cli.command("line-count", help="Get line count for source code.")
@click.option(
    "-d",
    "--directory",
    type=str,
    default="hyperglass_agent",
    help="Source code directory",
)
def line_count(directory):
    """Get lines of code.

    Arguments:
        directory {str} -- Source code directory
    """
    from develop import count_lines

    count = count_lines(directory)
    click.echo(
        NL
        + click.style("Line Count: ", fg="blue")
        + click.style(str(count), fg="green", bold=True)
        + NL
    )


if __name__ == "__main__":
    cli()
