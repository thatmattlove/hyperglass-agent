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
sudo apt install -y python3.7-dev python3-venv
curl https://pyenv.run | bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3
```

## Setup

```bash
git clone https://github.com/checktheroads/hyperglass-agent /opt/hyperglass-agent
cd /opt/hyperglass-agent
poetry install --no-dev
chown -R www-data:www-data /opt/hyperglass-agent
```

### 'Cannot uninstall 'PyYAML' Error

Some systems may produce the following error when running `poetry install`:

```
ERROR: Cannot uninstall 'PyYAML'. It is a distutils installed project and thus we cannot accurately determine which files belong to it which would lead to only a partial uninstall.
```

You can reference [this issue](https://github.com/pypa/pip/issues/4805) or [this Stack Overflow](https://stackoverflow.com/questions/49911550/how-to-upgrade-disutils-package-pyyaml) article on the topic, but this is "easily" fixed by running:

```bash
sudo rm -rf /usr/lib/python3/dist-packages/yaml /usr/lib/python3/dist-packages/PyYAML-*
```

And then run `poetry install` again.

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

**Note**: replace `/home/user/.poetry/bin/poetry` with the location of your `poetry` executable: `which poetry`

## Enabling & Starting

```bash
sudo systemctl enable hyperglass-agent
sudo systemctl restart hyperglass-agent
```

## License

[Clear BSD License](https://github.com/checktheroads/hyperglass-agent/master/LICENSE)