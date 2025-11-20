#!/usr/bin/env python3
#this belongs in apps/core/core_downloader.py - Version: 1
# X-Seti - November19 2025 - Multi-Emulator Launcher - Core Downloader

"""
RetroArch Core Downloader
Downloads and manages libretro cores for different platforms
"""

import os
import urllib.request
import json
from pathlib import Path
from typing import Dict, List, Optional

##Methods list -
# __init__
# download_core
# get_available_cores
# get_core_info
# get_cores_for_platform
# get_installed_cores
# _download_file
# _get_core_url
# _load_core_database

##class CoreDownloader -

class CoreDownloader: #vers 1
    """Manages downloading and organizing RetroArch cores"""
    
    # Core database with platform mappings
    CORE_DATABASE = {
        "PlayStation 2": {
            "cores": ["pcsx2_libretro"],
            "extensions": [".iso", ".bin", ".cue", ".img", ".mdf"],
            "bios_required": True,
            "bios_files": ["SCPH10000.bin", "SCPH39001.bin", "SCPH70012.bin"]
        },
        "PlayStation 3": {
            "cores": ["rpcs3"],
            "extensions": [".iso", ".pkg"],
            "bios_required": True,
            "bios_files": ["PS3UPDAT.PUP"]
        },
        "PlayStation 1": {
            "cores": ["pcsx_rearmed", "beetle_psx", "beetle_psx_hw"],
            "extensions": [".cue", ".bin", ".img", ".iso", ".chd", ".pbp"],
            "bios_required": True,
            "bios_files": ["scph1001.bin", "scph5501.bin", "scph7001.bin"]
        },
        "Nintendo Switch": {
            "cores": ["yuzu"],
            "extensions": [".nsp", ".xci"],
            "bios_required": True,
            "bios_files": ["prod.keys", "title.keys"]
        },
        "Nintendo 64": {
            "cores": ["mupen64plus_next", "parallel_n64"],
            "extensions": [".n64", ".v64", ".z64"],
            "bios_required": False,
            "bios_files": []
        },
        "Super Nintendo": {
            "cores": ["snes9x", "bsnes", "bsnes_hd_beta"],
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
        "Game Boy Advance": {
            "cores": ["mgba", "vba_next", "vba_m"],
            "extensions": [".gba", ".gb", ".gbc"],
            "bios_required": False,
            "bios_files": ["gba_bios.bin"]
        },
        "Nintendo DS": {
            "cores": ["desmume", "melonds"],
            "extensions": [".nds"],
            "bios_required": True,
            "bios_files": ["bios7.bin", "bios9.bin", "firmware.bin"]
        },
        "Sega Genesis": {
            "cores": ["genesis_plus_gx", "picodrive", "blastem"],
            "extensions": [".md", ".smd", ".gen", ".bin"],
            "bios_required": False,
            "bios_files": []
        },
        "Sega Saturn": {
            "cores": ["yabause", "kronos", "beetle_saturn"],
            "extensions": [".cue", ".bin", ".iso", ".mds"],
            "bios_required": True,
            "bios_files": ["saturn_bios.bin", "sega_101.bin"]
        },
        "Sega Dreamcast": {
            "cores": ["flycast", "redream"],
            "extensions": [".cdi", ".gdi", ".chd"],
            "bios_required": True,
            "bios_files": ["dc_boot.bin", "dc_flash.bin"]
        },
        "Xbox 360": {
            "cores": ["xenia"],
            "extensions": [".iso", ".xex"],
            "bios_required": False,
            "bios_files": []
        },
        "Arcade": {
            "cores": ["mame", "mame2003_plus", "fbneo", "fbalpha2012"],
            "extensions": [".zip"],
            "bios_required": True,
            "bios_files": ["neogeo.zip", "qsound.zip"]
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
        }
    }
    
    # RetroArch buildbot URLs
    BUILDBOT_BASE = "https://buildbot.libretro.com/nightly"
    
    def __init__(self, base_dir: Path): #vers 1
        """Initialize core downloader"""
        self.base_dir = Path(base_dir)
        self.cores_dir = self.base_dir / "cores"
        self.cores_dir.mkdir(parents=True, exist_ok=True)
        
    def get_available_cores(self) -> Dict[str, List[str]]: #vers 1
        """Get all available cores organized by platform"""
        return {
            platform: info["cores"] 
            for platform, info in self.CORE_DATABASE.items()
        }
        
    def get_cores_for_platform(self, platform: str) -> List[str]: #vers 1
        """Get list of cores for a specific platform"""
        if platform in self.CORE_DATABASE:
            return self.CORE_DATABASE[platform]["cores"]
        return []
        
    def get_core_info(self, platform: str) -> Optional[Dict]: #vers 1
        """Get detailed info about platform cores"""
        return self.CORE_DATABASE.get(platform)
        
    def get_installed_cores(self) -> List[str]: #vers 1
        """Get list of installed cores"""
        if not self.cores_dir.exists():
            return []
            
        installed = []
        for file in self.cores_dir.iterdir():
            if file.suffix in ['.so', '.dll', '.dylib']:
                installed.append(file.stem.replace('_libretro', ''))
        return installed
        
    def download_core(self, core_name: str, platform: str = "linux") -> bool: #vers 1
        """Download a specific core
        
        Args:
            core_name: Name of the core (e.g. 'pcsx_rearmed')
            platform: Target platform ('linux', 'windows', 'macos')
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            url = self._get_core_url(core_name, platform)
            if not url:
                print(f"Could not determine URL for core: {core_name}")
                return False
                
            # Determine file extension based on platform
            if platform == "windows":
                ext = ".dll"
            elif platform == "macos":
                ext = ".dylib"
            else:
                ext = ".so"
                
            output_file = self.cores_dir / f"{core_name}_libretro{ext}"
            
            print(f"Downloading {core_name} from {url}")
            success = self._download_file(url, output_file)
            
            if success:
                print(f"✓ Downloaded: {output_file.name}")
            else:
                print(f"✗ Failed to download: {core_name}")
                
            return success
            
        except Exception as e:
            print(f"Error downloading {core_name}: {e}")
            return False
            
    def _get_core_url(self, core_name: str, platform: str) -> Optional[str]: #vers 1
        """Construct download URL for a core"""
        # Platform-specific paths
        platform_paths = {
            "linux": "linux/x86_64/latest",
            "windows": "windows/x86_64/latest",
            "macos": "apple/osx/x86_64/latest"
        }
        
        path = platform_paths.get(platform, platform_paths["linux"])
        
        # File extension based on platform
        if platform == "windows":
            ext = ".dll.zip"
        elif platform == "macos":
            ext = ".dylib.zip"
        else:
            ext = ".so.zip"
            
        return f"{self.BUILDBOT_BASE}/{path}/{core_name}_libretro{ext}"
        
    def _download_file(self, url: str, output_path: Path) -> bool: #vers 1
        """Download file from URL"""
        try:
            urllib.request.urlretrieve(url, output_path)
            
            # If it's a zip, extract it
            if output_path.suffix == '.zip':
                import zipfile
                with zipfile.ZipFile(output_path, 'r') as zip_ref:
                    zip_ref.extractall(output_path.parent)
                output_path.unlink()  # Remove zip file
                
            return True
            
        except Exception as e:
            print(f"Download error: {e}")
            return False
            
    def _load_core_database(self) -> Dict: #vers 1
        """Load core database from file or use built-in"""
        db_file = self.base_dir / "core_database.json"
        
        if db_file.exists():
            try:
                with open(db_file, 'r') as f:
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
        
    # Create system-specific ROM folders
    systems = [
        "PlayStation 2", "PlayStation 1", "PSP", 
        "Nintendo Switch", "Nintendo 64", "Super Nintendo",
        "Nintendo Entertainment System", "Game Boy Advance",
        "Sega Genesis", "Arcade"
    ]
    
    roms_dir = base_dir / "roms"
    bios_dir = base_dir / "bios"
    
    for system in systems:
        (roms_dir / system).mkdir(exist_ok=True)
        (bios_dir / system).mkdir(exist_ok=True)
        
    print(f"\n✓ Directory structure created!")


# CLI usage
if __name__ == "__main__":
    import sys
    
    base_dir = Path.cwd()
    
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        # Initialize directory structure
        create_directory_structure(base_dir)
        
    elif len(sys.argv) > 1 and sys.argv[1] == "list":
        # List available cores
        downloader = CoreDownloader(base_dir)
        cores = downloader.get_available_cores()
        
        print("\nAvailable Cores by Platform:")
        print("=" * 60)
        for platform, core_list in sorted(cores.items()):
            print(f"\n{platform}:")
            for core in core_list:
                print(f"  - {core}")
                
    elif len(sys.argv) > 2 and sys.argv[1] == "download":
        # Download specific core
        core_name = sys.argv[2]
        platform = sys.argv[3] if len(sys.argv) > 3 else "linux"
        
        downloader = CoreDownloader(base_dir)
        downloader.download_core(core_name, platform)
        
    elif len(sys.argv) > 1 and sys.argv[1] == "installed":
        # Show installed cores
        downloader = CoreDownloader(base_dir)
        installed = downloader.get_installed_cores()
        
        print("\nInstalled Cores:")
        print("=" * 60)
        for core in sorted(installed):
            print(f"  ✓ {core}")
        print(f"\nTotal: {len(installed)} cores")
        
    else:
        print("Multi-Emulator Launcher - Core Downloader")
        print("=" * 60)
        print("\nUsage:")
        print("  python core_downloader.py init                  - Create directory structure")
        print("  python core_downloader.py list                  - List available cores")
        print("  python core_downloader.py download <core> [os]  - Download core")
        print("  python core_downloader.py installed             - Show installed cores")
        print("\nExamples:")
        print("  python core_downloader.py init")
        print("  python core_downloader.py download pcsx_rearmed linux")
        print("  python core_downloader.py download snes9x windows")
