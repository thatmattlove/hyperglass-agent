"""Actions executed by commands."""

# Standard Library
import os
import shutil
from typing import Any, Iterable, Optional, Generator
from pathlib import Path
from datetime import datetime, timedelta
from ipaddress import ip_address

# Third Party
from click import echo, style, prompt, confirm
from inquirer import List as InquirerList
from inquirer import Checkbox

# Project
from hyperglass_agent.util import get_addresses
from hyperglass_agent.cli.echo import (
    info,
    error,
    label,
    status,
    inquire,
    success,
    warning,
)
from hyperglass_agent.cli.static import CL, NL, WS, WARNING, E


def create_dir(path: Any, **kwargs: Any) -> bool:
    """Validate and attempt to create a directory, if it does not exist."""

    # If input path is not a path object, try to make it one
    if not isinstance(path, Path):
        try:
            path = Path(path)
        except TypeError:
            error("{p} is not a valid path", p=path)

    # If path does not exist, try to create it
    if not path.exists():
        try:
            path.mkdir(**kwargs)
        except PermissionError:
            error(
                "{u} does not have permission to create {p}. Try running with sudo?",
                u=os.getlogin(),
                p=path,
            )

        # Verify the path was actually created
        if path.exists():
            success("Created {p}", p=path)

    # If the path already exists, inform the user
    elif path.exists():
        info("{p} already exists", p=path)

    return True


def generate_secret(length: int = 32) -> str:
    """Generate a secret for JWT encoding."""
    import secrets

    gen_secret = secrets.token_urlsafe(length)
    status(
        """
This secret will be used to encrypt & decrypt the communication between
hyperglass and hyperglass-agent. Before proceeding any further, please
add the secret to the `password:` field of the device's configuration in
hyperglass's devices.yaml file, and restart hyperglass.
    """
    )
    label("Secret: {s}", s=gen_secret)
    done = confirm(
        "Press enter once complete...",
        default=True,
        prompt_suffix="",
        show_default=False,
    )
    if done:  # noqa: R503
        return gen_secret


def migrate_config(force: bool = False, secret: Optional[str] = None) -> None:
    """Copy example config file and remove .example extensions."""

    app_path = os.environ.get("hyperglass_agent_directory")

    if app_path is None:
        app_path = find_app_path()
    else:
        app_path = Path(app_path)

    example = Path(__file__).parent.parent / "example_config.yaml"
    target_file = app_path / "config.yaml"

    def copy(secret):
        shutil.copyfile(example, target_file)
        if not target_file.exists():
            raise FileNotFoundError(str(target_file) + "does not exist.")

        with target_file.open("r") as f:
            data = f.read()

        if secret is None:
            secret = generate_secret()

        data = data.replace("secret: null", "secret: '{}'".format(secret))

        with target_file.open("w") as f:
            f.write(data)

        success("Successfully migrated example config file to {t}", t=target_file)

    try:
        if target_file.exists():
            if not force:
                info("{f} already exists", f=str(target_file))
            else:
                copy(secret)
        else:
            copy(secret)

    except Exception as e:
        error("Failed to migrate '{f}': {e}", f=str(target_file), e=e)


def find_app_path() -> Path:
    """Try to find the app_path, prompt user to set one if it is not found."""
    from hyperglass_agent.util import set_app_path
    from hyperglass_agent.constants import APP_PATHS

    try:
        set_app_path(required=True)
        app_path = Path(os.environ["hyperglass_agent_directory"])
    except RuntimeError:
        warning(
            "None of the supported paths for hyperglass-agent were found.\n"
            + "Checked:\n{one}\n{two}",
            one=APP_PATHS[0],
            two=APP_PATHS[1],
        )
        create = confirm(style("Would you like to create one?", **WARNING))
        if not create:
            error(
                "hyperglass-agent requires an application path, "
                + "but you've chosen not to create one."
            )
        elif create:
            available_paths = [
                InquirerList(
                    "selected",
                    message="Choose a directory for hyperglass-agent",
                    choices=APP_PATHS,
                )
            ]
            answer = inquire(available_paths)
            if answer is None:
                error("A directory for hyperglass-agent is required")
            selected = answer["selected"]

            if not selected.exists():
                create_dir(selected)

            app_path = selected

    return app_path


def read_cert() -> Generator:
    """Read public key attributes."""
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.x509.extensions import ExtensionOID
    from cryptography.hazmat.backends import default_backend

    app_path = find_app_path()
    cert_path = app_path / "agent_cert.pem"

    cert = x509.load_pem_x509_certificate(cert_path.read_bytes(), default_backend())

    for attr in cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME):
        yield attr.value
    for attr in cert.extensions.get_extension_for_oid(
        ExtensionOID.SUBJECT_ALTERNATIVE_NAME
    ).value._general_names:
        yield attr.value


def make_cert(
    cn: str, sans: Iterable, o: str, start: datetime, end: datetime, size: int = 2048
) -> Generator:
    """Generate public & private key pair for SSL."""
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes

    key = rsa.generate_private_key(
        public_exponent=65537, key_size=size, backend=default_backend()
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
        .add_extension(
            x509.SubjectAlternativeName(
                [x509.DNSName(cn), *(x509.IPAddress(i) for i in sans)]
            ),
            critical=False,
        )
        .sign(key, hashes.SHA256(), default_backend())
    )
    yield cert.public_bytes(serialization.Encoding.PEM)
    yield key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )


def write_cert(name: str, org: str, duration: int, size: int, show: bool) -> None:
    """Generate SSL certificate keypair."""
    app_path = find_app_path()
    cert_path = app_path / "agent_cert.pem"
    key_path = app_path / "agent_key.pem"

    start = datetime.now()
    end = start + timedelta(days=duration * 365)

    label("Hostname: {cn}", cn=name)
    status(
        """
A self-signed certificate with the above hostname as the common name
attribute will be generated. This hostname must be resolvable by
hyperglass via either DNS or a host file, and must match the device's
`address:` field in hyperglass's devices.yaml."""
    )
    use_name = confirm("Is this the correct hostname?", default=True)

    if not use_name:
        name = prompt("Please enter the correct hostname", type=str)

    all_ips = [f"{a} [{i}]" for i, a in get_addresses()]

    status(
        """
hyperglass-agent adds any IP addresses reachable by hyperglass as
subject alternative names to the SSL certificate. Please select any IP
addresses over which hyperglass may communicate with hyperglass-agent."""
    )

    ips = [Checkbox("ips", message="Select IPs", choices=all_ips)]
    selected = [i.split("[")[0].strip() for i in inquire(ips)["ips"]]
    selected_ips = [ip_address(i) for i in selected]

    cert, key = make_cert(
        cn=name, sans=selected_ips, o=org, start=start, end=end, size=size
    )
    if show:
        info(f'Public Key:\n{cert.decode("utf8")}')
        info(f'Private Key:\n{key.decode("utf8")}')

    with cert_path.open("wb") as cf:
        cf.write(cert)

    if not cert_path.exists():
        error("Error writing public key to {f}", f=cert_path.absolute())

    success("Wrote public key to: {f}", f=cert_path.absolute())

    with key_path.open("wb") as kf:
        kf.write(key)

    if not key_path.exists():
        error("Error writing private key to {f}", f=key_path.absolute())

    success("Wrote private key to: {f}", f=key_path.absolute())


def send_certificate() -> None:
    """Send this device's public key to hyperglass."""

    from hyperglass_agent.config import params
    from hyperglass_agent.util import send_public_key
    from pydantic import AnyHttpUrl, create_model, ValidationError

    app_path = find_app_path()
    cert_file = app_path / "agent_cert.pem"

    device_name = read_cert().send(None)

    if params.ssl is not None and not params.ssl.enable:
        confirm(
            "SSL is disabled. Proceed with sending certificate to hyperglass?",
            default=False,
            abort=True,
        )

    if not cert_file.exists():
        error("File {f} does not exist", f=cert_file)

    with cert_file.open("r") as f:
        cert = f.read().strip()

    _hg_url = prompt("Enter hyperglass URL (e.g. https://lg.example.com)", type=str)

    url_model = create_model("UrlModel", url=(AnyHttpUrl, ...))

    try:
        hg_url = url_model(url=_hg_url)
    except ValidationError as ve:
        msg = ve.errors()[0]["msg"]
        warning("URL {u} is invalid: {e}", u=_hg_url, e=msg)
        _hg_url = prompt("Enter hyperglass URL (e.g. https://lg.example.com)", type=str)
        try:
            hg_url = url_model(url=_hg_url)
        except ValidationError as ve:
            msg = ve.errors()[0]["msg"]
            error("URL {u} is invalid: {e}", u=_hg_url, e=msg)

    try:
        status = send_public_key(
            str(hg_url.url), device_name=device_name, certificate=cert, params=params
        )
        success(status)
    except RuntimeError as re:
        error(str(re))


def install_systemd(service_path: Path) -> bool:
    """Installs generated systemd file to system's systemd directory."""
    systemd = Path("/etc/systemd/system")
    installed = systemd / "hyperglass-agent.service"

    if not systemd.exists():
        error("{e} does not exist. Unable to install systemd service.", e=systemd)

    if installed.is_symlink():
        installed.unlink()

    installed.symlink_to(service_path)

    if not installed.exists():
        error("Unable to symlink {s} to {d}", s=service_path, d=installed)

    success("Symlinked {s} to {d}", s=service_path, d=installed)
    return True


def make_systemd() -> bool:
    """Generate a systemd file based on the local system."""
    from shutil import which
    from getpass import getuser

    template = """
[Unit]
Description=hyperglass-agent
After=network.target

[Service]
User={user}
Group={group}
ExecStart={bin_path} start

[Install]
WantedBy=multi-user.target
    """
    app_path = find_app_path()
    service_path = app_path / "hyperglass-agent.service"
    cmd_path = which("hyperglass-agent")

    if not cmd_path:
        bin_path = "python3 -m hyperglass_agent.console"
        warning("hyperglass executable not found, using {h}", h=bin_path)
    else:
        bin_path = cmd_path

    if app_path == Path.home():
        user = getuser()
    else:
        user = "root"

    systemd = template.format(user=user, group=user, bin_path=bin_path)

    info(f"Generated systemd service:\n{systemd}")

    if service_path.exists():
        service_path.unlink()

    with service_path.open("w") as f:
        f.write(systemd)

    if not service_path.exists():
        error("Error writing systemd file to {f}", f=service_path)

    install_systemd(service_path)

    return True


def start_web_server() -> None:
    """Start web server."""

    find_app_path()
    try:
        from hyperglass_agent.config import params
        from hyperglass_agent.api.web import start

        msg_start = "Starting hyperglass agent web server on"
        msg_uri = "http://"
        msg_host = str(params.listen_address)
        msg_port = str(params.port)
        msg_len = len("".join([msg_start, WS[1], msg_uri, msg_host, CL[1], msg_port]))

        echo(
            NL[1]
            + WS[msg_len + 8]
            + E.ROCKET
            + NL[1]
            + E.CHECK
            + style(msg_start, fg="green", bold=True)
            + WS[1]
            + style(msg_uri, fg="white")
            + style(msg_host, fg="blue", bold=True)
            + style(CL[1], fg="white")
            + style(msg_port, fg="magenta", bold=True)
            + WS[1]
            + E.ROCKET
            + NL[1]
            + WS[1]
            + NL[1]
        )
        start()

    except Exception as e:
        error("Failed to start web server: {e}", e=e)
