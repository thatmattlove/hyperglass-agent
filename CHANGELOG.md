# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.5 - 2020-06-28

### Fixed
- Incorrect name of systemd service file (`hyperglass-service.service` → `hyperglass-agent.service`)
- Handle empty responses properly
- Format `bgp_aspath` and `bgp_community` commands properly for BIRD ([#4](https://github.com/checktheroads/hyperglass-agent/issues/4))

### Added
- Logging to file