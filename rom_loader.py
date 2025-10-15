"""
ROM Loader
Handles loading ROMs including ZIP extraction and caching
"""

import os
import zipfile
import shutil
import hashlib
from pathlib import Path


class RomLoader:
    def __init__(self, config, platforms):
        self.config = config
        self.platforms = platforms
        self.cache_dir = Path(config['cache_path']) / 'extracted'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.temp_extractions = []  # Track temp files for cleanup
    
    def load_rom(self, game_entry):
        """
        Load a ROM file, extracting from ZIP if necessary
        Returns the path to the loadable ROM file
        """
        game_type = game_entry['type']
        platform = game_entry['platform']
        platform_config = self.platforms.get(platform)
        
        if not platform_config:
            raise Exception(f"Unknown platform: {platform}")
        
        # Handle different game types
        if game_type == 'file':
            # Direct file, no extraction needed
            return game_entry['path']
        
        elif game_type == 'zip':
            # Extract ZIP and return main ROM file
            return self._extract_zip(game_entry, platform_config)
        
        elif game_type == 'folder':
            # Find main ROM in folder structure
            return self._find_folder_main_rom(game_entry)
        
        elif game_type == 'multidisk':
            # Return first disk
            first_disk = game_entry['disks'][0]
            # If first disk is a ZIP, extract it
            if first_disk.endswith('.zip'):
                temp_entry = {
                    'type': 'zip',
                    'path': first_disk,
                    'platform': platform,
                    'rom_files': game_entry.get('rom_files', [])
                }
                return self._extract_zip(temp_entry, platform_config)
            return first_disk
        
        raise Exception(f"Unknown game type: {game_type}")
    
    def _extract_zip(self, game_entry, platform_config):
        """Extract ZIP file and return path to main ROM"""
        zip_path = Path(game_entry['path'])
        
        # Check cache first if caching is enabled
        if platform_config.get('cache_extracted'):
            cached_path = self._get_cached_extraction(zip_path)
            if cached_path:
                return cached_path
        
        # Extract to temp or cache
        if platform_config.get('cache_extracted'):
            extract_dir = self._get_cache_path(zip_path)
        else:
            extract_dir = self.cache_dir / 'temp' / zip_path.stem
            self.temp_extractions.append(extract_dir)
        
        # Create extraction directory
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract ZIP
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract all files
                zip_ref.extractall(extract_dir)
            
            # Find main ROM file
            rom_files = game_entry.get('rom_files', [])
            if not rom_files:
                # Scan extracted directory for ROM files
                rom_files = self._find_rom_files(extract_dir, platform_config['extensions'])
            
            if not rom_files:
                raise Exception(f"No ROM files found in ZIP: {zip_path}")
            
            # Find the main/first disk
            main_rom = self._find_main_rom_file(rom_files, extract_dir)
            
            return str(main_rom)
        
        except Exception as e:
            # Cleanup on error
            if extract_dir.exists():
                shutil.rmtree(extract_dir, ignore_errors=True)
            raise Exception(f"Failed to extract ZIP {zip_path}: {e}")
    
    def _find_folder_main_rom(self, game_entry):
        """Find the main ROM file in a folder structure"""
        folder_path = Path(game_entry['path'])
        
        # Check for DISK1 subfolder first
        disk1_patterns = ['disk1', 'disk 1', 'disc1', 'disc 1']
        for pattern in disk1_patterns:
            for item in folder_path.iterdir():
                if item.is_dir() and pattern in item.name.lower():
                    # Look for ROM in this folder
                    for rom_file in item.iterdir():
                        if rom_file.is_file():
                            return str(rom_file)
        
        # If no DISK1 folder, return first ROM file found
        rom_files = game_entry.get('rom_files', [])
        if rom_files:
            first_rom = rom_files[0]
            return str(folder_path / first_rom)
        
        # Last resort: search entire folder
        for item in folder_path.rglob('*'):
            if item.is_file() and not item.name.startswith('.'):
                return str(item)
        
        raise Exception(f"No ROM files found in folder: {folder_path}")
    
    def _find_rom_files(self, directory, extensions):
        """Find all ROM files in a directory"""
        rom_files = []
        
        for item in Path(directory).rglob('*'):
            if item.is_file():
                ext = item.suffix.lower()
                if ext in extensions and not item.name.startswith('.'):
                    rom_files.append(str(item.relative_to(directory)))
        
        return rom_files
    
    def _find_main_rom_file(self, rom_files, base_path):
        """Find the main ROM file to load from a list"""
        base_path = Path(base_path)
        
        # Priority order for finding main ROM
        priorities = [
            lambda f: 'disk 1' in f.lower() or 'disk1' in f.lower(),
            lambda f: 'disc 1' in f.lower() or 'disc1' in f.lower(),
            lambda f: 'side a' in f.lower() or 'sidea' in f.lower(),
            lambda f: 'disk' not in f.lower() and 'disc' not in f.lower(),  # Single disk
        ]
        
        # Try each priority
        for priority_func in priorities:
            matches = [f for f in rom_files if priority_func(f)]
            if matches:
                return base_path / matches[0]
        
        # Default: return first file
        return base_path / rom_files[0]
    
    def _get_cache_path(self, zip_path):
        """Get cache directory path for a ZIP file"""
        # Create cache key based on file path and modification time
        zip_path = Path(zip_path)
        mtime = int(zip_path.stat().st_mtime)
        cache_key = f"{zip_path.stem}_{mtime}"
        
        return self.cache_dir / cache_key
    
    def _get_cached_extraction(self, zip_path):
        """Check if ZIP has been extracted to cache"""
        cache_path = self._get_cache_path(zip_path)
        
        if cache_path.exists():
            # Find a ROM file in the cache
            for item in cache_path.rglob('*'):
                if item.is_file() and not item.name.startswith('.'):
                    return str(item)
        
        return None
    
    def cleanup(self):
        """Clean up temporary extractions"""
        for temp_dir in self.temp_extractions:
            if temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"Warning: Could not remove temp directory {temp_dir}: {e}")
        
        self.temp_extractions.clear()
    
    def clear_cache(self):
        """Clear the entire extraction cache"""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_size(self):
        """Get total size of cache in bytes"""
        total_size = 0
        
        for item in self.cache_dir.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
        
        return total_size
