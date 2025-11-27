#!/usr/bin/env python3
#this belongs in apps/methods/platform_scanner.py - Version: 3
# X-Seti - November22 2025 - Multi-Emulator Launcher - Platform Scanner

"""
Dynamic Platform Scanner
Discovers emulator platforms by scanning ROM directories
Handles spaces in names, ignores system files, supports compressed formats (ZIP/7Z/RAR)
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set

##Methods list -
# __init__
# get_platform_info
# get_platforms
# scan_platforms
# _count_roms_in_directory
# _detect_file_extensions
# _guess_platform_type
# _is_system_file

class PlatformScanner: #vers 3
    """Dynamically discovers platforms from ROM directory structure"""
    
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
    
    def __init__(self, roms_dir: Path): #vers 2
        """Initialize platform scanner"""
        self.roms_dir = Path(roms_dir)
        self.platforms = {}
        
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
    
    def scan_platforms(self) -> Dict[str, Dict]: #vers 2
        """Scan ROM directory and discover platforms - handles spaces"""
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
            
            # Store platform info (spaces preserved!)
            platforms[platform_name] = {
                "name": platform_name,
                "path": str(item),
                "rom_count": rom_count,
                "extensions": list(extensions),
                "type": platform_type,
            }
            
            print(f"Loaded {len(platforms)} platform(s): {', '.join(platforms.keys())}")
            
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
