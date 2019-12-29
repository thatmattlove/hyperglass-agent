# hyperglass-agent

## WARNING

This repository is a **work in progress** replacement for its soon-to-be predecessors [hyperglass-frr](https://github.com/checktheroads/hyperglass-frr) and [hyperglass-bird](https://github.com/checktheroads/hyperglass-bird). It is **NOT** functional yet!

<hr>

<div align="center">

![LOC](https://raw.githubusercontent.com/checktheroads/hyperglass-agent/master/line_count.svg?sanitize=true)
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
curl https://raw.githubusercontent.com/kennethreitz/pipenv/master/get-pipenv.py | python3
```

## Setup

```bash
cd /opt
git clone https://github.com/checktheroads/hyperglass-agent
cd /opt/hyperglass-agent
pipenv install
chown -R www-data:www-data /opt/hyperglass-agent
```

# Service

## Systemd Example

Create file `/etc/systemd/system/hyperglass-agent.service` with:

```systemd
[Unit]
Description=hyperglass-agent
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/hyperglass-agent
ExecStart=/usr/local/bin/pipenv run python3 -m hyperglass_agent.agent

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