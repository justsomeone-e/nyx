#!/usr/bin/env bash
set -e

echo "==================================================================="
echo "⚡ Installing Nyx Core Toolchain (v2.0.0 Beta 1)..."
echo "==================================================================="

INSTALL_DIR="$HOME/.nyx"
BIN_DIR="$INSTALL_DIR/bin"

mkdir -p "$BIN_DIR"

if ! command -v python3 &> /dev/null; then
    echo "[!] Warning: Python 3.10+ is required to run Nyx."
    echo "    Install via your package manager (e.g. sudo apt install python3)"
else
    echo "[✓] Found Python: $(command -v python3)"
fi

# Create executable wrappers for nyx and he
for cmd in nyx he; do
    WRAPPER="$BIN_DIR/$cmd"
    cat << 'EOF' > "$WRAPPER"
#!/usr/bin/env bash
exec python3 "$HOME/.nyx/src/cli.py" "$@"
EOF
    chmod +x "$WRAPPER"
done

echo "==================================================================="
echo "[✓] Nyx binary wrappers created at: $BIN_DIR"
echo "    Add to your PATH by adding the following line to ~/.bashrc or ~/.zshrc:"
echo "    export PATH=\"\$PATH:$BIN_DIR\""
echo "==================================================================="
