#!/usr/bin/env python3
#this belongs in apps/methods/platform_scanner.py - Version: 4
# X-Seti - November28 2025 - Multi-Emulator Launcher - Platform Scanner

"""
Dynamic Platform Scanner
Discovers emulator platforms by scanning ROM directories
Handles spaces in names, ignores system files, supports compressed formats (ZIP/7Z/RAR)
Integrates with dynamic core detection and BIOS management
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from .system_core_scanner import SystemCoreScanner
from .bios_manager import BiosManager

##Methods list -
# __init__
# get_platform_info
# get_platforms
# scan_platforms
# update_platform_config_with_cores
# _count_roms_in_directory
# _detect_file_extensions
# _guess_platform_type
# _is_system_file

class PlatformScanner: #vers 4
    """Dynamically discovers platforms from ROM directory structure with core detection"""
    
    # Files/folders to ignore
    IGNORE_PATTERNS = {
        '.folder',  # System marker files
        '.DS_Store',  # macOS
        'Thumbs.db',  # Windows
        'desktop.ini',  # Windows
        '.git', '.gitignore',
        '__pycache__',
        'bootcode.bin',  # Raspberry Pi boot files
        'kernel.img', 'kernel7.img', 'kernel8-32.img',
        'bcm', #Raspberry Pi device tree files (start with bcm)
        'HXCSDFE.CFG', 'IMAGE_A.CFG',  # HxC floppy emulator
        '.iso',  # Boot ISOs like SPECCY97.iso
    }
    
    # Extension patterns
    EXTENSION_HINTS = {
        ".adf": ["Amiga"],
        ".ipf": ["Amiga"],
        ".dms": ["Amiga"],
        ".st": ["Atari ST"],
        ".stx": ["Atari ST"],
        ".a26": ["Atari 2600"],
        ".a52": ["Atari 5200"],
        ".a78": ["Atari 7800"],
        ".xex": ["Atari 800"],
        ".atr": ["Atari 800"],
        ".cas": ["Atari 800"],
        ".cue": ["PlayStation 1"],
        ".bin": ["PlayStation 1", "Atari 2600"],
        ".iso": ["PlayStation 2"],
        ".tap": ["ZX Spectrum", "Amstrad CPC"],
        ".tzx": ["ZX Spectrum"],
        ".sna": ["ZX Spectrum"],
        ".z80": ["ZX Spectrum"],
        ".dsk": ["Amstrad CPC", "MSX"],
        ".cdt": ["Amstrad CPC"],
        ".d64": ["C64"],
        ".t64": ["C64"],
        ".crt": ["C64"],
        ".prg": ["C64"],
        ".d81": ["C128"],
        ".rom": ["MSX", "Plus4", "Sam Coupe"],
        ".mx1": ["MSX"],
        ".mx2": ["MSX"],
        ".p41": ["Plus4"],
        ".mgt": ["Sam Coupe"],
        ".sad": ["Sam Coupe"],
        ".nes": ["Nintendo Entertainment System"],
        ".sfc": ["Super Nintendo"],
        ".smc": ["Super Nintendo"],
        ".gba": ["Game Boy Advance"],
        ".gen": ["Genesis"],
        ".md": ["Genesis"],
        ".smd": ["Genesis"],
    }
    
    # Platform to core mapping for dynamic detection
    PLATFORM_CORE_MAPPING = {
        "Amiga": ["puae", "uae"],
        "Atari 2600": ["stella", "stella2014"],
        "Atari 5200": ["atari800", "atari800_libretro"],
        "Atari 7800": ["prosystem"],
        "Atari 800": ["atari800", "atari800_libretro"],
        "Atari ST": ["hatari"],
        "Amstrad CPC": ["cap32", "crocods"],
        "BBC Micro": ["mame", "mess"],
        "C64": ["vice_x64", "vice_x64_libretro"],
        "Commodore 64": ["vice_x64", "vice_x64_libretro"],
        "MSX": ["fmsx", "bluemsx", "mesen-s"],
        "MSX2": ["fmsx", "bluemsx"],
        "ZX Spectrum": ["fuse", "scummvm"],
        "ZX Spectrum 128": ["fuse"],
        "Z81-Spec256": ["fuse"],
        "MS-DOS": ["dosbox_pure", "dosbox"],
        "Dragon 32-64": ["xroar"],
        "Sam Coupe": ["mame"],
        "Oric Atmos": ["mame"],
        "TRS-80": ["mame"],
        "Fujitsu FM-7": ["mame"],
        "Plus4": ["vice_xplus4"],
    }
    
    # Core name aliases for backward compatibility
    CORE_ALIASES = {
        "uae": "puae",
        "stella2014": "stella",
        "atari800_libretro": "atari800",
        "vice_x64_libretro": "vice_x64",
        "mess": "mame",
    }
    
    def __init__(self, roms_dir: Path, cores_dir: Path = None): #vers 3
        """Initialize platform scanner with core detection
        
        Args:
            roms_dir: Directory containing ROMs
            cores_dir: Directory containing cores (optional, defaults to ./cores)
        """
        self.roms_dir = Path(roms_dir)
        self.platforms = {}
        self.core_scanner = SystemCoreScanner(cores_dir or Path("./cores"))
        self.bios_manager = BiosManager()
        
        # Get available cores
        self.available_cores = self.core_scanner.get_installed_cores()
        print(f"Available cores: {list(self.available_cores.keys())}")
        
    def _is_system_file(self, name: str) -> bool: #vers 1
        """Check if file/folder should be ignored
        
        Args:
            name: File or folder name
            
        Returns:
            True if should be ignored
        """
        name_lower = name.lower()
        
        # Check exact matches
        if name in self.IGNORE_PATTERNS:
            return True
            
        # Check if name starts with ignore pattern
        for pattern in self.IGNORE_PATTERNS:
            if name_lower.startswith(pattern.lower()):
                return True
                
        # Ignore files starting with dot
        if name.startswith('.'):
            return True
            
        # Ignore .zip BIOS files
        if 'bios' in name_lower and name_lower.endswith('.zip'):
            return True
            
        return False
    
    def update_platform_config_with_cores(self, platform_config: Dict) -> Dict:
        """Update platform configuration with available cores
        
        Args:
            platform_config: Original platform configuration
            
        Returns:
            Updated platform configuration with available cores
        """
        # Make a copy of the original config
        updated_config = platform_config.copy()
        
        # Get the platform name for core mapping
        platform_name = updated_config.get("name", "")
        
        # Find available cores for this platform
        available_platform_cores = []
        
        # Check platform-specific core mappings
        if platform_name in self.PLATFORM_CORE_MAPPING:
            for core_candidate in self.PLATFORM_CORE_MAPPING[platform_name]:
                # Check if core exists (try both original and alias)
                actual_core = self.CORE_ALIASES.get(core_candidate, core_candidate)
                if actual_core in self.available_cores:
                    available_platform_cores.append(actual_core)
                elif core_candidate in self.available_cores:
                    available_platform_cores.append(core_candidate)
        
        # If no specific mapping found, try to determine from existing cores
        if not available_platform_cores and "cores" in updated_config:
            for core_candidate in updated_config["cores"]:
                actual_core = self.CORE_ALIASES.get(core_candidate, core_candidate)
                if actual_core in self.available_cores:
                    available_platform_cores.append(actual_core)
                elif core_candidate in self.available_cores:
                    available_platform_cores.append(core_candidate)
        
        # Update the cores list with only available ones
        updated_config["cores"] = available_platform_cores
        updated_config["core_available"] = len(available_platform_cores) > 0
        
        # Add BIOS information
        bios_info = self.bios_manager.get_platform_bios_info(platform_name)
        updated_config["bios_complete"] = bios_info["bios_complete"]
        updated_config["missing_bios"] = bios_info["missing_files"]
        updated_config["bios_required"] = len(bios_info["required_files"]) > 0
        
        return updated_config
    
    def scan_platforms(self) -> Dict[str, Dict]: #vers 3
        """Scan ROM directory and discover platforms - handles spaces
        Integrates with dynamic core detection and BIOS management
        """
        if not self.roms_dir.exists():
            print(f"ROM directory not found: {self.roms_dir}")
            return {}
            
        print(f"Scanning for platforms in: {self.roms_dir}")
        print("=" * 60)
        
        platforms = {}
        
        # Scan all subdirectories
        for item in self.roms_dir.iterdir():
            # Skip non-directories
            if not item.is_dir():
                continue
            
            # Skip system files/folders    
            if self._is_system_file(item.name):
                print(f"Skipping system folder: {item.name}")
                continue
                
            platform_name = item.name
            
            # Count ROMs
            rom_count = self._count_roms_in_directory(item)
            
            if rom_count == 0:
                print(f"Skipping {platform_name} (no ROM files found)")
                continue
                
            # Detect file extensions
            extensions = self._detect_file_extensions(item)
            
            # Guess platform type
            platform_type = self._guess_platform_type(platform_name, extensions)
            
            # Create basic platform config
            basic_config = {
                "name": platform_name,
                "path": str(item),
                "rom_count": rom_count,
                "extensions": list(extensions),
                "type": platform_type,
                # Default values that will be updated with dynamic detection
                "cores": [],
                "core_available": False,
                "bios_required": False,
                "bios_complete": False,
                "missing_bios": [],
            }
            
            # Update with dynamic core detection and BIOS info
            platform_config = self.update_platform_config_with_cores(basic_config)
            
            # Only add platform if it has available cores (to avoid "No core available" messages)
            if platform_config["core_available"]:
                platforms[platform_name] = platform_config
                print(f"✓ {platform_name}: {rom_count} ROMs, cores: {platform_config['cores']}, BIOS: {'✓' if platform_config['bios_complete'] else '✗' if platform_config['bios_required'] else 'N/A'}")
            else:
                print(f"✗ {platform_name}: No available core found for this platform")
                
        print(f"\nLoaded {len(platforms)} platform(s): {', '.join(platforms.keys())}")
        
        self.platforms = platforms
        return platforms
    
    def get_platforms(self) -> List[str]: #vers 1
        """Get list of platform names"""
        return list(self.platforms.keys())
    
    def get_platform_info(self, platform_name: str) -> Optional[Dict]: #vers 1
        """Get info for specific platform"""
        return self.platforms.get(platform_name)
    
    def _count_roms_in_directory(self, directory: Path) -> int: #vers 3
        """Count ROM files in directory - ignore system files, include archives"""
        count = 0
        rom_extensions = {
            '.adf', '.ipf', '.dms',  # Amiga
            '.st', '.stx',  # Atari ST
            '.a26', '.a52', '.a78',  # Atari consoles
            '.xex', '.atr', '.cas',  # Atari 8-bit
            '.tap', '.tzx', '.sna', '.z80',  # Spectrum
            '.dsk', '.cdt',  # Amstrad
            '.d64', '.t64', '.crt', '.prg',  # C64
            '.d81',  # C128
            '.rom', '.mx1', '.mx2',  # MSX
            '.nes', '.sfc', '.smc', '.gba',  # Nintendo
            '.gen', '.md', '.smd',  # Sega
            '.cue', '.bin', '.iso',  # Disc formats
            '.zip', '.7z', '.rar',  # Compressed archives
        }
        
        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue
                
            # Skip system files
            if self._is_system_file(file_path.name):
                continue
                
            if file_path.suffix.lower() in rom_extensions:
                count += 1
                    
        return count
        
    def _detect_file_extensions(self, directory: Path) -> Set[str]: #vers 2
        """Detect all ROM file extensions - ignore system files"""
        extensions = set()
        
        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue
                
            # Skip system files
            if self._is_system_file(file_path.name):
                continue
                
            ext = file_path.suffix.lower()
            if ext and ext != '.folder':
                extensions.add(ext)
                    
        return extensions
        
    def _guess_platform_type(self, platform_name: str, extensions: Set[str]) -> str: #vers 1
        """Guess platform type from name and extensions"""
        matches = {}
        
        for ext in extensions:
            if ext in self.EXTENSION_HINTS:
                for platform_type in self.EXTENSION_HINTS[ext]:
                    if platform_type not in matches:
                        matches[platform_type] = 0
                    matches[platform_type] += 1
                    
        if matches:
            best_match = max(matches.items(), key=lambda x: x[1])[0]
            
            if best_match.lower() in platform_name.lower() or \
               platform_name.lower() in best_match.lower():
                return best_match
                
        return platform_name
