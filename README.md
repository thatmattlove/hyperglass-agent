# hyperglass-agent

## WARNING

This repository is a **work in progress** replacement for its soon-to-be predecessors [hyperglass-frr](https://github.com/checktheroads/hyperglass-frr) and [hyperglass-bird](https://github.com/checktheroads/hyperglass-bird). It is **NOT** functional yet!

<hr>

<div align="center">

[![SCC Line Count](https://sloc.xyz/github/checktheroads/hyperglass-agent/?category=code)](https://github.com/boyter/scc/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

</div>

<hr>

The hyperglass agent is a RESTful API agent for [hyperglass](https://github.com/checktheroads/hyperglass), currently supporting:

- [Free Range Routing](https://frrouting.org/)
- [BIRD Routing Daemon](https://bird.network.cz/)

# Installation

## System Requirements

```bash
sudo apt install -y python3.7-dev
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

## Setup

```bash
git clone https://github.com/checktheroads/hyperglass-agent /opt/hyperglass-agent
cd /opt/hyperglass-agent
poetry install --no-dev
chown -R www-data:www-data /opt/hyperglass-agent
```

# Service

Any service manager can be used. Supervisor is recommended for flexibility and ease of use.

## Supervisor Example

### Install Supervisor

```bash
sudo apt install -y supervisor
```

### Create service

Create file `/etc/supervisor/conf.d/hyperglass-agent.conf`:

```ini
[program:hyperglass-agent]
command = poetry run python3 -m hyperglass_agent.agent
directory = /opt/hyperglass-agent/
user = www-data
```

### Start the service

```bash
sudo service restart supervisor
```

## Systemd Example

Create file `/etc/systemd/system/hyperglass-agent.service` with:

```ini
[Unit]
Description=hyperglass-agent
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/hyperglass-agent
ExecStart=/home/user/.poetry/bin/poetry run python3 -m hyperglass_agent.agent

[Install]
WantedBy=multi-user.target
```

**Note**: replace `/usr/local/bin/pipenv` with the location of your `pipenv` executable: `which pipenv`

## Enabling & Starting

```bash
sudo systemctl enable hyperglass-agent
sudo systemctl restart hyperglass-agent
```

## License

[Clear BSD License](https://github.com/checktheroads/hyperglass-agent/master/LICENSE)