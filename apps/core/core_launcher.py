#!/usr/bin/env python3
#this belongs in apps/core/core_launcher.py - Version: 6
# X-Seti - December01 2025 - Multi-Emulator Launcher - Direct Core Launcher

"""
Direct Libretro Core Launcher
Launches emulator cores directly without RetroArch
Uses libretro API to load and run cores with ROMs
NOW PREFERS LOCAL CORES FIRST + USER DISPLAY SETTINGS
"""

import os
import sys
import ctypes
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
from ..database.database_manager import DatabaseManager

##Methods list -
# __init__
# get_core_path
# is_running
# launch_game
# launch_with_subprocess
# normalize_platform_name
# stop_emulation
# update_database
# _find_core_for_platform
# _get_bios_path
# _load_core_library
# _load_database_from_db
# _verify_bios

##class CoreLauncher -

class CoreLauncher: #vers 6
    """Direct libretro core launcher - PREFERS LOCAL CORES"""

    def __init__(self, base_dir: Path, core_database: Dict = None, core_downloader=None, db_manager: DatabaseManager = None): #vers 4
        """Initialize core launcher"""
        self.base_dir = Path(base_dir)
        self.cores_dir = self.base_dir / "cores"
        self.roms_dir = self.base_dir / "roms"
        self.bios_dir = self.base_dir / "bios"
        self.saves_dir = self.base_dir / "saves"

        self.core_downloader = core_downloader
        self.db_manager = db_manager or DatabaseManager()
        self.current_process = None
        self.loaded_core = None

        # Load database
        self.core_database = core_database or self._load_database_from_db()

        print(f"CoreLauncher initialized")
        print(f"  Cores dir: {self.cores_dir}")
        print(f"  Database: {len(self.core_database)} platforms loaded")

    def _load_database_from_db(self): #vers 1
        """Load platform database from database manager"""
        if not self.db_manager:
            return {}

        try:
            platforms = self.db_manager.get_all_platforms()
            database = {}

            for platform in platforms:
                database[platform['name']] = {
                    'cores': platform.get('cores', '').split(',') if platform.get('cores') else [],
                    'extensions': platform.get('extensions', '').split(',') if platform.get('extensions') else [],
                    'bios_required': bool(platform.get('bios_required', 0)),
                    'bios_files': platform.get('bios_files', '').split(',') if platform.get('bios_files') else []
                }

            return database
        except Exception as e:
            print(f"Error loading database: {e}")
            return {}

    def normalize_platform_name(self, platform: str) -> str: #vers 1
        """Normalize platform name for fuzzy matching"""
        if self.core_downloader and hasattr(self.core_downloader, 'normalize_platform_name'):
            return self.core_downloader.normalize_platform_name(platform)
        return platform

    def update_database(self, new_database: Dict): #vers 1
        """Update core database"""
        self.core_database = new_database
        print(f"Database updated: {len(self.core_database)} platforms")

    def launch_game(self, platform: str, rom_path: Path, core_name: Optional[str] = None, game_config: Optional[Dict] = None) -> bool: #vers 4
        """Launch a game using appropriate core

        Args:
            platform: Platform name
            rom_path: Path to ROM file
            core_name: Specific core to use (optional, will auto-select)
            game_config: Optional game configuration dict

        Returns:
            True if launch successful, False otherwise
        """
        if not rom_path.exists():
            print(f"ROM not found: {rom_path}")
            return False

        # Reload database from database manager
        self.core_database = self._load_database_from_db()

        # Normalize platform name
        normalized_platform = self.normalize_platform_name(platform)

        print(f"\n=== Launching Game ===")
        print(f"Platform: '{platform}' -> '{normalized_platform}'")
        print(f"ROM: {rom_path.name}")

        # Get platform info
        platform_info = self.core_database.get(normalized_platform)
        if not platform_info:
            print(f"Unknown platform: {platform}")
            return False

        # Select core
        if not core_name:
            core_name = self._find_core_for_platform(normalized_platform)

        if not core_name:
            print(f"No core available for {platform}")
            # Try launching with installed emulator instead
            return self.launch_with_subprocess(None, rom_path, normalized_platform, game_config)

        # Get core path
        core_path = self.get_core_path(core_name)
        if not core_path or not core_path.exists():
            print(f"Core not found: {core_name}")
            # Try launching with installed emulator instead
            return self.launch_with_subprocess(None, rom_path, normalized_platform, game_config)

        # Check BIOS requirements
        if platform_info.get("bios_required"):
            bios_valid = self._verify_bios(normalized_platform, platform_info)
            if not bios_valid:
                print(f"Warning: Required BIOS files may be missing for {platform}")

        # Launch using subprocess
        return self.launch_with_subprocess(core_path, rom_path, normalized_platform, game_config)

    def launch_with_subprocess(self, core_path: Optional[Path], rom_path: Path, platform: str, game_config: Optional[Dict] = None) -> bool: #vers 5
        """Launch using local core OR installed emulator

        NEW BEHAVIOR: Prefers local cores FIRST, then installed emulators
        NOW USES USER DISPLAY SETTINGS from mel_settings.json

        Args:
            core_path: Path to local core file (if available)
            rom_path: Path to ROM file
            platform: Platform name
            game_config: Optional game configuration dict
        """

        # ==== PRIORITY 1: LOCAL CORES ====
        if core_path and core_path.exists():
            print(f"✓ Using local core: {core_path.name}")

            # Try RetroArch first (if installed)
            try:
                result = subprocess.run(["which", "retroarch"],
                                      capture_output=True,
                                      timeout=2)
                if result.returncode == 0:
                    print("  Launching with RetroArch...")
                    cmd = ["retroarch", "-L", str(core_path), str(rom_path)]

                    # Add custom args from game_config
                    if game_config:
                        custom_args = game_config.get("custom_args", "")
                        if custom_args:
                            cmd.extend(custom_args.split())

                        if game_config.get("fullscreen", False):
                            cmd.append("--fullscreen")

                    # Launch
                    self.current_process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    print(f"✓ Launched with local core: {rom_path.name}")
                    return True
            except Exception as e:
                print(f"  RetroArch not available: {e}")

        # ==== PRIORITY 2: INSTALLED STANDALONE EMULATORS ====
        print("  Checking for installed standalone emulators...")

        standalone_launchers = {
            "PlayStation 2": ["pcsx2", "pcsx2-qt"],
            "PlayStation 1": ["duckstation-qt", "epsxe"],
            "Nintendo 64": ["mupen64plus"],
            "Super Nintendo": ["snes9x-gtk", "bsnes"],
            "SNES": ["snes9x-gtk", "bsnes"],
            "Nintendo Entertainment System": ["fceux"],
            "NES": ["fceux"],
            "Game Boy Advance": ["mgba-qt", "visualboyadvance"],
            "GBA": ["mgba-qt", "visualboyadvance"],
            "Nintendo DS": ["desmume", "melonDS"],
            "Sega Genesis": ["kega-fusion", "blastem"],
            "Sega Mega Drive": ["kega-fusion", "blastem"],
            "Nintendo GameCube": ["dolphin-emu"],
            "Nintendo Wii": ["dolphin-emu"],
            "PSP": ["ppsspp-qt", "ppsspp"],
            "Amiga": ["fs-uae", "amiberry", "amiberry-lite"],
            "Atari ST": ["hatari"],
            "Atari 2600": ["stella"],
            "Atari 800": ["atari800"],
            "Amstrad CPC": ["cap32", "caprice32"],
            "BBC Micro": ["b2"],
            "Commodore 64": ["vice"],
            "C64": ["vice"],
            "ZX Spectrum": ["fuse"],
            "ZX Spectrum 128": ["fuse"],
            "MSX": ["bluemsx", "openmsx"],
            "MSX2": ["bluemsx", "openmsx"]
        }

        launchers = standalone_launchers.get(platform, [])

        for launcher in launchers:
            try:
                result = subprocess.run(["which", launcher],
                                      capture_output=True,
                                      text=True,
                                      timeout=2)
                if result.returncode == 0:
                    print(f"✓ Found installed emulator: {launcher}")

                    # Build command
                    cmd = [launcher, str(rom_path)]

                    # ==== NEW: Load user display settings ====
                    try:
                        from apps.gui.mel_settings_manager import MELSettingsManager
                        mel_settings = MELSettingsManager()
                        display_mode = mel_settings.get_emulator_display_mode(launcher)

                        if display_mode and display_mode != 'auto':
                            # Apply saved display settings
                            print(f"  Applying display setting: {display_mode}")
                            cmd.extend(display_mode.split())
                    except Exception as e:
                        print(f"  Could not load display settings: {e}")

                    # Add custom args from game_config (overrides display settings)
                    if game_config:
                        custom_args = game_config.get("custom_args", "")
                        if custom_args:
                            print(f"  Applying custom args: {custom_args}")
                            cmd.extend(custom_args.split())

                        if game_config.get("fullscreen", False):
                            cmd.append("--fullscreen")

                    # Add BIOS path if needed
                    bios_path = self._get_bios_path(platform)
                    if bios_path:
                        cmd.extend(["--bios", str(bios_path)])

                    # Get working directory from game_config
                    cwd = None
                    if game_config and game_config.get("working_dir"):
                        cwd = game_config["working_dir"]

                    # Launch
                    self.current_process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        cwd=cwd
                    )

                    print(f"✓ Launched with {launcher}: {rom_path.name}")
                    return True
            except Exception as e:
                continue

        # ==== FALLBACK: NO LAUNCHER FOUND ====
        print(f"\n✗ No launcher found for {platform}")
        print(f"  Local core: {'NOT FOUND' if not core_path else core_path}")
        print(f"  Checked emulators: {', '.join(launchers) if launchers else 'None defined'}")
        print(f"\n  To launch this game, you need to either:")
        print(f"    1. Download the core to {self.cores_dir}/")
        print(f"    2. Install one of: {', '.join(launchers) if launchers else 'N/A'}")

        return False

    def stop_emulation(self) -> bool: #vers 2
        """Stop current emulation"""
        if self.current_process:
            try:
                print("Stopping emulation...")
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
                self.current_process = None
                print("✓ Emulation stopped")
                return True
            except subprocess.TimeoutExpired:
                print("Timeout stopping emulation - forcing kill")
                self.current_process.kill()
                self.current_process = None
                return True
            except Exception as e:
                print(f"Error stopping emulation: {e}")
                return False
        return True

    def is_running(self) -> bool: #vers 1
        """Check if emulation is currently running"""
        if self.current_process:
            return self.current_process.poll() is None
        return False

    def get_core_path(self, core_name: str) -> Optional[Path]: #vers 1
        """Get full path to core file"""
        # Check for .so (Linux), .dll (Windows), .dylib (macOS)
        for ext in ['.so', '.dll', '.dylib']:
            core_file = self.cores_dir / f"{core_name}_libretro{ext}"
            if core_file.exists():
                return core_file
        return None

    def _find_core_for_platform(self, platform: str) -> Optional[str]: #vers 1
        """Find best available core for platform"""
        platform_info = self.core_database.get(platform)
        if not platform_info:
            return None

        cores = platform_info.get("cores", [])

        # Find first available core
        for core_name in cores:
            core_path = self.get_core_path(core_name)
            if core_path:
                return core_name

        return None

    def _get_bios_path(self, platform: str) -> Optional[Path]: #vers 1
        """Get BIOS directory for platform"""
        bios_path = self.bios_dir / platform
        if bios_path.exists():
            return bios_path
        return None

    def _verify_bios(self, platform: str, platform_info: Dict) -> bool: #vers 1
        """Verify required BIOS files exist"""
        bios_files = platform_info.get("bios_files", [])

        if not bios_files:
            return True

        bios_path = self._get_bios_path(platform)
        if not bios_path:
            return False

        # Check if all required files exist
        for bios_file in bios_files:
            if isinstance(bios_file, dict):
                filename = bios_file.get('name', '')
            else:
                filename = bios_file

            if not (bios_path / filename).exists():
                print(f"Missing BIOS file: {filename}")
                return False

        return True

    def _load_core_library(self, core_path: Path) -> Optional[ctypes.CDLL]: #vers 1
        """Load core library using ctypes (DEPRECATED - using subprocess now)"""
        try:
            core_lib = ctypes.CDLL(str(core_path))
            return core_lib
        except Exception as e:
            print(f"Failed to load core library: {e}")
            return None


def get_installed_emulators(): #vers 1
    """Scan system for installed emulators"""
    emulators = {
        # PlayStation
        "pcsx2": "PlayStation 2",
        "pcsx2-qt": "PlayStation 2",
        "duckstation-qt": "PlayStation 1",
        "epsxe": "PlayStation 1",
        "ppsspp-qt": "PSP",

        # Nintendo
        "mupen64plus": "Nintendo 64",
        "snes9x-gtk": "Super Nintendo",
        "fceux": "NES",
        "mgba-qt": "Game Boy Advance",
        "desmume": "Nintendo DS",
        "melonDS": "Nintendo DS",
        "dolphin-emu": "Nintendo GameCube",

        # Sega
        "blastem": "Sega Genesis",

        # Computer platforms
        "fs-uae": "Amiga",
        "amiberry": "Amiga",
        "hatari": "Atari ST",
        "stella": "Atari 2600",
        "atari800": "Atari 800",
        "cap32": "Amstrad CPC",
        "b2": "BBC Micro",
        "vice": "Commodore 64",
        "fuse": "ZX Spectrum",

        # Multi-system
        "mame": "Arcade",
        "mednafen": "Multi-System"
    }

    installed = {}

    for emu, platform in emulators.items():
        try:
            result = subprocess.run(["which", emu],
                                  capture_output=True,
                                  timeout=1)
            if result.returncode == 0:
                installed[emu] = platform
        except:
            pass

    return installed


# CLI testing
if __name__ == "__main__":
    base_dir = Path.cwd()

    if len(sys.argv) > 1 and sys.argv[1] == "detect":
        # Detect installed emulators
        print("Scanning for installed emulators...")
        print("=" * 60)

        installed = get_installed_emulators()

        if installed:
            print(f"\nFound {len(installed)} emulator(s):")
            for emu, platform in installed.items():
                print(f"  ✓ {emu} ({platform})")
        else:
            print("No emulators detected")

    elif len(sys.argv) > 3 and sys.argv[1] == "launch":
        # Test launch
        platform = sys.argv[2]
        rom_path = Path(sys.argv[3])

        # Need core database
        from core_downloader import CoreDownloader
        downloader = CoreDownloader(base_dir)

        launcher = CoreLauncher(base_dir, downloader.CORE_DATABASE, downloader)

        print(f"Launching {platform}: {rom_path.name}")
        success = launcher.launch_game(platform, rom_path)

        if success:
            print("✓ Game launched")
        else:
            print("✗ Launch failed")

    else:
        print("Direct Core Launcher")
        print("=" * 60)
        print("\nUsage:")
        print("  python core_launcher.py detect")
        print("  python core_launcher.py launch <platform> <rom_path>")
        print("\nExamples:")
        print("  python core_launcher.py detect")
        print('  python core_launcher.py launch "PlayStation 1" game.cue')
