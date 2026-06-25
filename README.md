# htb-cli

![CI](https://github.com/k31337/htb-cli/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue)
![Status](https://img.shields.io/badge/status-work%20in%20progress-yellow)
![Built with Typer](https://img.shields.io/badge/built%20with-Typer-009485?logo=python&logoColor=white)

An unofficial command-line tool to query the [Hack The Box](https://www.hackthebox.com/) API: browse machines and challenges, spawn and manage your active box, submit flags, and check your profile, all from the terminal.

Built with [Typer](https://typer.tiangolo.com/), [Rich](https://rich.readthedocs.io/) and [httpx](https://www.python-httpx.org/).

> Work in progress, built incrementally — new commands are added over time.

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Project structure](#project-structure)
- [Disclaimer](#disclaimer)

## Features

- Browse active and retired machines, with pagination and colored difficulty
- View full details of a single machine or challenge
- Spawn, reset, and stop your active machine
- Submit user/root flags directly from the terminal
- Browse challenges by category
- Check your own HTB profile and stats
- Manage your VPN connection: check status, list servers, switch, and download `.ovpn` files
- Raw JSON output (`--json`) on every read command, for scripting

## Requirements

- Python 3.10 or higher
- An HTB API token

### Getting your HTB token

1. Log in to [hackthebox.com](https://www.hackthebox.com/)
2. Go to **Settings > App Tokens**
3. Create a new token and copy it

Keep this token private. Anyone with it can act on the API as you. If it ever leaks, revoke it from the same settings page and create a new one.

## Installation

```bash
git clone https://github.com/k31337/htb-cli.git
cd htb-cli
```

### Option 1: pipx (recommended)

[pipx](https://pipx.pypa.io/) installs the CLI in its own isolated environment but makes the `htb` command available everywhere, with no need to activate anything.

```bash
python -m pip install --user pipx
python -m pipx ensurepath
```

Close and reopen your terminal so the `PATH` change takes effect, then:

```bash
pipx install -e .
```

The `-e` (editable) flag means pipx links directly to this repo, so any changes you pull or make are picked up immediately without reinstalling.

### Option 2: virtual environment

```bash
python -m venv .venv
pip install -e .
```

Activate the virtual environment (do this every time you open a new terminal):

```bash
source .venv/Scripts/activate   # Git Bash
.venv\Scripts\Activate.ps1      # PowerShell
.venv\Scripts\activate.bat      # CMD
```

## Configuration

You have two ways to authenticate:

### Option 1: `htb login` (persists across sessions)

```bash
htb login
```

You'll be prompted for your token (input is hidden). It's saved to `~/.htb-cli/config.json` and picked up automatically every time you run the CLI, even after closing the terminal.

To remove it:

```bash
htb logout
```

### Option 2: `HTB_TOKEN` environment variable (current session only)

```bash
export HTB_TOKEN=your_token_here          # Git Bash
$env:HTB_TOKEN = "your_token_here"        # PowerShell
set HTB_TOKEN=your_token_here             # CMD
```

This only lasts for the current terminal session and takes priority over the saved login if both are set.

## Usage

```bash
htb --help
htb <command> --help
```

### Commands

| Command                              | Description                                          |
| -------------------------------------- | ------------------------------------------------------ |
| `htb login`                           | Save your API token so you don't have to set it again |
| `htb logout`                          | Remove the saved API token                             |
| `htb version`                         | Show the CLI version                                   |
| `htb machines [--retired] [--json]`   | List active or retired machines                        |
| `htb machine <id_or_name> [--json]`   | Show details of a single machine                       |
| `htb spawn <machine_id>`              | Spawn a machine and wait for its IP                     |
| `htb stop <machine_id>`               | Stop the active machine                                |
| `htb reset <machine_id>`              | Reset the active machine                                |
| `htb submit <machine_id> <flag>`      | Submit a user/root flag                                 |
| `htb challenges [--json]`             | List challenges                                         |
| `htb challenge <id> [--json]`         | Show details of a single challenge                      |
| `htb profile [--json]`                | Show your own HTB profile                               |
| `htb vpn status`                      | Show your currently assigned VPN server                 |
| `htb vpn servers`                     | List available VPN servers                              |
| `htb vpn switch <server_id>`          | Switch to a different VPN server                         |
| `htb vpn download <server_id> [--tcp] [-o file]` | Download the `.ovpn` config for a server      |

Listings (`machines`, `challenges`) are paginated 15 results at a time: press `n` for next page, `p` for previous, `q` to quit. Pass `--json` to any read command to get raw JSON instead, for piping into tools like `jq`.

### A typical session

```bash
htb login
htb vpn servers
htb vpn switch 698
htb vpn download 698 -o lab.ovpn
htb machines
htb spawn 912
htb submit 912 32f7a3b1...
htb stop 912
```

## Troubleshooting

- **`'htb' is not recognized as an internal or external command`**: if you installed with pipx, make sure you ran `pipx ensurepath` and reopened your terminal, and that you've run `pipx install -e .` from the repo folder. If you used the venv option, activate it as shown above.
- **`HTB token not found`**: run `htb login`, or set the `HTB_TOKEN` environment variable in your current terminal session.
- **`Invalid or expired token`**: generate a new token from Settings > App Tokens, then run `htb login` again (or update `HTB_TOKEN`).
- **`Not found. Check the ID or name and try again.`**: the ID/name doesn't exist or was mistyped — double check it on the HTB website.
- **Spawning/resetting fails with a message about VIP**: starting most active machines requires an HTB VIP subscription.

## Running tests

Tests mock the HTB API with [respx](https://lundberg.github.io/respx/), so they don't need a real token or network access.

```bash
pip install -e ".[test]"
pytest -v
```

## Project structure

```
src/htb_cli/
├── __init__.py
├── api.py             # HTTP client for the HTB API
├── cli.py             # Entry point: registers commands from each module below
└── commands/
    ├── _shared.py     # Shared console, error handling, pagination, formatters
    ├── auth.py        # version, login, logout
    ├── machines.py    # machines, machine, spawn, stop, reset, submit
    ├── challenges.py  # challenges, challenge
    ├── profile.py     # profile
    └── vpn.py         # vpn status, vpn servers, vpn switch, vpn download

tests/
├── conftest.py        # Shared fixtures (fake token, isolated config file)
├── test_token_storage.py
└── test_api_client.py
```

## Disclaimer

This is an unofficial, community-built tool and is not affiliated with or endorsed by Hack The Box. Use it only with your own account and API token, and in accordance with [Hack The Box's terms of service](https://www.hackthebox.com/terms-and-conditions).
