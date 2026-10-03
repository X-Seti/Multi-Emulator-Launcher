#!/bin/bash
# Caprice32 Launcher Wrapper
# Ensures proper window size by modifying config before launch

CONFIG_FILE="$HOME/.caprice32/cap32.cfg"

# Create config directory if needed
mkdir -p "$(dirname "$CONFIG_FILE")"

# Backup existing config
if [ -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup"
fi

# Set window size in config
cat > "$CONFIG_FILE" << EOF
scr_width=800
scr_height=600
scr_style=1
scr_bpp=32
scr_fs=0
scr_aspect=1
EOF

echo "✓ Set Caprice32 config to 800x600 windowed mode"

# Launch Caprice32 with all arguments
cap32 "$@"

# Restore backup
if [ -f "$CONFIG_FILE.backup" ]; then
    mv "$CONFIG_FILE.backup" "$CONFIG_FILE"
fi
