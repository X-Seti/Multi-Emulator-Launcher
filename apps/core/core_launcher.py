#!/usr/bin/env python3
#this belongs in apps/core/core_launcher.py - Version: 1
# X-Seti - November19 2025 - Multi-Emulator Launcher - Direct Core Launcher

"""
Direct Libretro Core Launcher
Launches emulator cores directly without RetroArch
Uses libretro API to load and run cores with ROMs
"""

import os
import sys
import ctypes
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess

##Methods list -
# __init__
# get_core_path
# is_running
# launch_game
# launch_with_subprocess
# stop_emulation
# _find_core_for_platform
# _get_bios_path
# _load_core_library
# _verify_bios

##class CoreLauncher -

class CoreLauncher: #vers 1
    """Direct libretro core launcher"""
    
    def __init__(self, base_dir: Path, core_database: Dict): #vers 1
        """Initialize core launcher
        
        Args:
            base_dir: Base directory containing cores, roms, etc
            core_database: Platform -> core info mapping
        """
        self.base_dir = Path(base_dir)
        self.cores_dir = self.base_dir / "cores"
        self.roms_dir = self.base_dir / "roms"
        self.bios_dir = self.base_dir / "bios"
        self.saves_dir = self.base_dir / "saves"
        
        self.core_database = core_database
        self.current_process = None
        self.loaded_core = None
        
    def launch_game(self, platform: str, rom_path: Path, core_name: Optional[str] = None) -> bool: #vers 1
        """Launch a game using appropriate core
        
        Args:
            platform: Platform name (e.g. "PlayStation 1")
            rom_path: Path to ROM file
            core_name: Specific core to use (optional, will auto-select)
            
        Returns:
            True if launch successful, False otherwise
        """
        if not rom_path.exists():
            print(f"ROM not found: {rom_path}")
            return False
            
        # Get platform info
        platform_info = self.core_database.get(platform)
        if not platform_info:
            print(f"Unknown platform: {platform}")
            return False
            
        # Select core
        if not core_name:
            core_name = self._find_core_for_platform(platform)
            
        if not core_name:
            print(f"No core available for {platform}")
            return False
            
        # Get core path
        core_path = self.get_core_path(core_name)
        if not core_path or not core_path.exists():
            print(f"Core not found: {core_name}")
            return False
            
        # Check BIOS requirements
        if platform_info.get("bios_required"):
            bios_valid = self._verify_bios(platform, platform_info)
            if not bios_valid:
                print(f"Required BIOS files missing for {platform}")
                return False
                
        # Launch using subprocess (simpler than ctypes for now)
        return self.launch_with_subprocess(core_path, rom_path, platform)
        
    def launch_with_subprocess(self, core_path: Path, rom_path: Path, platform: str) -> bool: #vers 2
        """Launch core using subprocess
        
        This uses standalone libretro players like:
        - retroarch (if available)
        - mednafen (for some cores)
        - standalone emulators
        """
        # Build command
        # For now, use direct core execution or standalone emulators
        
        # Check for standalone executables based on platform
        standalone_launchers = {
            "PlayStation 2": ["pcsx2", "pcsx2-qt"],
            "PlayStation 1": ["duckstation-qt", "epsxe"],
            "Nintendo 64": ["mupen64plus"],
            "Super Nintendo": ["snes9x-gtk", "bsnes"],
            "Nintendo Entertainment System": ["fceux"],
            "Game Boy Advance": ["mgba-qt", "visualboyadvance"],
            "Nintendo DS": ["desmume", "melonDS"],
            "Sega Genesis": ["kega-fusion", "blastem"],
            "Nintendo GameCube": ["dolphin-emu"],
            "Nintendo Wii": ["dolphin-emu"],
            "PSP": ["ppsspp-qt", "ppsspp"]
        }
        
        launchers = standalone_launchers.get(platform, [])
        
        for launcher in launchers:
            # Check if launcher exists
            try:
                result = subprocess.run(["which", launcher], 
                                      capture_output=True, 
                                      text=True,
                                      timeout=2)
                if result.returncode == 0:
                    # Found launcher
                    print(f"Launching with {launcher}")
                    
                    # Build command
                    cmd = [launcher, str(rom_path)]
                    
                    # Add BIOS path if needed
                    bios_path = self._get_bios_path(platform)
                    if bios_path:
                        # Some emulators need BIOS path argument
                        cmd.extend(["--bios", str(bios_path)])
                        
                    # Launch in background
                    self.current_process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    
                    print(f"✓ Launched: {rom_path.name}")
                    return True
                    
            except Exception as e:
                continue
                
        # Fallback: Try using the core directly with a generic runner
        print(f"No standalone launcher found for {platform}")
        print(f"Core: {core_path}")
        print(f"ROM: {rom_path}")
        
        # For now, just report what would be launched
        print("\nTo launch this game, you need to install one of:")
        for launcher in launchers:
            print(f"  - {launcher}")
            
        return False
        
    def stop_emulation(self) -> bool: #vers 1
        """Stop current emulation"""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
                self.current_process = None
                print("✓ Emulation stopped")
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
            return True  # No BIOS required
            
        bios_path = self._get_bios_path(platform)
        if not bios_path:
            print(f"BIOS directory not found: {platform}")
            return False
            
        missing = []
        for bios_file in bios_files:
            if not (bios_path / bios_file).exists():
                missing.append(bios_file)
                
        if missing:
            print(f"Missing BIOS files for {platform}:")
            for f in missing:
                print(f"  - {f}")
            return False
            
        return True
        
    def _load_core_library(self, core_path: Path) -> Optional[ctypes.CDLL]: #vers 1
        """Load core as shared library (advanced - for future)"""
        try:
            lib = ctypes.CDLL(str(core_path))
            return lib
        except Exception as e:
            print(f"Error loading core: {e}")
            return None


def get_installed_emulators() -> Dict[str, str]: #vers 1
    """Get list of installed standalone emulators"""
    emulators = {
        # PlayStation
        "pcsx2": "PlayStation 2",
        "pcsx2-qt": "PlayStation 2",
        "duckstation-qt": "PlayStation 1",
        "epsxe": "PlayStation 1",
        "ppsspp": "PSP",
        "ppsspp-qt": "PSP",
        
        # Nintendo
        "mupen64plus": "Nintendo 64",
        "snes9x-gtk": "Super Nintendo",
        "bsnes": "Super Nintendo",
        "fceux": "Nintendo Entertainment System",
        "mgba-qt": "Game Boy Advance",
        "visualboyadvance": "Game Boy Advance",
        "desmume": "Nintendo DS",
        "melonDS": "Nintendo DS",
        "dolphin-emu": "Nintendo GameCube/Wii",
        
        # Sega
        "kega-fusion": "Sega Genesis",
        "blastem": "Sega Genesis",
        
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
        
        launcher = CoreLauncher(base_dir, downloader.CORE_DATABASE)
        
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
