# namigate

A Kanagawa-themed TUI to navigate and launch your SSH connections.

## Features

- Browse SSH connections in a table with zebra stripes and row cursor
- Press **Enter** on a row to connect via SSH
- Press **h** for a help notification

## Requirements

- Python 3.8+
- [textual](https://github.com/Textualize/textual) >= 0.48.0

## Installation

```bash
git clone git@github.com:anderswodenker/namigate.git
cd namigate
./install.sh
```

The install script will:
- Create a Python virtual environment and install dependencies
- Copy `connections.sample.json` to `connections.json` if it doesn't exist
- Install a `server` launcher to `~/.local/bin/server`

Then edit `connections.json` with your actual hosts and type:

```bash
server
```

> **Note:** If `~/.local/bin` is not in your `PATH`, the script will print instructions to add it.

## Manual Usage

```bash
source venv/bin/activate
python main.py
```

### Keybindings

| Key    | Action         |
|--------|----------------|
| ↑ / ↓  | Navigate rows  |
| Enter  | Connect via SSH |
| h      | Show help      |
| q      | Quit           |

## Adding Connections

Edit `connections.json` and add entries in this format:

```json
{
  "alias": "MyServer",
  "hostname": "192.168.1.10",
  "user": "myuser",
  "port": 22,
  "location": "Home",
  "description": "My home server"
}
```
