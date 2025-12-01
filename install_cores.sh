#!/bin/bash
# X-Seti - November23 2025 - MEL Core Installer
# Installs libretro cores for recognized platforms

echo "==================================================="
echo "Multi-Emulator Launcher - Core Installer"
echo "==================================================="
echo ""

# Create cores directory
CORES_DIR="./cores"
mkdir -p "$CORES_DIR"

echo "Installing libretro cores to: $CORES_DIR"
echo ""

# Detect architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "x86_64" ]]; then
    PLATFORM="x86_64"
elif [[ "$ARCH" == "aarch64" ]] || [[ "$ARCH" == "arm64" ]]; then
    PLATFORM="aarch64"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

echo "Detected architecture: $PLATFORM"
echo ""

# Base URL for libretro buildbot
BASE_URL="https://buildbot.libretro.com/nightly/linux/${PLATFORM}/latest"

# Core list for your platforms
declare -A CORES=(
    # Retro computers
    ["puae"]="Amiga"
    ["cap32"]="Amstrad CPC"
    ["crocods"]="Amstrad CPC (alt)"
    ["hatari"]="Atari ST"
    ["stella"]="Atari 2600"
    ["atari800"]="Atari 800/5200/8-bit"
    ["prosystem"]="Atari 7800"
    ["fuse"]="ZX Spectrum"
    ["81"]="ZX81"
    ["vice_x64"]="Commodore 64"
    ["vice_x64sc"]="Commodore 64 (accurate)"
    ["vice_xplus4"]="Commodore Plus/4"
    ["fmsx"]="MSX"
    ["bluemsx"]="MSX/MSX2"
    ["xroar"]="Dragon 32/64"
    
    # Modern systems
    ["beetle_psx"]="PlayStation 1"
    ["beetle_psx_hw"]="PlayStation 1 (hw)"
    ["pcsx_rearmed"]="PlayStation 1 (ARM)"
    ["mupen64plus_next"]="Nintendo 64"
    ["parallel_n64"]="Nintendo 64 (alt)"
    ["snes9x"]="Super Nintendo"
    ["bsnes"]="Super Nintendo (accurate)"
    ["nestopia"]="NES"
    ["fceumm"]="NES (FCE Ultra)"
    ["mgba"]="Game Boy Advance"
    ["genesis_plus_gx"]="Sega Genesis"
    ["picodrive"]="Sega Genesis (alt)"
    
    # Multi-system
    ["mame"]="Multiple Arcade/Computer"
    ["mame2003_plus"]="MAME 2003+"
)

# Download function
download_core() {
    local core_name=$1
    local description=$2
    local url="${BASE_URL}/${core_name}_libretro.so.zip"
    local zip_file="${CORES_DIR}/${core_name}_libretro.so.zip"
    local so_file="${CORES_DIR}/${core_name}_libretro.so"
    
    # Skip if already exists
    if [ -f "$so_file" ]; then
        echo "✓ $core_name ($description) - already installed"
        return 0
    fi
    
    echo -n "  Downloading $core_name ($description)... "
    
    # Download with timeout
    if wget -q --timeout=10 --tries=2 "$url" -O "$zip_file" 2>/dev/null; then
        # Extract
        if unzip -q -o "$zip_file" -d "$CORES_DIR" 2>/dev/null; then
            rm "$zip_file"
            if [ -f "$so_file" ]; then
                echo "✓"
                return 0
            else
                echo "✗ (extraction failed)"
                rm -f "$zip_file"
                return 1
            fi
        else
            echo "✗ (unzip failed)"
            rm -f "$zip_file"
            return 1
        fi
    else
        echo "✗ (download failed)"
        rm -f "$zip_file"
        return 1
    fi
}

# Check for required tools
if ! command -v wget &> /dev/null; then
    echo "Error: wget is required but not installed."
    echo "Install with: sudo apt install wget"
    exit 1
fi

if ! command -v unzip &> /dev/null; then
    echo "Error: unzip is required but not installed."
    echo "Install with: sudo apt install unzip"
    exit 1
fi

# Download cores
echo "Downloading cores..."
echo ""

SUCCESS=0
FAILED=0
SKIPPED=0

for core in "${!CORES[@]}"; do
    if download_core "$core" "${CORES[$core]}"; then
        if [ -f "${CORES_DIR}/${core}_libretro.so" ]; then
            ((SUCCESS++))
        else
            ((SKIPPED++))
        fi
    else
        ((FAILED++))
    fi
done

echo ""
echo "==================================================="
echo "Installation Summary:"
echo "  ✓ Installed: $SUCCESS cores"
echo "  ⊘ Skipped (already exists): $SKIPPED cores"
echo "  ✗ Failed: $FAILED cores"
echo "==================================================="
echo ""

if [ $SUCCESS -gt 0 ]; then
    echo "✓ Cores installed to: $CORES_DIR"
    echo ""
    echo "You can now launch games for these platforms:"
    ls -1 "$CORES_DIR"/*.so 2>/dev/null | xargs -n1 basename | sed 's/_libretro.so//' | sed 's/^/  - /'
else
    echo "No cores were installed successfully."
    echo "Check your internet connection and try again."
fi

echo ""
echo "Note: Some platforms may also work with standalone emulators."
echo "Install standalone emulators with: sudo apt install <emulator>"
echo ""
