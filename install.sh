#!/bin/bash
set -e

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
LAUNCHER="$BIN_DIR/server"

echo "Setting up ssh_list..."

# Create venv if it doesn't exist
if [ ! -d "$INSTALL_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$INSTALL_DIR/venv"
fi

# Install dependencies
echo "Installing dependencies..."
"$INSTALL_DIR/venv/bin/pip" install -q -r "$INSTALL_DIR/requirements.txt"

# Copy sample connections if no connections.json exists
if [ ! -f "$INSTALL_DIR/connections.json" ]; then
    echo "Creating connections.json from sample..."
    cp "$INSTALL_DIR/connections.sample.json" "$INSTALL_DIR/connections.json"
    echo "  -> Edit $INSTALL_DIR/connections.json to add your hosts."
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
