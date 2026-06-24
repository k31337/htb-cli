# htb-cli

![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-GPLv3-blue)
![Status](https://img.shields.io/badge/status-work%20in%20progress-yellow)
![Built with Typer](https://img.shields.io/badge/built%20with-Typer-009485?logo=python&logoColor=white)

An unofficial command-line tool to query the [Hack The Box](https://www.hackthebox.com/) API: list machines, check their details, and view your profile, all from the terminal.

Built with [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/).

> Work in progress, built incrementally — new commands are added over time.

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
git clone https://github.com/<your-user>/htb-cli.git
cd htb-cli
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
```

### Commands

| Command                     | Description                                          |
| ---------------------------- | ----------------------------------------------------- |
| `htb login`                 | Save your API token so you don't have to set it again |
| `htb logout`                | Remove the saved API token                            |
| `htb version`               | Show the CLI version                                  |
| `htb machines`              | List active machines on HTB                           |
| `htb machines --retired`    | List retired machines on HTB                          |
| `htb machine <id_or_name>`  | Show details of a single machine                      |
| `htb challenges`            | List challenges on HTB                                |
| `htb profile`               | Show your own HTB profile                             |

Listings (`machines`, `challenges`) are paginated 15 results at a time: press `n` for next page, `p` for previous, `q` to quit.

### Examples

```bash
htb login
htb machines
htb machines --retired
htb machine 912
htb machine Nimbus
htb challenges
htb profile
```

## Troubleshooting

- **`'htb' is not recognized as an internal or external command`**: your virtual environment isn't active. Activate it as shown above.
- **`HTB token not found`**: run `htb login`, or set the `HTB_TOKEN` environment variable in your current terminal session.
- **`Invalid or expired token`**: generate a new token from Settings > App Tokens, then run `htb login` again (or update `HTB_TOKEN`).

## Project structure

```
src/htb_cli/
├── __init__.py
├── api.py   # HTTP client for the HTB API
└── cli.py   # Typer commands
```
