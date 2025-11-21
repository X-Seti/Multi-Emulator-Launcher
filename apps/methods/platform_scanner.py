#!/usr/bin/env python3
#this belongs in apps/methods/platform_scanner.py - Version: 1
# X-Seti - November20 2025 - Multi-Emulator Launcher - Platform Scanner

"""
Dynamic Platform Scanner
Discovers emulator platforms by scanning ROM directories
No hardcoded platform list - adapts to user's collection
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

##class PlatformScanner -

class PlatformScanner: #vers 1
    """Dynamically discovers platforms from ROM directory structure"""
    
    # Extension patterns to help identify platform types
    EXTENSION_HINTS = {
        ".adf": ["Amiga"],
        ".ipf": ["Amiga"],
        ".dms": ["Amiga"],
        ".st": ["Atari ST"],
        ".stx": ["Atari ST"],
        ".cue": ["PlayStation 1", "Sega CD", "Sega Saturn"],
        ".bin": ["PlayStation 1", "Sega Genesis", "Atari 2600"],
        ".iso": ["PlayStation 2", "PlayStation 3", "GameCube", "Wii", "Dreamcast"],
        ".nsp": ["Nintendo Switch"],
        ".xci": ["Nintendo Switch"],
        ".n64": ["Nintendo 64"],
        ".z64": ["Nintendo 64"],
        ".v64": ["Nintendo 64"],
        ".nes": ["Nintendo Entertainment System"],
        ".sfc": ["Super Nintendo"],
        ".smc": ["Super Nintendo"],
        ".gba": ["Game Boy Advance"],
        ".gbc": ["Game Boy Color"],
        ".gb": ["Game Boy"],
        ".nds": ["Nintendo DS"],
        ".3ds": ["Nintendo 3DS"],
        ".cia": ["Nintendo 3DS"],
        ".gcm": ["Nintendo GameCube"],
        ".gcz": ["Nintendo GameCube"],
        ".wbfs": ["Nintendo Wii"],
        ".wad": ["Nintendo Wii"],
        ".gen": ["Sega Genesis"],
        ".md": ["Sega Genesis"],
        ".smd": ["Sega Genesis"],
        ".32x": ["Sega 32X"],
        ".gg": ["Sega Game Gear"],
        ".sms": ["Sega Master System"],
        ".psp": ["PSP"],
        ".cso": ["PSP"]
    }
    
    def __init__(self, roms_dir: Path): #vers 1
        """Initialize platform scanner
        
        Args:
            roms_dir: Path to roms directory
        """
        self.roms_dir = Path(roms_dir)
        self.platforms = {}  # {platform_name: platform_info}
        
    def scan_platforms(self) -> Dict[str, Dict]: #vers 1
        """Scan ROM directory and discover platforms
        
        Returns:
            Dict mapping platform names to platform info
        """
        if not self.roms_dir.exists():
            print(f"ROM directory not found: {self.roms_dir}")
            return {}
            
        print(f"Scanning for platforms in: {self.roms_dir}")
        print("=" * 60)
        
        platforms = {}
        
        # Scan all subdirectories
        for item in self.roms_dir.iterdir():
            if not item.is_dir():
                continue
                
            platform_name = item.name
            
            # Count ROMs
            rom_count = self._count_roms_in_directory(item)
            
            if rom_count == 0:
                print(f"Skipping {platform_name} (no ROM files found)")
                continue
                
            # Detect file extensions
            extensions = self._detect_file_extensions(item)
            
            # Guess platform type from extensions
            platform_type = self._guess_platform_type(platform_name, extensions)
            
            # Store platform info
            platforms[platform_name] = {
                "name": platform_name,
                "path": str(item),
                "rom_count": rom_count,
                "extensions": list(extensions),
                "type": platform_type,
                "discovered": True
            }
            
            print(f"✓ {platform_name}")
            print(f"  ROMs: {rom_count}")
            print(f"  Extensions: {', '.join(sorted(extensions))}")
            print(f"  Type: {platform_type}")
            print()
            
        self.platforms = platforms
        
        print("=" * 60)
        print(f"Discovered {len(platforms)} platform(s)")
        print("=" * 60)
        
        return platforms
        
    def get_platforms(self) -> List[str]: #vers 1
        """Get list of discovered platform names
        
        Returns:
            List of platform names
        """
        if not self.platforms:
            self.scan_platforms()
            
        return sorted(self.platforms.keys())
        
    def get_platform_info(self, platform_name: str) -> Optional[Dict]: #vers 1
        """Get information about a specific platform
        
        Args:
            platform_name: Platform name
            
        Returns:
            Platform info dict or None
        """
        if not self.platforms:
            self.scan_platforms()
            
        return self.platforms.get(platform_name)
        
    def _count_roms_in_directory(self, directory: Path) -> int: #vers 1
        """Count ROM files in directory (recursive)
        
        Args:
            directory: Directory to scan
            
        Returns:
            Number of ROM files
        """
        count = 0
        
        # Common ROM extensions
        rom_extensions = {
            '.adf', '.ipf', '.dms', '.hdf',  # Amiga
            '.st', '.stx', '.msa',  # Atari ST
            '.cue', '.bin', '.iso', '.img', '.chd', '.pbp',  # Disc images
            '.zip', '.7z', '.rar',  # Archives
            '.n64', '.v64', '.z64',  # N64
            '.nes', '.fds', '.unf',  # NES
            '.sfc', '.smc',  # SNES
            '.gba', '.gbc', '.gb',  # Game Boy
            '.nds', '.3ds', '.cia',  # Nintendo handhelds
            '.gcm', '.gcz', '.iso',  # GameCube
            '.wbfs', '.wad',  # Wii
            '.gen', '.md', '.smd', '.32x',  # Sega
            '.gg', '.sms',  # Sega 8/16-bit
            '.psp', '.cso',  # PSP
            '.nsp', '.xci'  # Switch
        }
        
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                if file_path.suffix.lower() in rom_extensions:
                    count += 1
                    
        return count
        
    def _detect_file_extensions(self, directory: Path) -> Set[str]: #vers 1
        """Detect all file extensions in directory
        
        Args:
            directory: Directory to scan
            
        Returns:
            Set of file extensions (with dots)
        """
        extensions = set()
        
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext:
                    extensions.add(ext)
                    
        return extensions
        
    def _guess_platform_type(self, platform_name: str, extensions: Set[str]) -> str: #vers 1
        """Guess platform type from name and extensions
        
        Args:
            platform_name: Platform name from directory
            extensions: Set of file extensions found
            
        Returns:
            Platform type classification
        """
        # First try to match by extensions
        matches = {}
        
        for ext in extensions:
            if ext in self.EXTENSION_HINTS:
                for platform_type in self.EXTENSION_HINTS[ext]:
                    if platform_type not in matches:
                        matches[platform_type] = 0
                    matches[platform_type] += 1
                    
        # If we have extension matches, use the most common one
        if matches:
            best_match = max(matches.items(), key=lambda x: x[1])[0]
            
            # Verify it's close to the directory name
            if best_match.lower() in platform_name.lower() or \
               platform_name.lower() in best_match.lower():
                return best_match
                
        # Fallback: use directory name as-is
        return platform_name


def create_platform_config(scanner: PlatformScanner, output_file: Path) -> None: #vers 1
    """Create platform configuration file from scanned platforms
    
    Args:
        scanner: PlatformScanner instance with scanned platforms
        output_file: Path to output JSON file
    """
    import json
    
    if not scanner.platforms:
        scanner.scan_platforms()
        
    config = {}
    
    for platform_name, info in scanner.platforms.items():
        config[platform_name] = {
            "extensions": info["extensions"],
            "rom_path": info["path"],
            "rom_count": info["rom_count"],
            "type": info["type"],
            "bios_required": False,  # Will be determined later
            "core": None  # Will be set by user
        }
        
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
        
    print(f"\nPlatform configuration saved to: {output_file}")


# CLI testing
if __name__ == "__main__":
    import sys
    
    base_dir = Path.cwd()
    roms_dir = base_dir / "roms"
    
    if len(sys.argv) > 1 and sys.argv[1] == "scan":
        # Scan for platforms
        scanner = PlatformScanner(roms_dir)
        platforms = scanner.scan_platforms()
        
        if not platforms:
            print("\nNo platforms found.")
            print(f"Create platform directories in: {roms_dir}")
            print("\nExample structure:")
            print("  roms/")
            print("    Amiga/")
            print("      game1.adf")
            print("      game2.adf")
            print("    PlayStation 1/")
            print("      game1.cue")
            print("      game1.bin")
        else:
            print(f"\nDiscovered platforms: {', '.join(sorted(platforms.keys()))}")
            
    elif len(sys.argv) > 1 and sys.argv[1] == "export":
        # Export platform configuration
        scanner = PlatformScanner(roms_dir)
        scanner.scan_platforms()
        
        output_file = base_dir / "config" / "discovered_platforms.json"
        create_platform_config(scanner, output_file)
        
    elif len(sys.argv) > 2 and sys.argv[1] == "info":
        # Show info for specific platform
        platform_name = sys.argv[2]
        
        scanner = PlatformScanner(roms_dir)
        scanner.scan_platforms()
        
        info = scanner.get_platform_info(platform_name)
        
        if info:
            print(f"\nPlatform: {info['name']}")
            print("=" * 60)
            print(f"Path: {info['path']}")
            print(f"ROMs: {info['rom_count']}")
            print(f"Extensions: {', '.join(info['extensions'])}")
            print(f"Type: {info['type']}")
        else:
            print(f"Platform not found: {platform_name}")
            
    else:
        print("Multi-Emulator Launcher - Platform Scanner")
        print("=" * 60)
        print("\nUsage:")
        print("  python platform_scanner.py scan              - Scan ROM directories")
        print("  python platform_scanner.py export            - Export config file")
        print("  python platform_scanner.py info <platform>   - Show platform info")
        print("\nExamples:")
        print("  python platform_scanner.py scan")
        print("  python platform_scanner.py export")
        print('  python platform_scanner.py info "Amiga"')
        print("\nDirectory Structure:")
        print("  Place ROMs in subdirectories named after platforms:")
        print("    roms/Amiga/")
        print("    roms/PlayStation 1/")
        print("    roms/Nintendo Switch/")
        print("  The scanner will automatically detect platforms from folder names.")
