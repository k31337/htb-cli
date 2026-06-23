# htb-cli

Unofficial CLI to query the Hack The Box API, built with [Typer](https://typer.tiangolo.com/).

## Status

Work in progress, built incrementally.

## Requirements

- Python 3.10+
- An HTB API token (Settings > App Tokens in your HTB account)

## Installation

```bash
git clone https://github.com/<your-user>/htb-cli.git
cd htb-cli
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
# .venv\Scripts\activate         # Windows (PowerShell/cmd)
pip install -e .
```

## Configuration

The CLI reads your HTB token from the `HTB_TOKEN` environment variable.

```bash
export HTB_TOKEN=your_token_here          # Git Bash
# $env:HTB_TOKEN = "your_token_here"      # PowerShell
# set HTB_TOKEN=your_token_here           # CMD
```

## Usage

```bash
htb --help
htb version
htb machines
htb machine <id_or_name>
```

### Commands

| Command              | Description                              |
| --------------------- | ----------------------------------------- |
| `version`             | Show the CLI version                      |
| `machines`            | List active machines on HTB               |
| `machine <id_or_name>`| Show details of a single machine          |

## Project structure

```
src/htb_cli/
├── __init__.py
├── api.py   # HTTP client for the HTB API
└── cli.py   # Typer commands
```
