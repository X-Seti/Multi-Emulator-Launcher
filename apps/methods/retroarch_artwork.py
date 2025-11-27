#!/usr/bin/env python3
#this belongs in apps/methods/retroarch_artwork.py - Version: 1
# X-Seti - November27 2025 - Multi-Emulator Launcher - RetroArch Artwork Scanner

"""
RetroArch Artwork Scanner
Finds and uses artwork from existing RetroArch installation
Supports thumbnails from Named_Boxarts, Named_Titles, Named_Snaps
"""

import os
from pathlib import Path
from typing import Optional, List, Dict
from PyQt6.QtGui import QPixmap

##Methods list -
# __init__
# find_retroarch_dirs
# get_game_artwork
# get_platform_mapping
# scan_artwork_directories
# _clean_game_name
# _find_artwork_file

class RetroArchArtwork: #vers 1
    """Scanner for RetroArch artwork directories"""
    
    # Platform name mapping: MEL name -> RetroArch playlist name
    PLATFORM_MAPPING = {
        'PlayStation': 'Sony - PlayStation',
        'PlayStation 2': 'Sony - PlayStation 2',
        'PSP': 'Sony - PlayStation Portable',
        'Nintendo 64': 'Nintendo - Nintendo 64',
        'GameCube': 'Nintendo - GameCube',
        'Wii': 'Nintendo - Wii',
        'SNES': 'Nintendo - Super Nintendo Entertainment System',
        'NES': 'Nintendo - Nintendo Entertainment System',
        'Game Boy': 'Nintendo - Game Boy',
        'Game Boy Color': 'Nintendo - Game Boy Color',
        'Game Boy Advance': 'Nintendo - Game Boy Advance',
        'Genesis': 'Sega - Mega Drive - Genesis',
        'Mega Drive': 'Sega - Mega Drive - Genesis',
        'Master System': 'Sega - Master System - Mark III',
        'Dreamcast': 'Sega - Dreamcast',
        'Saturn': 'Sega - Saturn',
        'Amiga': 'Commodore - Amiga',
        'C64': 'Commodore - 64',
        'Atari 2600': 'Atari - 2600',
        'Atari 7800': 'Atari - 7800',
        'Atari ST': 'Atari - ST',
        'Atari Lynx': 'Atari - Lynx',
        'Neo Geo': 'SNK - Neo Geo',
        'Neo Geo Pocket': 'SNK - Neo Geo Pocket',
        'Neo Geo Pocket Color': 'SNK - Neo Geo Pocket Color',
        'TurboGrafx-16': 'NEC - PC Engine - TurboGrafx 16',
        'PC Engine': 'NEC - PC Engine - TurboGrafx 16',
        'Wonderswan': 'Bandai - WonderSwan',
        'Wonderswan Color': 'Bandai - WonderSwan Color',
        '3DO': 'The 3DO Company - 3DO',
        'Arcade': 'MAME'
    }
    
    def __init__(self): #vers 1
        """Initialize RetroArch artwork scanner"""
        self.retroarch_dirs = []
        self.thumbnails_dir = None
        self.artwork_cache = {}
        
        # Find RetroArch directories
        self.retroarch_dirs = self.find_retroarch_dirs()
        
        # Scan for thumbnails
        if self.retroarch_dirs:
            self.scan_artwork_directories()
    
    def find_retroarch_dirs(self): #vers 1
        """Find RetroArch installation directories
        
        Returns:
            List of Path objects to RetroArch directories
        """
        possible_dirs = []
        
        # Linux paths
        if os.name == 'posix':
            possible_dirs.extend([
                Path.home() / '.config' / 'retroarch',
                Path('/usr/share/retroarch'),
                Path('/usr/local/share/retroarch'),
                Path.home() / '.local' / 'share' / 'retroarch',
            ])
        
        # Windows paths
        elif os.name == 'nt':
            possible_dirs.extend([
                Path(os.environ.get('APPDATA', '')) / 'RetroArch',
                Path('C:/RetroArch'),
                Path(os.environ.get('PROGRAMFILES', '')) / 'RetroArch',
            ])
        
        # macOS paths
        elif os.name == 'darwin':
            possible_dirs.extend([
                Path.home() / 'Library' / 'Application Support' / 'RetroArch',
                Path('/Applications/RetroArch.app/Contents/Resources'),
            ])
        
        # Filter to existing directories
        found_dirs = [d for d in possible_dirs if d.exists()]
        
        return found_dirs
    
    def scan_artwork_directories(self): #vers 1
        """Scan RetroArch directories for thumbnails"""
        for retroarch_dir in self.retroarch_dirs:
            # Check for thumbnails directory
            thumbnails = retroarch_dir / 'thumbnails'
            if thumbnails.exists():
                self.thumbnails_dir = thumbnails
                from apps.utils.debug_logger import info
                info(f"Found RetroArch thumbnails: {thumbnails}", "ARTWORK")
                break
    
    def get_platform_mapping(self, platform_name): #vers 1
        """Get RetroArch playlist name for platform
        
        Args:
            platform_name: MEL platform name
            
        Returns:
            RetroArch playlist name or None
        """
        return self.PLATFORM_MAPPING.get(platform_name)
    
    def get_game_artwork(self, platform_name, game_name, artwork_type='Named_Boxarts'): #vers 1
        """Get artwork for a game
        
        Args:
            platform_name: MEL platform name
            game_name: Game name
            artwork_type: Type of artwork (Named_Boxarts, Named_Titles, Named_Snaps)
            
        Returns:
            Path to artwork file or None
        """
        if not self.thumbnails_dir:
            return None
        
        # Get RetroArch playlist name
        retroarch_platform = self.get_platform_mapping(platform_name)
        if not retroarch_platform:
            from apps.utils.debug_logger import debug
            debug(f"No RetroArch mapping for platform: {platform_name}", "ARTWORK")
            return None
        
        # Check cache
        cache_key = f"{platform_name}:{game_name}:{artwork_type}"
        if cache_key in self.artwork_cache:
            return self.artwork_cache[cache_key]
        
        # Clean game name for filename matching
        clean_name = self._clean_game_name(game_name)
        
        # Build path to artwork directory
        artwork_dir = self.thumbnails_dir / retroarch_platform / artwork_type
        
        if not artwork_dir.exists():
            from apps.utils.debug_logger import debug
            debug(f"Artwork directory not found: {artwork_dir}", "ARTWORK")
            return None
        
        # Try to find artwork file
        artwork_file = self._find_artwork_file(artwork_dir, clean_name)
        
        # Cache result
        self.artwork_cache[cache_key] = artwork_file
        
        if artwork_file:
            from apps.utils.debug_logger import debug
            debug(f"Found artwork: {artwork_file.name}", "ARTWORK")
        
        return artwork_file
    
    def _clean_game_name(self, game_name): #vers 1
        """Clean game name for filename matching
        
        Args:
            game_name: Original game name
            
        Returns:
            Cleaned name for filename matching
        """
        # Remove file extensions
        name = game_name
        for ext in ['.zip', '.7z', '.rar', '.adf', '.st', '.sms', '.gg', '.bin', '.cue', '.iso']:
            if name.lower().endswith(ext):
                name = name[:-len(ext)]
        
        # RetroArch uses URL encoding for special characters
        # For now, just do basic cleaning
        name = name.strip()
        
        return name
    
    def _find_artwork_file(self, artwork_dir, game_name): #vers 1
        """Find artwork file in directory
        
        Args:
            artwork_dir: Directory to search
            game_name: Cleaned game name
            
        Returns:
            Path to artwork file or None
        """
        # Try common image extensions
        for ext in ['.png', '.jpg', '.jpeg']:
            # Try exact match
            artwork_file = artwork_dir / f"{game_name}{ext}"
            if artwork_file.exists():
                return artwork_file
        
        # Try case-insensitive search
        try:
            for file in artwork_dir.iterdir():
                if file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    # Compare without extension and case-insensitive
                    file_stem = file.stem.lower()
                    game_stem = game_name.lower()
                    
                    if file_stem == game_stem:
                        return file
        except Exception as e:
            from apps.utils.debug_logger import error
            error(f"Error searching artwork directory: {e}", "ARTWORK")
        
        return None
    
    def get_available_platforms(self): #vers 1
        """Get list of platforms with available artwork
        
        Returns:
            List of RetroArch platform names
        """
        if not self.thumbnails_dir:
            return []
        
        platforms = []
        try:
            for item in self.thumbnails_dir.iterdir():
                if item.is_dir():
                    platforms.append(item.name)
        except Exception as e:
            from apps.utils.debug_logger import error
            error(f"Error listing platforms: {e}", "ARTWORK")
        
        return platforms
    
    def load_artwork_pixmap(self, artwork_path, size=(64, 64)): #vers 1
        """Load artwork as QPixmap
        
        Args:
            artwork_path: Path to artwork file
            size: Tuple of (width, height) for scaling
            
        Returns:
            QPixmap or None
        """
        if not artwork_path or not artwork_path.exists():
            return None
        
        try:
            pixmap = QPixmap(str(artwork_path))
            if not pixmap.isNull():
                # Scale to requested size while maintaining aspect ratio
                pixmap = pixmap.scaled(
                    size[0], size[1],
                    aspectRatioMode=1,  # Keep aspect ratio
                    transformMode=1     # Smooth transformation
                )
                return pixmap
        except Exception as e:
            from apps.utils.debug_logger import error
            error(f"Error loading artwork: {e}", "ARTWORK")
        
        return None
