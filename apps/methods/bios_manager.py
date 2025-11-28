#!/usr/bin/env python3
#this belongs in apps/methods/bios_manager.py - Version: 1
# X-Seti - November28 2025 - Multi-Emulator Launcher - BIOS Manager

"""
BIOS Manager
Handles automatic BIOS detection and management for different platforms
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set
import json
import hashlib

##Methods list -
# __init__
# find_bios_files
# get_platform_bios_requirements
# is_platform_bios_complete
# get_missing_bios
# get_bios_paths
# get_platform_bios_info
# scan_bios_directory

class BiosManager: #vers 1
    """Manages BIOS files for different platforms"""
    
    # Common BIOS directory paths
    BIOS_PATHS = [
        Path.home() / ".config/retroarch/bios",
        Path.home() / ".local/share/libretro/bios",
        Path("/usr/share/libretro/bios"),
        Path("/usr/lib/libretro/bios"),
        Path("./bios"),
        Path("./ROMS/bios"),
    ]
    
    # Platform-specific BIOS requirements
    PLATFORM_BIOS_REQUIREMENTS = {
        "Amiga": {
            "required": ["kick34005.A500", "kick40068.A1200"],
            "alternative_names": {
                "kick34005.A500": ["kick34005.A500", "kick.rom", "kick34005.rom", "A500_ROM", "kickstart.rom"],
                "kick40068.A1200": ["kick40068.A1200", "kick1200.rom", "A1200_ROM"]
            }
        },
        "Atari 5200": {
            "required": ["5200.rom"],
            "alternative_names": {
                "5200.rom": ["5200.rom", "5200_cart.rom", "atari5200.rom", "cart.rom"]
            }
        },
        "Atari 800": {
            "required": ["ATARIXL.ROM", "ATARIBAS.ROM"],
            "alternative_names": {
                "ATARIXL.ROM": ["ATARIXL.ROM", "ATARIXL.rom", "atari800xl.rom", "atariosb.rom"],
                "ATARIBAS.ROM": ["ATARIBAS.ROM", "ATARIBAS.rom", "atari800bas.rom", "atari_basic.rom"]
            }
        },
        "Atari-8-bit": {
            "required": ["ATARIXL.ROM", "ATARIBAS.ROM"],
            "alternative_names": {
                "ATARIXL.ROM": ["ATARIXL.ROM", "ATARIXL.rom", "atari800xl.rom", "atariosb.rom"],
                "ATARIBAS.ROM": ["ATARIBAS.ROM", "ATARIBAS.rom", "atari800bas.rom", "atari_basic.rom"]
            }
        },
        "Atari ST": {
            "required": ["tos.img"],
            "alternative_names": {
                "tos.img": ["tos.img", "TOS.IMG", "tos.rom", "TOS.ROM", "etosrom.img"]
            }
        },
        "Atari 7800": {
            "required": ["7800 BIOS (U).rom"],
            "alternative_names": {
                "7800 BIOS (U).rom": ["7800 BIOS (U).rom", "7800bios.rom", "bios.rom", "7800.rom"]
            }
        },
        "MSX": {
            "required": ["MSX.ROM", "MSX2.ROM"],
            "alternative_names": {
                "MSX.ROM": ["MSX.ROM", "MSX.rom", "msx1.rom", "MSX_BIOS.rom"],
                "MSX2.ROM": ["MSX2.ROM", "MSX2.rom", "msx2.rom", "MSX2_BIOS.rom"]
            }
        },
        "MSX2": {
            "required": ["MSX2.ROM", "MSX2EXT.ROM"],
            "alternative_names": {
                "MSX2.ROM": ["MSX2.ROM", "MSX2.rom", "msx2.rom", "MSX2_BIOS.rom"],
                "MSX2EXT.ROM": ["MSX2EXT.ROM", "MSX2EXT.rom", "msx2ext.rom", "MSX2_EXT.rom"]
            }
        },
        "BBC Micro": {
            "required": ["BeebROM.bin"],
            "alternative_names": {
                "BeebROM.bin": ["BeebROM.bin", "beebrom.bin", "rom.bin", "bbcmicro.rom"]
            }
        },
        "Commodore 64": {
            "required": ["c64.rom"],
            "alternative_names": {
                "c64.rom": ["c64.rom", "C64.ROM", "basic.rom", "kernal.rom", "chargen.rom"]
            }
        },
        "C64": {
            "required": ["c64.rom"],
            "alternative_names": {
                "c64.rom": ["c64.rom", "C64.ROM", "basic.rom", "kernal.rom", "chargen.rom"]
            }
        },
    }
    
    def __init__(self, bios_dir: Path = None): #vers 1
        """Initialize BIOS manager
        
        Args:
            bios_dir: Optional custom BIOS directory
        """
        self.bios_dir = Path(bios_dir) if bios_dir else None
        self.bios_cache = {}
        
    def scan_bios_directory(self, bios_path: Path) -> Dict[str, Path]:
        """Scan a BIOS directory for available files
        
        Args:
            bios_path: Directory to scan
            
        Returns:
            Dict of filename -> Path
        """
        bios_files = {}
        
        if not bios_path.exists():
            return bios_files
            
        for item in bios_path.iterdir():
            if item.is_file() and item.suffix.lower() in ['.rom', '.bin', '.img', '.iso']:
                bios_files[item.name.lower()] = item
                
        return bios_files
    
    def find_bios_files(self) -> Dict[str, Path]:
        """Find all available BIOS files in common locations
        
        Returns:
            Dict of filename -> Path
        """
        all_bios = {}
        
        # Use custom BIOS directory if provided
        if self.bios_dir:
            all_bios.update(self.scan_bios_directory(self.bios_dir))
            
        # Scan common BIOS paths
        for bios_path in self.BIOS_PATHS:
            all_bios.update(self.scan_bios_directory(bios_path))
            
        return all_bios
    
    def get_platform_bios_requirements(self, platform_name: str) -> Dict:
        """Get BIOS requirements for a specific platform
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            Dict with required files and alternative names
        """
        # Normalize platform name
        normalized_name = self.normalize_platform_name(platform_name)
        
        return self.PLATFORM_BIOS_REQUIREMENTS.get(normalized_name, {
            "required": [],
            "alternative_names": {}
        })
    
    def normalize_platform_name(self, platform_name: str) -> str:
        """Normalize platform name to handle variations
        
        Args:
            platform_name: Original platform name
            
        Returns:
            Normalized platform name
        """
        # Common aliases and variations
        platform_aliases = {
            "Amiga 500": "Amiga",
            "Amiga 1200": "Amiga",
            "AtariST": "Atari ST",
            "Atari_ST": "Atari ST",
            "Atari-ST": "Atari ST",
            "Atari 800XL": "Atari 800",
            "Atari800": "Atari 800",
            "ZX Spectrum 48K": "ZX Spectrum",
            "ZX Spectrum 128K": "ZX Spectrum 128",
            "Commodore 64": "C64",
            "C-64": "C64",
            "MSX1": "MSX",
        }
        
        normalized = platform_name.strip()
        
        # Handle variations with spaces, underscores, hyphens
        normalized = normalized.replace('_', ' ').replace('-', ' ')
        
        # Check aliases
        return platform_aliases.get(normalized, normalized)
    
    def get_bios_paths(self, platform_name: str) -> Dict[str, Optional[Path]]:
        """Get actual paths for required BIOS files for a platform
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            Dict of required_file -> actual_path or None if not found
        """
        platform_name = self.normalize_platform_name(platform_name)
        requirements = self.get_platform_bios_requirements(platform_name)
        available_bios = self.find_bios_files()
        
        bios_paths = {}
        
        for required_file in requirements["required"]:
            # Check for exact match first
            if required_file.lower() in available_bios:
                bios_paths[required_file] = available_bios[required_file.lower()]
                continue
                
            # Check alternative names
            found = False
            if required_file in requirements["alternative_names"]:
                for alt_name in requirements["alternative_names"][required_file]:
                    if alt_name.lower() in available_bios:
                        bios_paths[required_file] = available_bios[alt_name.lower()]
                        found = True
                        break
                        
            if not found:
                bios_paths[required_file] = None
                
        return bios_paths
    
    def is_platform_bios_complete(self, platform_name: str) -> bool:
        """Check if all required BIOS files are available for a platform
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            True if all required BIOS files are available
        """
        bios_paths = self.get_bios_paths(platform_name)
        
        # Check if all required files have paths (not None)
        for required_file, path in bios_paths.items():
            if path is None:
                return False
                
        return True
    
    def get_missing_bios(self, platform_name: str) -> List[str]:
        """Get list of missing BIOS files for a platform
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            List of missing BIOS file names
        """
        bios_paths = self.get_bios_paths(platform_name)
        missing = []
        
        for required_file, path in bios_paths.items():
            if path is None:
                missing.append(required_file)
                
        return missing
    
    def get_platform_bios_info(self, platform_name: str) -> Dict:
        """Get comprehensive BIOS info for a platform
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            Dict with BIOS information
        """
        platform_name = self.normalize_platform_name(platform_name)
        requirements = self.get_platform_bios_requirements(platform_name)
        bios_paths = self.get_bios_paths(platform_name)
        
        return {
            "platform": platform_name,
            "required_files": requirements["required"],
            "available_files": {name: str(path) if path else None for name, path in bios_paths.items()},
            "missing_files": self.get_missing_bios(platform_name),
            "bios_complete": self.is_platform_bios_complete(platform_name),
            "bios_directory": str(self.bios_dir) if self.bios_dir else "auto-detected"
        }

def test_bios_manager():
    """Test function for BIOS manager"""
    print("Testing BIOS Manager...")
    
    # Create BIOS manager
    bios_manager = BiosManager()
    
    # Test platforms
    test_platforms = [
        "Amiga", "Atari 5200", "Atari 800", "Atari ST", 
        "MSX", "ZX Spectrum", "Commodore 64", "BBC Micro"
    ]
    
    for platform in test_platforms:
        info = bios_manager.get_platform_bios_info(platform)
        print(f"\n{platform}:")
        print(f"  Required: {info['required_files']}")
        print(f"  Available: {info['available_files']}")
        print(f"  Missing: {info['missing_files']}")
        print(f"  Complete: {info['bios_complete']}")

if __name__ == "__main__":
    test_bios_manager()