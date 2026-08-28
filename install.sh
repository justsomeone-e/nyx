#!/usr/bin/env bash
set -e

echo "==================================================================="
echo "⚡ Installing HolyEasyLang Core Toolchain (v2.0.0 Beta 1)..."
echo "==================================================================="

INSTALL_DIR="$HOME/.holyeasy"
BIN_DIR="$INSTALL_DIR/bin"

mkdir -p "$BIN_DIR"

if ! command -v python3 &> /dev/null; then
    echo "[!] Warning: Python 3.10+ is required to run HolyEasyLang."
    echo "    Install via your package manager (e.g. sudo apt install python3)"
else
    echo "[✓] Found Python: $(command -v python3)"
fi

# Create executable wrapper
WRAPPER="$BIN_DIR/he"
cat << 'EOF' > "$WRAPPER"
#!/usr/bin/env bash
exec python3 "$HOME/.holyeasy/src/cli.py" "$@"
EOF
chmod +x "$WRAPPER"

echo "==================================================================="
echo "[✓] HolyEasyLang binary wrapper created at: $WRAPPER"
echo "    Add to your PATH by adding the following line to ~/.bashrc or ~/.zshrc:"
echo "    export PATH=\"\$PATH:$BIN_DIR\""
echo "==================================================================="
