#!/bin/bash
set -e

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
LAUNCHER="$BIN_DIR/server"
CONNECTIONS_DIR="$HOME/.config/namigate"

# Optional: pass your private connections repo as the first argument
# Example: ./install.sh git@github.com:you/your-connections-repo.git
CONNECTIONS_REPO="${1:-}"

echo "Setting up namigate..."

# Create venv if it doesn't exist
if [ ! -d "$INSTALL_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$INSTALL_DIR/venv"
fi

# Install dependencies
echo "Installing dependencies..."
"$INSTALL_DIR/venv/bin/pip" install -q -r "$INSTALL_DIR/requirements.txt"

# Set up connections
if [ -d "$CONNECTIONS_DIR/.git" ]; then
    echo "Connections repo already set up at $CONNECTIONS_DIR."
elif [ -n "$CONNECTIONS_REPO" ]; then
    echo "Cloning connections repo to $CONNECTIONS_DIR..."
    mkdir -p "$(dirname "$CONNECTIONS_DIR")"
    git clone --branch master "$CONNECTIONS_REPO" "$CONNECTIONS_DIR"
    echo "  -> Edit $CONNECTIONS_DIR/connections.json to add your hosts."
else
    echo "No connections repo provided — creating local connections.json..."
    mkdir -p "$CONNECTIONS_DIR"
    if [ ! -f "$CONNECTIONS_DIR/connections.json" ]; then
        cp "$INSTALL_DIR/connections.sample.json" "$CONNECTIONS_DIR/connections.json"
        echo "  -> Edit $CONNECTIONS_DIR/connections.json to add your hosts."
        echo "  -> To enable cloud sync later, run: ./install.sh git@github.com:you/your-repo.git"
    fi
fi

# Create ~/.local/bin if needed
mkdir -p "$BIN_DIR"

# Write the launcher script
cat > "$LAUNCHER" << EOF
#!/bin/bash
"$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/main.py" "\$@"
EOF
chmod +x "$LAUNCHER"

echo "Installed launcher to $LAUNCHER"

# Warn if ~/.local/bin is not in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "WARNING: $BIN_DIR is not in your PATH."
    echo "Add the following line to your ~/.bashrc or ~/.zshrc:"
    echo ""
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi

echo "Done. Type 'server' to launch."
