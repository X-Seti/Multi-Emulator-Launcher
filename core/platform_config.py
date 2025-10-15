# X-Seti - October15 2025 - Multi-Emulator Launcher - Platform Configuration Manager
# This belongs in core/platform_config.py - Version: 1
"""
Platform Configuration Manager - Handles platform-specific settings, cores, and BIOS requirements.
"""

##Methods list -
# get_core_path
# get_default_platforms
# get_platform
# is_valid_extension
# load_platforms
# verify_bios

import json
import os
from pathlib import Path


class PlatformManager: #vers 1
    def __init__(self, config_dir): #vers 1
        self.config_dir = Path(config_dir)
        self.platforms = self.load_platforms()
    
    def get_core_path(self, platform_name, core_base_path): #vers 1
        """Get full path to core for a platform"""
        platform = self.get_platform(platform_name)
        if not platform:
            return None
        
        core_file = platform['core']
        return Path(core_base_path) / core_file
    
    def get_default_platforms(self): #vers 1
        """Default platform configurations"""
        return {
            "Acorn Electron": {
                "core": "mame_libretro.so",
                "extensions": [".adf", ".uef"],
                "zip_support": "extract",
                "cache_extracted": True,
                "bios_required": False,
                "bios_files": {}
            },
            "Amiga": {
                "core": "puae_libretro.so",
                "extensions": [".adf", ".ipf", ".dms", ".hdf", ".hdz", ".zip"],
                "zip_support": "extract",
                "cache_extracted": True,
                "bios_required": True,
                "bios_files": {
                    "kick34005.A500": "Kickstart 3.1 ROM",
                    "kick40068.A1200": "Kickstart 3.1 ROM (A1200)"
                }
            },
            "Amstrad CPC": {
                "core": "cap32_libretro.so",
                "extensions": [".dsk", ".sna", ".cdt", ".zip"],
                "zip_support": "extract",
                "cache_extracted": True,
                "bios_required": False,
                "bios_files": {}
            },
            "Atari 2600": {
                "core": "stella_libretro.so",
                "extensions": [".bin", ".a26", ".zip"],
                "zip_support": "native",
                "cache_extracted": False,
                "bios_required": False,
                "bios_files": {}
            },
            "Atari 800": {
                "core": "atari800_libretro.so",
                "extensions": [".atr", ".xex", ".xfd", ".dcm", ".zip"],
                "zip_support": "extract",
                "cache_extracted": True,
                "bios_required": True,
                "bios_files": {
                    "ATARIXL.ROM": "Atari XL/XE OS",
                    "ATARIBAS.ROM": "Atari BASIC"
                }
            },
            "Atari-8-bit": {
                "core": "atari800_libretro.so",
                "extensions": [".atr", ".xex", ".xfd", ".dcm", ".zip"],
                "zip_support": "extract",
                "cache_extracted": True,
                "bios_required": True,
                "bios_files": {
                    "ATARIXL.ROM": "Atari XL/XE OS",
                    "ATARIBAS.ROM": "Atari BASIC"
                }
            },
            "Atari ST": {
                "core": "hatari_libretro.so",
                "extensions": [".st", ".stx", ".msa", ".dim", ".zip"],
                "zip_support": "extract",
                "cache_extracted": True,
                "bios_required": True,
                "bios_files": {
                    "tos.img": "TOS System ROM"
                }
            },
            "BBC Micro": {
                "core": "mame_libretro.so",
                "extensions": [".ssd", ".dsd", ".uef", ".zip"],
                "zip_support": "extract",
                "cache_extracted": True,
                "bios_required": False,
                "bios_files": {}
            },
            "Commodore 64": {
                "core": "vice_x64_libretro.so",
                "extensions": [".d64", ".t64", ".prg", ".tap", ".zip"],
                "zip_support": "extract",
                "cache_extracted": True,
                "bios_required": False,
                "bios_files": {}
            },
            "MS-DOS": {
                "core": "dosbox_pure_libretro.so",
                "extensions": [".zip", ".dosz"],
                "zip_support": "native",
                "cache_extracted": False,
                "bios_required": False,
                "bios_files": {}
            },
            "ZX Spectrum": {
                "core": "fuse_libretro.so",
                "extensions": [".tzx", ".tap", ".z80", ".sna", ".szx", ".zip"],
                "zip_support": "extract",
                "cache_extracted": True,
                "bios_required": False,
                "bios_files": {}
            }
        }
    
    def get_platform(self, platform_name): #vers 1
        """Get configuration for a specific platform"""
        return self.platforms.get(platform_name)
    
    def is_valid_extension(self, platform_name, filename): #vers 1
        """Check if a file has a valid extension for the platform"""
        platform = self.get_platform(platform_name)
        if not platform:
            return False
        
        ext = os.path.splitext(filename.lower())[1]
        return ext in platform['extensions']
    
    def load_platforms(self): #vers 1
        """Load or create platform configurations"""
        platforms_file = self.config_dir / 'platforms.json'
        
        if platforms_file.exists():
            with open(platforms_file, 'r') as f:
                return json.load(f)
        else:
            default_platforms = self.get_default_platforms()
            
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(platforms_file, 'w') as f:
                json.dump(default_platforms, f, indent=2)
            
            return default_platforms
    
    def verify_bios(self, platform_name, bios_path): #vers 1
        """Check if all required BIOS files exist for a platform"""
        platform = self.get_platform(platform_name)
        
        if not platform or not platform.get('bios_required'):
            return True, "No BIOS required"
        
        platform_bios_dir = Path(bios_path) / platform_name
        
        if not platform_bios_dir.exists():
            return False, f"BIOS directory not found: {platform_bios_dir}"
        
        missing_files = []
        for bios_file, description in platform['bios_files'].items():
            bios_file_path = platform_bios_dir / bios_file
            if not bios_file_path.exists():
                missing_files.append(f"{bios_file} ({description})")
        
        if missing_files:
            return False, f"Missing BIOS files:\n  - " + "\n  - ".join(missing_files)
        
        return True, "All BIOS files present"
