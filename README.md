# namigate

A Kanagawa-themed TUI to navigate and launch your SSH connections.

## Features

- Browse SSH connections in a filterable table with zebra stripes
- Press **Enter** on a row to connect via SSH
- Copy the SSH command to clipboard with **c**
- Optional cloud sync via a private git repo

## Requirements

- Python 3.8+
- [textual](https://github.com/Textualize/textual) >= 0.48.0

## Installation

```bash
git clone https://github.com/anderswodenker/namigate.git
cd namigate
./install.sh
```

The install script will:
- Create a Python virtual environment and install dependencies
- Create `~/.config/namigate/connections.json` from the sample if it doesn't exist
- Install a `server` launcher to `~/.local/bin/server`

Then edit `~/.config/namigate/connections.json` with your actual hosts and type:

```bash
server
```

> **Note:** If `~/.local/bin` is not in your `PATH`, the script will print instructions to add it.

## Manual Usage

```bash
source venv/bin/activate
python main.py
```

## Keybindings

| Key      | Action                          |
|----------|---------------------------------|
| ↑ / ↓    | Navigate rows                   |
| Enter    | Connect via SSH                 |
| /        | Focus search / filter           |
| Escape   | Clear filter / quit             |
| c        | Copy SSH command to clipboard   |
| ctrl+r   | Pull latest from git remote     |
| h        | Show help                       |
| q        | Quit                            |

## Adding Connections

Edit `~/.config/namigate/connections.json` and add entries in this format:

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

## Syncing Across Devices (optional)

You can keep `connections.json` in a private git repository so it stays in sync across all your machines.

**First-time setup:**

```bash
mkdir -p ~/.config/namigate && cd ~/.config/namigate
git init && git checkout -b master
# add your connections.json, then:
git remote add origin git@github.com:you/your-private-repo.git
git add connections.json && git commit -m "initial connections"
git push -u origin master
```

**On each additional machine**, pass your repo URL to `install.sh`:

```bash
./install.sh git@github.com:you/your-private-repo.git
```

The app will automatically pull the latest connections on every launch. Press **ctrl+r** to sync manually at any time.

**After editing connections on any machine:**

```bash
cd ~/.config/namigate
git add connections.json && git commit -m "update" && git push
```
