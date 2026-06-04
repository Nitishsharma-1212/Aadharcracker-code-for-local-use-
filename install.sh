#!/bin/bash

# AADHAAR ULTRACODE - INSTALLATION SCRIPT
echo "============================================================"
echo "    SUBTLE0 - ULTRACODE MASTER INSTALLER"
echo "============================================================"

# Create virtual environment if it doesn't exist
if [ ! -d "myenv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv myenv
fi

# 1. Install pip dependencies
echo "[*] Installing required Python libraries..."
source myenv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 2. Setup the global command shortcut
echo "[*] Setting up 'ultracode' shortcut for terminal..."

CURRENT_DIR=$(pwd)
WRAPPER_PATH="$HOME/.local/bin/ultracode"

mkdir -p "$HOME/.local/bin"

# Write the shortcut scripts
echo '#!/bin/bash' > "$WRAPPER_PATH"
echo "source \"$CURRENT_DIR/myenv/bin/activate\"" >> "$WRAPPER_PATH"
echo "python3 \"$CURRENT_DIR/ultracode.py\" \"\$@\"" >> "$WRAPPER_PATH"
chmod +x "$WRAPPER_PATH"

WEB_WRAPPER_PATH="$HOME/.local/bin/ultracode-web"
echo '#!/bin/bash' > "$WEB_WRAPPER_PATH"
echo "source \"$CURRENT_DIR/myenv/bin/activate\"" >> "$WEB_WRAPPER_PATH"
echo "python3 \"$CURRENT_DIR/app.py\" \"\$@\"" >> "$WEB_WRAPPER_PATH"
chmod +x "$WEB_WRAPPER_PATH"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo "[!] Added ~/.local/bin to PATH. You might need to restart terminal or run: source ~/.bashrc"
fi

echo "============================================================"
echo "🔥 INSTALLATION SUCCESSFUL! 🔥"
echo "Now you can run the tool from anywhere by typing:"
echo "👉 Terminal Tool: ultracode"
echo "👉 Web Interface: ultracode-web"
echo "============================================================"
