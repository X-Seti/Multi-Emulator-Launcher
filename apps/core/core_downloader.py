#!/usr/bin/env python3
#this belongs in apps/core/core_downloader.py - Version: 2
# X-Seti - November23 2025 - Multi-Emulator Launcher - Core Downloader

"""
RetroArch Core Downloader
Downloads and manages libretro cores for different platforms
NOW WITH FUZZY NAME MATCHING - handles "AtariST", "Atari ST", "Atari_ST", etc.
"""

import os
import urllib.request
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

##Methods list -
# __init__
# download_core
# get_available_cores
# get_core_info
# get_cores_for_platform
# get_installed_cores
# normalize_platform_name
# _download_file
# _get_core_url
# _load_core_database

##class CoreDownloader -

class CoreDownloader: #vers 2
    """Manages downloading and organizing RetroArch cores with fuzzy name matching"""
    
    # Core database with platform mappings - EXPANDED for all your platforms
    CORE_DATABASE = {
        # Your platforms from tree.git
        "Acorn Aton": {
            "cores": ["mame"],
            "extensions": [".adf", ".uef"],
            "bios_required": False,
            "bios_files": []
        },
        "Acorn Electron": {
            "cores": ["mame"],
            "extensions": [".adf", ".uef"],
            "bios_required": False,
            "bios_files": []
        },
        "Amiga": {
            "cores": ["puae"],
            "extensions": [".adf", ".ipf", ".dms", ".hdf", ".hdz", ".iso", ".cue"],
            "bios_required": True,
            "bios_files": ["kick34005.A500", "kick40068.A1200"]
        },
        "Amstrad CPC": {
            "cores": ["cap32", "crocods"],
            "extensions": [".dsk", ".sna", ".cdt", ".tap"],
            "bios_required": False,
            "bios_files": []
        },
        "Atari 2600": {
            "cores": ["stella"],
            "extensions": [".bin", ".a26", ".zip"],
            "bios_required": False,
            "bios_files": []
        },
        "Atari 5200": {
            "cores": ["atari800"],
            "extensions": [".a52", ".atr", ".xex"],
            "bios_required": True,
            "bios_files": ["5200.rom"]
        },
        "Atari 7800": {
            "cores": ["prosystem"],
            "extensions": [".a78", ".bin"],
            "bios_required": True,
            "bios_files": ["7800 BIOS (U).rom"]
        },
        "Atari 800": {
            "cores": ["atari800"],
            "extensions": [".atr", ".xex", ".xfd", ".dcm", ".zip"],
            "bios_required": True,
            "bios_files": ["ATARIXL.ROM", "ATARIBAS.ROM"]
        },
        "Atari 8-bit": {
            "cores": ["atari800"],
            "extensions": [".atr", ".xex", ".xfd", ".dcm", ".zip"],
            "bios_required": True,
            "bios_files": ["ATARIXL.ROM", "ATARIBAS.ROM"]
        },
        "Atari ST": {
            "cores": ["hatari"],
            "extensions": [".st", ".stx", ".msa", ".dim", ".zip"],
            "bios_required": True,
            "bios_files": ["tos.img"]
        },
        "BBC Micro": {
            "cores": ["mame"],
            "extensions": [".ssd", ".dsd", ".img", ".uef"],
            "bios_required": False,
            "bios_files": []
        },
        "Commodore 64": {
            "cores": ["vice_x64"],
            "extensions": [".d64", ".t64", ".crt", ".prg", ".tap"],
            "bios_required": False,
            "bios_files": []
        },
        "C64": {
            "cores": ["vice_x64"],
            "extensions": [".d64", ".t64", ".crt", ".prg", ".tap"],
            "bios_required": False,
            "bios_files": []
        },
        "MSX": {
            "cores": ["fmsx", "bluemsx"],
            "extensions": [".rom", ".mx1", ".mx2", ".dsk"],
            "bios_required": True,
            "bios_files": ["MSX.ROM", "MSX2.ROM"]
        },
        "MSX2": {
            "cores": ["fmsx", "bluemsx"],
            "extensions": [".rom", ".mx1", ".mx2", ".dsk"],
            "bios_required": True,
            "bios_files": ["MSX2.ROM", "MSX2EXT.ROM"]
        },
        "Plus4": {
            "cores": ["vice_xplus4"],
            "extensions": [".p41", ".prg", ".d64"],
            "bios_required": False,
            "bios_files": []
        },
        "Sam Coupe": {
            "cores": ["mame"],
            "extensions": [".mgt", ".sad", ".dsk"],
            "bios_required": False,
            "bios_files": []
        },
        "ZX Spectrum": {
            "cores": ["fuse"],
            "extensions": [".tap", ".tzx", ".z80", ".sna", ".dsk"],
            "bios_required": False,
            "bios_files": []
        },
        "ZX Spectrum 128": {
            "cores": ["fuse"],
            "extensions": [".tap", ".tzx", ".z80", ".sna", ".dsk"],
            "bios_required": False,
            "bios_files": []
        },
        "Z81-Spec256": {
            "cores": ["fuse"],
            "extensions": [".tap", ".tzx", ".z80", ".sna"],
            "bios_required": False,
            "bios_files": []
        },
        "Dragon 32-64": {
            "cores": ["xroar"],
            "extensions": [".cas", ".wav", ".k7", ".dsk", ".vdk"],
            "bios_required": False,
            "bios_files": []
        },
        "Fujitsu FM-7": {
            "cores": ["mame"],
            "extensions": [".d77", ".t77"],
            "bios_required": False,
            "bios_files": []
        },
        "Oric Atmos": {
            "cores": ["mame"],
            "extensions": [".tap", ".dsk"],
            "bios_required": False,
            "bios_files": []
        },
        "TRS-80": {
            "cores": ["mame"],
            "extensions": [".cas", ".cmd", ".dsk"],
            "bios_required": False,
            "bios_files": []
        },
        
        # Modern platforms
        "PlayStation 2": {
            "cores": ["pcsx2"],
            "extensions": [".iso", ".bin", ".cue", ".img", ".mdf"],
            "bios_required": True,
            "bios_files": ["SCPH10000.bin", "SCPH39001.bin", "SCPH70012.bin"]
        },
        "PlayStation 1": {
            "cores": ["pcsx_rearmed", "beetle_psx", "beetle_psx_hw"],
            "extensions": [".cue", ".bin", ".img", ".iso", ".chd", ".pbp"],
            "bios_required": True,
            "bios_files": ["scph1001.bin", "scph5501.bin", "scph7001.bin"]
        },
        "PSP": {
            "cores": ["ppsspp"],
            "extensions": [".iso", ".cso", ".pbp"],
            "bios_required": False,
            "bios_files": []
        },
        "Nintendo 64": {
            "cores": ["mupen64plus_next", "parallel_n64"],
            "extensions": [".n64", ".v64", ".z64"],
            "bios_required": False,
            "bios_files": []
        },
        "Super Nintendo": {
            "cores": ["snes9x", "bsnes"],
            "extensions": [".sfc", ".smc", ".fig", ".swc"],
            "bios_required": False,
            "bios_files": []
        },
        "SNES": {
            "cores": ["snes9x", "bsnes"],
            "extensions": [".sfc", ".smc", ".fig", ".swc"],
            "bios_required": False,
            "bios_files": []
        },
        "Nintendo Entertainment System": {
            "cores": ["nestopia", "fceumm", "mesen"],
            "extensions": [".nes", ".fds", ".unf"],
            "bios_required": False,
            "bios_files": []
        },
        "NES": {
            "cores": ["nestopia", "fceumm"],
            "extensions": [".nes", ".fds", ".unf"],
            "bios_required": False,
            "bios_files": []
        },
        "Game Boy Advance": {
            "cores": ["mgba", "vba_next"],
            "extensions": [".gba", ".gb", ".gbc"],
            "bios_required": False,
            "bios_files": ["gba_bios.bin"]
        },
        "GBA": {
            "cores": ["mgba", "vba_next"],
            "extensions": [".gba", ".gb", ".gbc"],
            "bios_required": False,
            "bios_files": []
        },
        "Nintendo DS": {
            "cores": ["desmume", "melonds"],
            "extensions": [".nds"],
            "bios_required": True,
            "bios_files": ["bios7.bin", "bios9.bin", "firmware.bin"]
        },
        "Sega Genesis": {
            "cores": ["genesis_plus_gx", "picodrive"],
            "extensions": [".md", ".smd", ".gen", ".bin"],
            "bios_required": False,
            "bios_files": []
        },
        "Sega Mega Drive": {
            "cores": ["genesis_plus_gx", "picodrive"],
            "extensions": [".md", ".smd", ".gen", ".bin"],
            "bios_required": False,
            "bios_files": []
        },
        "Nintendo Switch": {
            "cores": ["yuzu"],
            "extensions": [".nsp", ".xci"],
            "bios_required": True,
            "bios_files": ["prod.keys", "title.keys"]
        },
        "Nintendo GameCube": {
            "cores": ["dolphin"],
            "extensions": [".iso", ".gcm", ".gcz", ".elf", ".dol"],
            "bios_required": False,
            "bios_files": []
        },
        "Nintendo Wii": {
            "cores": ["dolphin"],
            "extensions": [".iso", ".wbfs", ".wad"],
            "bios_required": False,
            "bios_files": []
        },
        "Arcade": {
            "cores": ["mame", "mame2003_plus", "fbneo"],
            "extensions": [".zip"],
            "bios_required": True,
            "bios_files": ["neogeo.zip", "qsound.zip"]
        }
    }
    
    # Platform name aliases for fuzzy matching
    PLATFORM_ALIASES = {
        "atarist": "Atari ST",
        "atari_st": "Atari ST",
        "atari-st": "Atari ST",
        "amstradcpc": "Amstrad CPC",
        "amstrad_cpc": "Amstrad CPC",
        "amstrad-cpc": "Amstrad CPC",
        "amstrad464": "Amstrad CPC",
        "amstrad_464": "Amstrad CPC",
        "amstrad6128": "Amstrad CPC",
        "amstrad_6128": "Amstrad CPC",
        "atari8bit": "Atari 8-bit",
        "atari-8-bit": "Atari 8-bit",
        "atari_8_bit": "Atari 8-bit",
        "dragon3264": "Dragon 32-64",
        "dragon32": "Dragon 32-64",
        "dragon64": "Dragon 32-64",
        "fujitsu": "Fujitsu FM-7",
        "oricatmos": "Oric Atmos",
        "oric_atmos": "Oric Atmos",
        "oric-atmos": "Oric Atmos",
        "samcoupe": "Sam Coupe",
        "sam_coupe": "Sam Coupe",
        "spectrumtapfiles": "ZX Spectrum",
        "spectrum_tap_files": "ZX Spectrum",
        "tandy": "TRS-80",
        "trs80": "TRS-80",
        "trs-80": "TRS-80",
        "z8148k128k": "ZX Spectrum",
        "z81_48k_128k": "ZX Spectrum",
        "sagagenesis": "Sega Genesis",
        "genesis": "Sega Genesis",
        "bbcmicro": "BBC Micro",
        "bbc_micro": "BBC Micro",
        "bbc-micro": "BBC Micro",
        "commodore64": "Commodore 64",
        "commodore_64": "Commodore 64",
        "zxspectrum": "ZX Spectrum",
        "zx_spectrum": "ZX Spectrum",
        "zx-spectrum": "ZX Spectrum",
        "zxspectrum128": "ZX Spectrum 128",
        "playstation1": "PlayStation 1",
        "playstation_1": "PlayStation 1",
        "ps1": "PlayStation 1",
        "playstation2": "PlayStation 2",
        "playstation_2": "PlayStation 2",
        "ps2": "PlayStation 2",
        "n64": "Nintendo 64",
        "nintendo64": "Nintendo 64",
        "snes": "Super Nintendo",
        "supernintendo": "Super Nintendo",
        "nes": "Nintendo Entertainment System",
        "gba": "Game Boy Advance",
        "gameboyadvance": "Game Boy Advance",
        "segagenesis": "Sega Genesis",
        "segamegadrive": "Sega Mega Drive"
    }
    
    # RetroArch buildbot URLs
    BUILDBOT_BASE = "https://buildbot.libretro.com/nightly"
    
    def __init__(self, base_dir: Path): #vers 2
        """Initialize core downloader"""
        self.base_dir = Path(base_dir)
        self.cores_dir = self.base_dir / "cores"
        self.cores_dir.mkdir(parents=True, exist_ok=True)
        
    @staticmethod
    def normalize_platform_name(name: str) -> str: #vers 1
        """Normalize platform name for fuzzy matching
        
        Handles: "AtariST", "Atari ST", "Atari_ST", "atari-st" all → "Atari ST"
        
        Args:
            name: Platform name from folder
            
        Returns:
            Normalized platform name from database
        """
        # First try exact match
        if name in CoreDownloader.CORE_DATABASE:
            return name
            
        # Try normalized version (lowercase, no spaces/underscores/hyphens)
        normalized = re.sub(r'[\s_-]', '', name.lower())
        
        if normalized in CoreDownloader.PLATFORM_ALIASES:
            return CoreDownloader.PLATFORM_ALIASES[normalized]
            
        # Return original if no match (will be marked as unknown)
        return name
        
    def get_available_cores(self) -> Dict[str, List[str]]: #vers 1
        """Get all available cores organized by platform"""
        return {
            platform: info["cores"] 
            for platform, info in self.CORE_DATABASE.items()
        }
        
    def get_cores_for_platform(self, platform: str) -> List[str]: #vers 2
        """Get list of cores for a specific platform with fuzzy matching
        
        Args:
            platform: Platform name (will be normalized)
            
        Returns:
            List of core names
        """
        normalized = self.normalize_platform_name(platform)
        if normalized in self.CORE_DATABASE:
            return self.CORE_DATABASE[normalized]["cores"]
        return []
        
    def get_core_info(self, platform: str) -> Optional[Dict]: #vers 2
        """Get detailed info about platform cores with fuzzy matching
        
        Args:
            platform: Platform name (will be normalized)
            
        Returns:
            Platform info dict or None
        """
        normalized = self.normalize_platform_name(platform)
        return self.CORE_DATABASE.get(normalized)
        
    def get_installed_cores(self) -> List[str]: #vers 1
        """Get list of installed cores"""
        if not self.cores_dir.exists():
            return []
            
        installed = []
        for file in self.cores_dir.iterdir():
            if file.suffix in ['.so', '.dll', '.dylib']:
                installed.append(file.stem.replace('_libretro', ''))
        return installed
    
    def scan_available_cores(self) -> Dict[str, List[str]]: #vers 1
        """Scan cores directory and build dynamic database of available cores"""
        if not self.cores_dir.exists():
            return {}
        
        # Get all installed cores
        installed_cores = self.get_installed_cores()
        
        # Build reverse mapping: core_name -> [platforms that use it]
        core_to_platforms = {}
        for platform, info in self.CORE_DATABASE.items():
            for core_name in info.get("cores", []):
                if core_name not in core_to_platforms:
                    core_to_platforms[core_name] = []
                if platform not in core_to_platforms[core_name]:
                    core_to_platforms[core_name].append(platform)
        
        # Build dynamic database with only available cores
        available_database = {}
        for core_name in installed_cores:
            if core_name in core_to_platforms:
                for platform in core_to_platforms[core_name]:
                    if platform not in available_database:
                        available_database[platform] = {
                            "cores": [],
                            "extensions": self.CORE_DATABASE[platform]["extensions"],
                            "bios_required": self.CORE_DATABASE[platform]["bios_required"],
                            "bios_files": self.CORE_DATABASE[platform]["bios_files"]
                        }
                    if core_name not in available_database[platform]["cores"]:
                        available_database[platform]["cores"].append(core_name)
        
        return available_database
    
    def get_dynamic_core_database(self) -> Dict:
        """Get core database built from actually available cores"""
        available_database = self.scan_available_cores()
        
        # Add any missing platforms that have no available cores but exist in the master database
        for platform, info in self.CORE_DATABASE.items():
            if platform not in available_database:
                available_database[platform] = {
                    "cores": [],
                    "extensions": info["extensions"],
                    "bios_required": info["bios_required"],
                    "bios_files": info["bios_files"]
                }
        
        return available_database
    
    def get_dynamic_core_database_with_aliases(self) -> Dict:
        """Get core database with both main platforms and aliases for fuzzy matching"""
        # Get the base dynamic database
        base_database = self.get_dynamic_core_database()
        
        # Create a new database that includes both main platforms and aliases
        full_database = {}
        
        # Add all main platforms
        for platform, info in base_database.items():
            full_database[platform] = info
            
        # Add aliases as separate entries (mapping to same core info)
        for alias, main_platform in self.PLATFORM_ALIASES.items():
            if main_platform in base_database:
                full_database[alias] = base_database[main_platform]
        
        return full_database
        
    def download_core(self, core_name: str, platform: str = "linux") -> bool: #vers 1
        """Download a specific core
        
        Args:
            core_name: Name of the core (e.g. 'snes9x')
            platform: Platform architecture (linux/windows/macos)
            
        Returns:
            True if download successful
        """
        url = self._get_core_url(core_name, platform)
        if not url:
            return False
            
        core_file = self.cores_dir / f"{core_name}_libretro.so"
        return self._download_file(url, core_file)
        
    def _get_core_url(self, core_name: str, platform: str) -> Optional[str]: #vers 1
        """Construct download URL for core"""
        platform_map = {
            "linux": "x86_64",
            "windows": "windows",
            "macos": "apple/osx"
        }
        
        arch = platform_map.get(platform)
        if not arch:
            return None
            
        return f"{self.BUILDBOT_BASE}/{arch}/latest/{core_name}_libretro.so.zip"
        
    def _download_file(self, url: str, dest: Path) -> bool: #vers 1
        """Download file from URL"""
        try:
            print(f"Downloading: {url}")
            urllib.request.urlretrieve(url, dest)
            print(f"✓ Saved to: {dest}")
            return True
        except Exception as e:
            print(f"✗ Download failed: {e}")
            return False
            
    def _load_core_database(self) -> Dict: #vers 1
        """Load core database from JSON file (if exists)"""
        db_file = self.base_dir / "config" / "core_database.json"
        
        if db_file.exists():
            try:
                with open(db_file) as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading core database: {e}")
                
        return self.CORE_DATABASE


def create_directory_structure(base_dir: Path): #vers 1
    """Create standard directory structure for emulator"""
    directories = {
        'cores': 'RetroArch core files',
        'roms': 'ROM files organized by system',
        'bios': 'BIOS files organized by system', 
        'saves': 'Save states and memory cards',
        'config': 'Configuration files',
        'playlists': 'Game playlists',
        'screenshots': 'Screenshots',
        'system': 'System files'
    }
    
    print(f"Creating directory structure in: {base_dir}")
    
    for dir_name, description in directories.items():
        dir_path = base_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_name}/ - {description}")
        
    print(f"\n✓ Directory structure created!")
