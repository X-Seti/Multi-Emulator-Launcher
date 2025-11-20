# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] Git installed
- [ ] RetroArch installed
- [ ] PS4 controller (optional, keyboard works too)

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/multi-emulator-launcher.git
cd multi-emulator-launcher
```

### 2. Run Setup

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create virtual environment
- Install dependencies
- Create directory structure
- Generate config files

### 3. Add Cores

**Option A: Copy from RetroArch**

```bash
# Linux
cp ~/.config/retroarch/cores/*_libretro.so cores/

# macOS
cp ~/Library/Application\ Support/RetroArch/cores/*.dylib cores/

# Windows (PowerShell)
Copy-Item "$env:APPDATA\RetroArch\cores\*.dll" cores\
```

**Option B: Download Manually**

Download cores from [buildbot.libretro.com](https://buildbot.libretro.com/nightly/)

Place in `cores/` directory.

### 4. Add BIOS Files (if needed)

```bash
# Example for Amiga
mkdir -p bios/Amiga
# Copy your kick*.rom files to bios/Amiga/

# Example for Atari ST
mkdir -p bios/Atari\ ST
# Copy your tos.img to bios/Atari ST/
```

### 5. Add Your ROMs

```bash
# Create platform directories
mkdir -p roms/Amiga
mkdir -p roms/"Atari ST"
mkdir -p roms/"Amstrad CPC"

# Copy your ROM files
cp /path/to/your/amiga/games/*.adf roms/Amiga/
cp /path/to/your/atari/games/*.st roms/"Atari ST"/
# etc...
```

### 6. Launch!

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Run the launcher
python main.py
```

## First Time Setup

When you launch for the first time:

1. **Settings Tab** - Verify paths are correct
2. **Platform Tabs** - Should auto-populate with your ROM folders
3. **Select a Game** - Use arrow keys or controller
4. **Press Enter or X (Cross)** - Launch the game!

## Keyboard Controls

| Key | Action |
|-----|--------|
| ↑↓ | Navigate games |
| ←→ | Switch tabs |
| Enter | Launch game |
| Esc | Exit |

## PS4 Controller Controls

| Button | Action |
|--------|--------|
| D-Pad/Left Stick | Navigate games |
| ✖ (Cross) | Launch game |
| ○ (Circle) | Exit |
| L1/R1 | Switch tabs |
| Options | Settings |

## Troubleshooting

### "No cores found"
```bash
# Check cores directory
ls -la cores/

# Should see files like:
# puae_libretro.so
# hatari_libretro.so
# etc.
```

### "RetroArch not found"
```bash
# Test RetroArch installation
which retroarch  # Linux/Mac
where retroarch  # Windows

# Install if missing:
# Linux: sudo apt install retroarch
# Mac: brew install retroarch
# Windows: Download from retroarch.com
```

### "No games found"
```bash
# Check ROM directory structure
ls -la roms/

# Should have folders like:
# roms/Amiga/
# roms/Atari ST/
# etc.

# Folder names MUST match platform names exactly
```

### "BIOS missing"
```bash
# Check BIOS structure
ls -la bios/

# Example for Amiga:
# bios/Amiga/kick13.rom
# bios/Amiga/kick31.rom

# Check platform requirements in README.md
```

### Games not launching
```bash
# Run in debug mode
python main.py

# Check terminal output for errors
# Common issues:
# - Wrong core for platform
# - Missing BIOS files
# - Incorrect file extensions
```

## Testing Individual Components

### Test game scanner
```bash
python -c "
from src.game_scanner import GameScanner
from src.platform_config import PlatformManager
import json

config = json.load(open('config/settings.json'))
pm = PlatformManager('config')
scanner = GameScanner(config, pm.platforms)

platforms = scanner.discover_platforms()
print('Platforms found:', platforms)

for p in platforms:
    games = scanner.scan_platform(p)
    print(f'{p}: {len(games)} games')
"
```

### Test ROM loader
```bash
python -c "
from src.rom_loader import RomLoader
from src.platform_config import PlatformManager
import json

config = json.load(open('config/settings.json'))
pm = PlatformManager('config')
loader = RomLoader(config, pm.platforms)

print('Cache size:', loader.get_cache_size(), 'bytes')
"
```

### Test RetroArch connection
```bash
# Check RetroArch version
retroarch --version

# List available cores
retroarch --list-libretro-cores

# Test launching a core directly
retroarch -L cores/puae_libretro.so --verbose
```

## Directory Structure Check

Your structure should look like this:

```
multi-emulator-launcher/
├── venv/                  ✓ Created by setup.sh
├── cores/
│   ├── puae_libretro.so  ✓ You add these
│   ├── hatari_libretro.so
│   └── ...
├── bios/
│   ├── Amiga/            ✓ You create and populate
│   │   ├── kick13.rom
│   │   └── kick31.rom
│   └── Atari ST/
│       └── tos.img
├── roms/
│   ├── Amiga/            ✓ You create and populate
│   │   ├── Game1.adf
│   │   └── Game2.zip
│   └── Atari ST/
│       └── Game.st
├── config/
│   └── settings.json     ✓ Created by setup.sh
└── ... (source files)
```

## Minimum Test Setup

To test without a full collection:

1. **One core** - e.g., `puae_libretro.so` for Amiga
2. **Required BIOS** - Amiga needs kickstart ROMs
3. **One game** - Single `.adf` file
4. **One platform folder** - `roms/Amiga/`

Example:
```bash
# Minimal Amiga setup
cores/puae_libretro.so
bios/Amiga/kick31.rom
roms/Amiga/TestGame.adf
```

Then run:
```bash
python main.py
```

You should see:
- Amiga tab appear
- TestGame in the list
- Able to launch with Enter

## Next Steps

Once you have it working:

1. **Add more platforms** - Copy more cores and create ROM folders
2. **Organize ROMs** - Use subdirectories if needed (they'll be scanned)
3. **Configure settings** - Edit `config/settings.json` for display/input
4. **Set up controller** - Connect PS4 controller before launching
5. **Clear cache** - Use Settings tab if things get messy

## Common File Extensions by Platform

| Platform | Extensions |
|----------|-----------|
| Amiga | .adf, .ipf, .dms, .hdf |
| Atari ST | .st, .stx, .msa |
| Amstrad CPC | .cdt, .dsk |
| Atari 2600 | .bin, .a26 |
| Atari 800 | .atr, .xex |

## Getting Help

1. Check README.md for detailed documentation
2. Check CONTRIBUTING.md for development info
3. Open an issue on GitHub
4. Check existing issues for solutions

## Success Indicators

✅ No errors when running `python main.py`  
✅ Platform tabs appear  
✅ Games listed in each tab  
✅ Can launch a game successfully  
✅ Controller responds (if connected)  

## Performance Tips

- **Enable caching** - Keeps extracted ZIPs for faster loading
- **Use .adf over .zip** - Direct files load faster
- **Group multi-disk games** - Use consistent naming (Disk 1, Disk 2)
- **Clear old cache** - Use Settings → Clear Cache periodically

## You're Ready! 🎮

Start playing your retro games with a clean, controller-friendly interface!

Questions? Check the [Wiki](../../wiki) or [open an issue](../../issues).