#!/usr/bin/env python3
#this belongs in apps/methods/core_downloader.py - Version: 2
# X-Seti - November30 2025 - Multi-Emulator Launcher - Core Downloader

"""
Core Downloader
Handles downloading and managing RetroArch cores dynamically
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import requests
import subprocess
from .system_core_scanner import SystemCoreScanner

##Methods list -
# __init__
# download_core
# get_available_cores
# get_core_download_url
# get_core_info
# get_installed_cores
# update_core_database

class CoreDownloader: #vers 2
    """Manages downloading and updating RetroArch cores"""
    
    # RetroArch core download URLs
    CORE_LIST_URL = "https://buildbot.libretro.com/assets/cores/"
    CORE_DOWNLOAD_BASE_URL = "https://buildbot.libretro.com/assets/cores/"
    
    # Platform to core mapping for download suggestions
    PLATFORM_CORE_MAPPING = {
        "Nintendo Entertainment System": ["fceumm", "nestopia"],
        "Super Nintendo": ["snes9x", "bsnes"],
        "Game Boy": ["gambatte", "mgba"],
        "Game Boy Advance": ["mgba", "vba-next"],
        "Genesis": ["genesis-plus-gx", "picodrive"],
        "Sega CD": ["genesis-plus-gx", "picodrive"],
        "32X": ["picodrive"],
        "Master System": ["genesis-plus-gx", "picodrive"],
        "PlayStation 1": ["pcsx_rearmed", "mednafen_psx_hw"],
        "PlayStation 2": ["pcsx2", "play"],
        "Nintendo 64": ["mupen64plus-next", "parallel-n64"],
        "GameCube": ["dolphin"],
        "Wii": ["dolphin"],
        "Game Boy Color": ["gambatte"],
        "Virtual Boy": ["mednafen_vb"],
        "Atari 2600": ["stella"],
        "Atari 5200": ["atari800"],
        "Atari 7800": ["prosystem"],
        "Atari ST": ["hatari"],
        "Atari 800": ["atari800"],
        "Commodore 64": ["vice_x64"],
        "C64": ["vice_x64"],
        "Amiga": ["puae"],
        "Amstrad CPC": ["cap32"],
        "ZX Spectrum": ["fuse"],
        "MSX": ["fmsx"],
        "MSX2": ["fmsx"],
        "PC Engine": ["mednafen_pce_fast", "mednafen_supergrafx"],
        "TurboGrafx-16": ["mednafen_pce_fast"],
        "TurboGrafx-CD": ["mednafen_pce_fast"],
        "Neo Geo": ["fbneo", "mame"],
        "Neo Geo Pocket": ["mednafen_ngp"],
        "WonderSwan": ["mednafen_wswan"],
        "Arcade": ["fbneo", "mame"],
        "MS-DOS": ["dosbox_pure"],
        "3DO": ["opera"],
        "Dreamcast": ["flycast"],
        "Nintendo DS": ["melonds", "desmume"],
        "Game Gear": ["genesis-plus-gx"],
        "SG-1000": ["genesis-plus-gx"],
        "ColecoVision": ["bluemsx"],
        "Intellivision": ["freeintv"],
        "Vectrex": ["vecx"],
        "Odyssey 2": ["o2em"],
        "PC-88": ["quasi88"],
        "PC-98": ["np2kai"],
        "PC-FX": ["mednafen_supergrafx"],
        "Atari Lynx": ["handy", "mednafen_lynx"],
        "Neo Geo CD": ["neocd"],
        "WonderSwan Color": ["mednafen_wswan"],
        "Super Cassette Vision": ["emuscv"],
        "SC-3000": ["genesis-plus-gx"],
        "TI-99/4A": ["x16-emulator", "mame"],
        "Uzebox": ["prboom"],
        "X68000": ["px68k"],
        "Z-Machine": ["jzintext"],
        "ZX81": ["81"],
        "32X": ["picodrive"],
        "Astrocade": ["bnes"],
        "Channel F": ["freechaf"],
        "Intellivision": ["freeintv"],
        "Magnavox Odyssey2": ["o2em"],
        "SG-1000": ["genesis-plus-gx"],
        "WonderSwan": ["mednafen_wswan"],
        "WonderSwan Color": ["mednafen_wswan"],
        "ColecoVision": ["bluemsx"],
        "Vectrex": ["vecx"],
        "MSX": ["fmsx"],
        "MSX2": ["fmsx"],
        "PC Engine": ["mednafen_pce_fast"],
        "PC Engine CD": ["mednafen_pce_fast"],
        "SuperGrafx": ["mednafen_supergrafx"],
        "Atari 5200": ["atari800"],
        "Atari 7800": ["prosystem"],
        "Atari Jaguar": ["virtualjaguar"],
        "Atari Lynx": ["handy", "mednafen_lynx"],
        "Atari ST": ["hatari"],
        "BBC Micro": ["mame"],
        "Dragon 32-64": ["xroar"],
        "Oric Atmos": ["mame"],
        "TRS-80": ["mame"],
        "Fujitsu FM-7": ["mame"],
        "Sam Coupe": ["mame"],
        "Z81-Spec256": ["fuse"],
        "Plus4": ["vice_xplus4"],
    }
    
    def __init__(self, cores_dir: Path = None): #vers 1
        """Initialize core downloader
        
        Args:
            cores_dir: Directory to store cores (defaults to ./cores)
        """
        self.cores_dir = Path(cores_dir) if cores_dir else Path("./cores")
        self.cores_dir.mkdir(parents=True, exist_ok=True)
        self.system_core_scanner = SystemCoreScanner(self.cores_dir)
        
    def get_available_cores(self) -> Dict[str, str]: #vers 1
        """Get list of available cores from RetroArch
        
        Returns:
            Dict of core_name -> description
        """
        # For now, return a static list based on common cores
        # In a real implementation, this would fetch from RetroArch API
        available_cores = {
            "fceumm": "Nintendo Entertainment System",
            "snes9x": "Super Nintendo Entertainment System",
            "gambatte": "Game Boy / Game Boy Color",
            "mgba": "Game Boy Advance",
            "genesis-plus-gx": "Sega Genesis / Master System / Game Gear",
            "pcsx_rearmed": "PlayStation 1",
            "mupen64plus-next": "Nintendo 64",
            "dolphin": "GameCube / Wii",
            "stella": "Atari 2600",
            "atari800": "Atari 5200 / 800 / XL / XE",
            "prosystem": "Atari 7800",
            "hatari": "Atari ST",
            "vice_x64": "Commodore 64",
            "puae": "Commodore Amiga",
            "cap32": "Amstrad CPC",
            "fuse": "ZX Spectrum",
            "fmsx": "MSX / MSX2",
            "mednafen_pce_fast": "PC Engine / TurboGrafx-16",
            "fbneo": "FinalBurn Neo (Arcade)",
            "mame": "MAME (Arcade)",
            "dosbox_pure": "MS-DOS",
            "bluemsx": "MSX / MSX2 / SG-1000",
            "mednafen_supergrafx": "SuperGrafx",
            "mednafen_lynx": "Atari Lynx",
            "mednafen_ngp": "Neo Geo Pocket",
            "mednafen_pce": "PC Engine",
            "mednafen_wswan": "WonderSwan",
            "mednafen_vb": "Virtual Boy",
            "mednafen_psx_hw": "PlayStation 1 (Hardware Renderer)",
            "pcsx2": "PlayStation 2",
            "melonds": "Nintendo DS",
            "desmume": "Nintendo DS",
            "flycast": "Sega Dreamcast",
            "opera": "3DO Interactive Multiplayer",
            "freeintv": "Intellivision",
            "freechaf": "Fairchild Channel F",
            "o2em": "Magnavox Odyssey2 / Philips Videopac+",
            "vecx": "Vectrex",
            "quasi88": "PC-8801",
            "np2kai": "PC-9801",
            "x16-emulator": "Commander X16",
            "xroar": "Dragon 32/64, CoCo",
            "vice_xplus4": "Commodore Plus/4",
        }
        
        return available_cores
    
    def get_installed_cores(self) -> List[str]: #vers 1
        """Get list of installed cores
        
        Returns:
            List of installed core names
        """
        return self.system_core_scanner.get_installed_cores()
    
    def get_core_info(self, core_name: str) -> Dict: #vers 1
        """Get information about a specific core
        
        Args:
            core_name: Name of the core
            
        Returns:
            Dict with core information
        """
        available_cores = self.get_available_cores()
        
        platforms = []
        for platform, cores in self.PLATFORM_CORE_MAPPING.items():
            if core_name in cores:
                platforms.append(platform)
        
        return {
            "name": core_name,
            "description": available_cores.get(core_name, f"LibRetro core for {core_name}"),
            "supported_platforms": platforms,
            "installed": core_name in self.system_core_scanner.get_installed_cores(),
            "download_url": self.get_core_download_url(core_name)
        }
    
    def get_core_download_url(self, core_name: str) -> Optional[str]:
        """Get download URL for a core (placeholder implementation)
        
        Args:
            core_name: Name of the core
            
        Returns:
            Download URL or None if not available
        """
        # This would normally fetch from RetroArch's buildbot
        # For now, return None as a real implementation would require
        # architecture-specific downloads
        return f"{self.CORE_DOWNLOAD_BASE_URL}{core_name}_libretro.so"
    
    def download_core(self, core_name: str) -> bool:
        """Download a core (placeholder implementation)
        
        Args:
            core_name: Name of the core to download
            
        Returns:
            True if download was successful
        """
        try:
            # Get the download URL
            download_url = self.get_core_download_url(core_name)
            if not download_url:
                print(f"Could not find download URL for core: {core_name}")
                return False
            
            # For now, this is a placeholder - in a real implementation,
            # we would download the appropriate core for the user's architecture
            print(f"Would download core from: {download_url}")
            print(f"Core would be saved to: {self.cores_dir}/{core_name}_libretro.so")
            
            # In a real implementation, you would use requests to download
            # the file and save it to the cores directory
            return True
            
        except Exception as e:
            print(f"Error downloading core {core_name}: {e}")
            return False
    
    def update_core_database(self, platform_config: Dict) -> Dict:
        """Update platform configuration with available cores
        
        Args:
            platform_config: Original platform configuration
            
        Returns:
            Updated platform configuration
        """
        # Make a copy of the original config
        updated_config = platform_config.copy()
        
        # Get the platform name
        platform_name = updated_config.get("name", "")
        
        # Find available cores for this platform
        available_cores = self.get_available_cores()
        available_platform_cores = []
        
        # Check if this platform has specific core mappings
        if platform_name in self.PLATFORM_CORE_MAPPING:
            for core_candidate in self.PLATFORM_CORE_MAPPING[platform_name]:
                if core_candidate in available_cores:
                    available_platform_cores.append(core_candidate)
        
        # Also check existing cores in the config
        existing_cores = updated_config.get("cores", [])
        for core_candidate in existing_cores:
            if core_candidate in available_cores:
                if core_candidate not in available_platform_cores:
                    available_platform_cores.append(core_candidate)
        
        # Update the cores list with only available ones
        updated_config["available_cores"] = available_platform_cores
        updated_config["core_download_suggestions"] = available_platform_cores
        
        return updated_config

def test_core_downloader():
    """Test function for Core Downloader"""
    print("Testing Core Downloader...")
    
    # Create core downloader
    downloader = CoreDownloader()
    
    # Test getting available cores
    available_cores = downloader.get_available_cores()
    print(f"\nAvailable cores: {len(available_cores)} found")
    print(f"First 10 cores: {list(available_cores.keys())[:10]}")
    
    # Test getting core info
    test_cores = ["stella", "puae", "fuse", "fmsx"]
    for core in test_cores:
        info = downloader.get_core_info(core)
        print(f"\n{core}: {info['description']}")
        print(f"  Supported platforms: {info['supported_platforms']}")
        print(f"  Installed: {info['installed']}")
    
    # Test updating a platform config
    test_config = {
        "name": "Atari 2600",
        "cores": ["stella", "stella2014", "other_core"],
        "extensions": [".a26", ".bin"]
    }
    
    updated_config = downloader.update_core_database(test_config)
    print(f"\nUpdated config for {test_config['name']}:")
    print(f"  Available cores: {updated_config['available_cores']}")
    print(f"  Download suggestions: {updated_config['core_download_suggestions']}")

if __name__ == "__main__":
    test_core_downloader()