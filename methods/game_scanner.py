# X-Seti - October15 2025 - Multi-Emulator Launcher - Game Scanner
# This belongs in methods/game_scanner.py - Version: 1
"""
Game Scanner - Scans ROM directories, handles ZIP files, multi-disk games, and folder structures.
"""

##Methods list -
# _clean_name
# _create_game_entry
# _detect_multidisk
# _group_multidisk_games
# _is_valid_rom
# _scan_folder
# _scan_zip
# discover_platforms
# scan_platform

import os
import zipfile
import re
from pathlib import Path
from collections import defaultdict


class GameScanner: #vers 1
    def __init__(self, config, platforms): #vers 1
        self.config = config
        self.platforms = platforms
        self.rom_path = Path(config['rom_path'])
        
        self.skip_extensions = [
            '.txt', '.nfo', '.jpg', '.png', '.gif', '.pdf', 
            '.diz', '.doc', '.rtf', '.md', '.html'
        ]
    
    def _clean_name(self, name): #vers 1
        """Clean up game name for display"""
        cleaned = re.sub(r'\[.*?\]', '', name)
        cleaned = re.sub(r'\(.*?\)', '', cleaned)
        cleaned = re.sub(r'[_-]+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned if cleaned else name
    
    def _create_game_entry(self, file_path, platform_name): #vers 1
        """Create entry for a single ROM file"""
        return {
            'name': file_path.stem,
            'display_name': self._clean_name(file_path.stem),
            'type': 'file',
            'path': str(file_path),
            'platform': platform_name,
            'file_count': 1,
            'disk_count': 0,
            'disks': [str(file_path)]
        }
    
    def _detect_multidisk(self, file_list): #vers 1
        """Detect and order multi-disk games"""
        patterns = [
            r'disk\s*(\d+)',
            r'disc\s*(\d+)',
            r'side\s*([ab])',
            r'\(disk\s*(\d+)',
            r'\(disc\s*(\d+)',
            r'd(\d+)',
            r'_(\d+)\.'
        ]
        
        disk_files = []
        
        for filename in file_list:
            lower_name = filename.lower()
            
            for pattern in patterns:
                match = re.search(pattern, lower_name)
                if match:
                    disk_num = match.group(1)
                    if disk_num.isalpha():
                        disk_num = ord(disk_num.lower()) - ord('a') + 1
                    else:
                        disk_num = int(disk_num)
                    
                    disk_files.append((disk_num, filename))
                    break
        
        if len(disk_files) > 1:
            disk_files.sort(key=lambda x: x[0])
            return [f[1] for f in disk_files]
        
        return None
    
    def _group_multidisk_games(self, games): #vers 1
        """Group games that are split across multiple files"""
        disk_pattern = re.compile(
            r'(.+?)[\s_-]*'
            r'(?:'
            r'disk\s*\d+|'
            r'disc\s*\d+|'
            r'side\s*[ab]|'
            r'\(disk\s*\d+\)|'
            r'\(disc\s*\d+\)|'
            r'd\d+|'
            r'_\d+$'
            r')',
            re.IGNORECASE
        )
        
        grouped = defaultdict(list)
        single_games = []
        
        for game in games:
            if game.get('disk_count', 0) > 1:
                single_games.append(game)
                continue
            
            match = disk_pattern.match(game['name'])
            
            if match:
                base_name = match.group(1).strip()
                grouped[base_name].append(game)
            else:
                single_games.append(game)
        
        for base_name, disk_list in grouped.items():
            if len(disk_list) > 1:
                disk_list.sort(key=lambda g: g['name'])
                
                single_games.append({
                    'name': base_name,
                    'display_name': self._clean_name(base_name),
                    'type': 'multidisk',
                    'path': disk_list[0]['path'],
                    'platform': disk_list[0]['platform'],
                    'file_count': len(disk_list),
                    'disk_count': len(disk_list),
                    'disks': [g['path'] for g in disk_list]
                })
            else:
                single_games.append(disk_list[0])
        
        return single_games
    
    def _is_valid_rom(self, filename, extensions): #vers 1
        """Check if file is a valid ROM"""
        ext = os.path.splitext(filename.lower())[1]
        
        if ext in self.skip_extensions:
            return False
        
        return ext in extensions
    
    def _scan_folder(self, folder_path, platform_name, extensions): #vers 1
        """Scan folder-based game"""
        rom_files = []
        disk_folders = []
        
        for item in folder_path.rglob('*'):
            if item.is_file() and self._is_valid_rom(item.name, extensions):
                rom_files.append(str(item.relative_to(folder_path)))
            elif item.is_dir() and 'disk' in item.name.lower():
                disk_folders.append(item.name)
        
        if not rom_files:
            return None
        
        disk_files = self._detect_multidisk(rom_files)
        
        return {
            'name': folder_path.name,
            'display_name': self._clean_name(folder_path.name),
            'type': 'folder',
            'path': str(folder_path),
            'platform': platform_name,
            'file_count': len(rom_files),
            'disk_count': len(disk_files) if disk_files else 0,
            'disks': disk_files if disk_files else rom_files[:1],
            'disk_folders': disk_folders,
            'rom_files': rom_files
        }
    
    def _scan_zip(self, zip_path, platform_name, extensions): #vers 1
        """Peek inside ZIP to get game information"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                contents = zip_ref.namelist()
                
                rom_files = [f for f in contents if self._is_valid_rom(f, extensions)]
                
                if not rom_files:
                    return None
                
                disk_files = self._detect_multidisk(rom_files)
                
                game_name = zip_path.stem
                
                return {
                    'name': game_name,
                    'display_name': self._clean_name(game_name),
                    'type': 'zip',
                    'path': str(zip_path),
                    'platform': platform_name,
                    'file_count': len(rom_files),
                    'disk_count': len(disk_files) if disk_files else 0,
                    'disks': disk_files if disk_files else [str(zip_path)],
                    'rom_files': rom_files
                }
        except Exception as e:
            print(f"Error scanning ZIP {zip_path}: {e}")
            return None
    
    def discover_platforms(self): #vers 1
        """Find all platform folders in the ROM directory"""
        if not self.rom_path.exists():
            return []
        
        platforms = []
        for item in self.rom_path.iterdir():
            if item.is_dir() and item.name in self.platforms:
                platforms.append(item.name)
        
        return sorted(platforms)
    
    def scan_platform(self, platform_name): #vers 1
        """Scan all games for a specific platform"""
        platform_path = self.rom_path / platform_name
        
        if not platform_path.exists():
            return []
        
        platform_config = self.platforms.get(platform_name)
        if not platform_config:
            return []
        
        games = []
        extensions = platform_config['extensions']
        
        for item in platform_path.iterdir():
            if item.name.startswith('.'):
                continue
            
            if item.suffix.lower() == '.zip':
                game_info = self._scan_zip(item, platform_name, extensions)
                if game_info:
                    games.append(game_info)
            
            elif item.is_dir():
                game_info = self._scan_folder(item, platform_name, extensions)
                if game_info:
                    games.append(game_info)
            
            elif self._is_valid_rom(item.name, extensions):
                games.append(self._create_game_entry(item, platform_name))
        
        grouped_games = self._group_multidisk_games(games)
        
        return sorted(grouped_games, key=lambda g: g['display_name'].lower())
