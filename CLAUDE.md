# CLAUDE.md

## Project Overview

**namigate** — A Kanagawa-themed TUI to navigate and launch your SSH connections. Built with [Textual](https://github.com/Textualize/textual). The single entry point is `main.py`.

## Project Structure

```
ssh_list/
├── main.py                   # Main application
├── connections.sample.json   # Sample connection file for new users
├── install.sh                # Installs launcher to ~/.local/bin/server
├── requirements.txt          # Python dependencies (textual>=0.48.0)
├── .python-version           # Minimum Python version (3.8)
├── venv/                     # Virtual environment (gitignored)
└── CLAUDE.md

~/.config/namigate/           # Created by install.sh; optionally a private git repo for sync
└── connections.json          # SSH connection definitions
```

## Running the App

```bash
# After install.sh:
server

# Or manually:
source venv/bin/activate
python main.py
```

## Architecture

- `SSHConnectionTable` — a `DataTable` subclass with row cursor and zebra stripes
- `ListSSH` — the main `App`; loads connections from `connections.json`, handles row selection, and calls `os.system()` to execute the SSH command after the TUI exits

## Connections

Connections are stored in `~/.config/namigate/connections.json` as a JSON array. Each entry has: `alias`, `hostname`, `user`, `port`, `location`, `description`.

The file is stored outside the app repo so it can optionally live in its own private git repo for cross-device sync. The app pulls on every launch and on `ctrl+r` if the directory is a git repo.

## Dependencies

- `textual>=0.48.0` — the only external dependency
