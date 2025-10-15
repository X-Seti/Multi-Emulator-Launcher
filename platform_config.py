"""
Platform Configuration Manager
Handles platform-specific settings, cores, and BIOS requirements
"""

import json
import os
from pathlib import Path


class PlatformManager:
    def __init__(self, config_dir):
        self.config_dir = Path(config_dir)
        self.platforms = self.load_platforms()
    
    def load_platforms(self):
        """Load or create platform configurations"""
        platforms_file = self.config_dir / 'platforms.json'
        
        if platforms_file.exists():
            with open(platforms_file, 'r') as f:
                return json.load(f)
        else:
            # Create default platform configurations
            default_platforms = self.get_default_platforms()
            
            # Save to file
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(platforms_file, 'w') as f:
                json.dump(default_platforms, f, indent=2)
            
            return default_platforms
    
    def get_default_platforms(self):
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
                    "kick13.rom": "Kickstart v1.3 (A500,A1000,A2000)",
                    "kick20.rom": "Kickstart v2.0 (A500+)",
                    "kick31.rom": "Kickstart v3.1 (A1200,A4000)"
                },
                "default_settings": {
                    "model": "A1200",
                    "chipset": "AGA",
                    "cpu_speed": "14MHz"
                }
            },
            "Amstrad 464": {
                "core": "cap32_libretro.so",
                "extensions": [".cdt", ".dsk", ".zip"],
                "zip_support": "extract",
                "cache_extracted": True,
                "bios_required": False,
                "bios_files": {}
            },
            "Amstrad 6128": {
                "core": "cap32_libretro.so",
                "extensions": [".dsk", ".zip"],
                "zip_support": "extract",
                "cache_extracted": True,
                "bios_required": False,
                "bios_files": {}
            },
            "Amstrad CPC": {
                "core": "cap32_libretro.so",
                "extensions": [".cdt", ".dsk", ".zip"],
                "zip_support": "extract",
                "cache_extracted": True,
                "bios_required": False,
                "bios_files": {}
            },
            "Apple-II": {
                "core": "mame_libretro.so",
                "extensions": [".do", ".po", ".nib", ".zip"],
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
            }
        }
    
    def get_platform(self, platform_name):
        """Get configuration for a specific platform"""
        return self.platforms.get(platform_name)
    
    def verify_bios(self, platform_name, bios_path):
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
    
    def get_core_path(self, platform_name, core_base_path):
        """Get full path to core for a platform"""
        platform = self.get_platform(platform_name)
        if not platform:
            return None
        
        core_file = platform['core']
        return Path(core_base_path) / core_file
    
    def is_valid_extension(self, platform_name, filename):
        """Check if a file has a valid extension for the platform"""
        platform = self.get_platform(platform_name)
        if not platform:
            return False
        
        ext = os.path.splitext(filename.lower())[1]
        return ext in platform['extensions']
