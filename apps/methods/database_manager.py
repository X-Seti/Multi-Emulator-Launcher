#!/usr/bin/env python3
#this belongs in apps/methods/database_manager.py - Version: 1
# X-Seti - November30 2025 - Multi-Emulator Launcher - Dynamic Database Manager

"""
Dynamic Database Manager
Manages a comprehensive database for Game ROMs, BIOS ROMs, and editable paths
Provides functionality to add/edit paths for cores, game ROMs, and BIOS ROMs
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import os
import threading
from contextlib import contextmanager

##Methods list -
# __init__
# _create_tables
# add_rom_path
# remove_rom_path
# get_rom_paths
# add_bios_path
# remove_bios_path
# get_bios_paths
# add_core_path
# remove_core_path
# get_core_paths
# add_game_rom
# remove_game_rom
# get_game_roms
# add_bios_rom
# remove_bios_rom
# get_bios_roms
# get_all_roms
# get_all_bios
# update_rom_path
# update_bios_path
# update_core_path
# get_path_by_id
# get_path_type_by_id
# search_roms
# get_rom_stats
# backup_database
# restore_database
# get_database_path

class DatabaseManager: #vers 1
    """Manages a comprehensive database for Game ROMs, BIOS ROMs, and editable paths"""
    
    def __init__(self, db_path: Path = None):
        """Initialize database manager
        
        Args:
            db_path: Path to database file. If None, uses default location
        """
        self.db_path = db_path or Path("./config/database.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()  # Thread safety for database operations
        
        # Initialize database
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table for ROM paths (game ROMs)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rom_paths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    platform TEXT,
                    description TEXT,
                    enabled BOOLEAN DEFAULT 1,
                    last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table for BIOS paths
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bios_paths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    description TEXT,
                    enabled BOOLEAN DEFAULT 1
                )
            ''')
            
            # Table for core paths
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS core_paths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    description TEXT,
                    enabled BOOLEAN DEFAULT 1
                )
            ''')
            
            # Table for game ROMs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_roms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    size INTEGER,
                    extension TEXT,
                    last_modified TIMESTAMP,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified BOOLEAN DEFAULT 0,
                    checksum TEXT
                )
            ''')
            
            # Table for BIOS ROMs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bios_roms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    platform TEXT,
                    size INTEGER,
                    required BOOLEAN DEFAULT 0,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified BOOLEAN DEFAULT 0,
                    checksum TEXT
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_game_roms_platform ON game_roms(platform)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_game_roms_extension ON game_roms(extension)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bios_roms_platform ON bios_roms(platform)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rom_paths_platform ON rom_paths(platform)')
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections with thread safety"""
        with self.lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            try:
                yield conn
            finally:
                conn.close()
    
    def add_rom_path(self, path: str, platform: str = None, description: str = "") -> int:
        """Add a ROM path to the database
        
        Args:
            path: Path to ROM directory
            platform: Platform name (optional)
            description: Description of the path
            
        Returns:
            ID of the added path
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO rom_paths (path, platform, description)
                    VALUES (?, ?, ?)
                ''', (path, platform, description))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Path already exists
                return self.get_path_by_path(path, 'rom_paths')
    
    def get_path_by_path(self, path: str, table: str) -> Optional[int]:
        """Get ID of a path if it exists in the specified table"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT id FROM {table} WHERE path = ?', (path,))
            result = cursor.fetchone()
            return result['id'] if result else None
    
    def remove_rom_path(self, path_id: int) -> bool:
        """Remove a ROM path by ID
        
        Args:
            path_id: ID of the path to remove
            
        Returns:
            True if successful, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM rom_paths WHERE id = ?', (path_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_rom_paths(self, platform: str = None) -> List[Dict]:
        """Get all ROM paths, optionally filtered by platform
        
        Args:
            platform: Filter by platform name
            
        Returns:
            List of ROM paths as dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if platform:
                cursor.execute('''
                    SELECT * FROM rom_paths 
                    WHERE platform = ? AND enabled = 1
                    ORDER BY platform, path
                ''', (platform,))
            else:
                cursor.execute('''
                    SELECT * FROM rom_paths 
                    WHERE enabled = 1 
                    ORDER BY platform, path
                ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def add_bios_path(self, path: str, description: str = "") -> int:
        """Add a BIOS path to the database
        
        Args:
            path: Path to BIOS directory
            description: Description of the path
            
        Returns:
            ID of the added path
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO bios_paths (path, description)
                    VALUES (?, ?)
                ''', (path, description))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Path already exists
                return self.get_path_by_path(path, 'bios_paths')
    
    def remove_bios_path(self, path_id: int) -> bool:
        """Remove a BIOS path by ID
        
        Args:
            path_id: ID of the path to remove
            
        Returns:
            True if successful, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM bios_paths WHERE id = ?', (path_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_bios_paths(self) -> List[Dict]:
        """Get all BIOS paths
        
        Returns:
            List of BIOS paths as dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bios_paths WHERE enabled = 1 ORDER BY path')
            return [dict(row) for row in cursor.fetchall()]
    
    def add_core_path(self, path: str, description: str = "") -> int:
        """Add a core path to the database
        
        Args:
            path: Path to core directory
            description: Description of the path
            
        Returns:
            ID of the added path
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO core_paths (path, description)
                    VALUES (?, ?)
                ''', (path, description))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Path already exists
                return self.get_path_by_path(path, 'core_paths')
    
    def remove_core_path(self, path_id: int) -> bool:
        """Remove a core path by ID
        
        Args:
            path_id: ID of the path to remove
            
        Returns:
            True if successful, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM core_paths WHERE id = ?', (path_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_core_paths(self) -> List[Dict]:
        """Get all core paths
        
        Returns:
            List of core paths as dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM core_paths WHERE enabled = 1 ORDER BY path')
            return [dict(row) for row in cursor.fetchall()]
    
    def add_game_rom(self, name: str, path: str, platform: str, size: int = None, 
                     extension: str = None, verified: bool = False, checksum: str = None) -> int:
        """Add a game ROM to the database
        
        Args:
            name: Name of the ROM
            path: Full path to the ROM file
            platform: Platform name
            size: Size of the ROM in bytes
            extension: File extension
            verified: Whether the ROM has been verified
            checksum: Checksum of the ROM
            
        Returns:
            ID of the added ROM
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO game_roms (name, path, platform, size, extension, verified, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, path, platform, size, extension, verified, checksum))
            conn.commit()
            return cursor.lastrowid
    
    def remove_game_rom(self, rom_id: int) -> bool:
        """Remove a game ROM by ID
        
        Args:
            rom_id: ID of the ROM to remove
            
        Returns:
            True if successful, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM game_roms WHERE id = ?', (rom_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_game_roms(self, platform: str = None, extension: str = None) -> List[Dict]:
        """Get all game ROMs, optionally filtered by platform or extension
        
        Args:
            platform: Filter by platform name
            extension: Filter by file extension
            
        Returns:
            List of game ROMs as dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = 'SELECT * FROM game_roms'
            params = []
            
            conditions = []
            if platform:
                conditions.append('platform = ?')
                params.append(platform)
            if extension:
                conditions.append('extension = ?')
                params.append(extension)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY platform, name'
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def add_bios_rom(self, name: str, path: str, platform: str = None, size: int = None, 
                     required: bool = False, verified: bool = False, checksum: str = None) -> int:
        """Add a BIOS ROM to the database
        
        Args:
            name: Name of the BIOS ROM
            path: Full path to the BIOS file
            platform: Platform name (optional)
            size: Size of the BIOS in bytes
            required: Whether this BIOS is required
            verified: Whether the BIOS has been verified
            checksum: Checksum of the BIOS
            
        Returns:
            ID of the added BIOS ROM
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bios_roms (name, path, platform, size, required, verified, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, path, platform, size, required, verified, checksum))
            conn.commit()
            return cursor.lastrowid
    
    def remove_bios_rom(self, rom_id: int) -> bool:
        """Remove a BIOS ROM by ID
        
        Args:
            rom_id: ID of the BIOS ROM to remove
            
        Returns:
            True if successful, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM bios_roms WHERE id = ?', (rom_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_bios_roms(self, platform: str = None) -> List[Dict]:
        """Get all BIOS ROMs, optionally filtered by platform
        
        Args:
            platform: Filter by platform name
            
        Returns:
            List of BIOS ROMs as dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if platform:
                cursor.execute('''
                    SELECT * FROM bios_roms 
                    WHERE platform = ? 
                    ORDER BY platform, name
                ''', (platform,))
            else:
                cursor.execute('SELECT * FROM bios_roms ORDER BY platform, name')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_roms(self) -> Dict[str, List[Dict]]:
        """Get all ROMs (both game and BIOS) organized by platform
        
        Returns:
            Dictionary with platform names as keys and ROM lists as values
        """
        roms = {}
        
        # Get game ROMs
        game_roms = self.get_game_roms()
        for rom in game_roms:
            platform = rom['platform']
            if platform not in roms:
                roms[platform] = []
            rom['type'] = 'game'
            roms[platform].append(rom)
        
        # Get BIOS ROMs
        bios_roms = self.get_bios_roms()
        for rom in bios_roms:
            platform = rom['platform'] or 'BIOS'
            if platform not in roms:
                roms[platform] = []
            rom['type'] = 'bios'
            roms[platform].append(rom)
        
        return roms
    
    def get_all_bios(self) -> Dict[str, List[Dict]]:
        """Get all BIOS ROMs organized by platform
        
        Returns:
            Dictionary with platform names as keys and BIOS ROM lists as values
        """
        bios = {}
        bios_roms = self.get_bios_roms()
        
        for rom in bios_roms:
            platform = rom['platform'] or 'General'
            if platform not in bios:
                bios[platform] = []
            bios[platform].append(rom)
        
        return bios
    
    def update_rom_path(self, path_id: int, path: str = None, platform: str = None, 
                        description: str = None, enabled: bool = None) -> bool:
        """Update a ROM path entry
        
        Args:
            path_id: ID of the path to update
            path: New path (optional)
            platform: New platform (optional)
            description: New description (optional)
            enabled: New enabled status (optional)
            
        Returns:
            True if successful, False otherwise
        """
        updates = []
        params = []
        
        if path is not None:
            updates.append('path = ?')
            params.append(path)
        if platform is not None:
            updates.append('platform = ?')
            params.append(platform)
        if description is not None:
            updates.append('description = ?')
            params.append(description)
        if enabled is not None:
            updates.append('enabled = ?')
            params.append(enabled)
        
        if not updates:
            return False
        
        params.append(path_id)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE rom_paths SET {", ".join(updates)} WHERE id = ?', params)
            conn.commit()
            return cursor.rowcount > 0
    
    def update_bios_path(self, path_id: int, path: str = None, description: str = None, 
                         enabled: bool = None) -> bool:
        """Update a BIOS path entry
        
        Args:
            path_id: ID of the path to update
            path: New path (optional)
            description: New description (optional)
            enabled: New enabled status (optional)
            
        Returns:
            True if successful, False otherwise
        """
        updates = []
        params = []
        
        if path is not None:
            updates.append('path = ?')
            params.append(path)
        if description is not None:
            updates.append('description = ?')
            params.append(description)
        if enabled is not None:
            updates.append('enabled = ?')
            params.append(enabled)
        
        if not updates:
            return False
        
        params.append(path_id)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE bios_paths SET {", ".join(updates)} WHERE id = ?', params)
            conn.commit()
            return cursor.rowcount > 0
    
    def update_core_path(self, path_id: int, path: str = None, description: str = None, 
                         enabled: bool = None) -> bool:
        """Update a core path entry
        
        Args:
            path_id: ID of the path to update
            path: New path (optional)
            description: New description (optional)
            enabled: New enabled status (optional)
            
        Returns:
            True if successful, False otherwise
        """
        updates = []
        params = []
        
        if path is not None:
            updates.append('path = ?')
            params.append(path)
        if description is not None:
            updates.append('description = ?')
            params.append(description)
        if enabled is not None:
            updates.append('enabled = ?')
            params.append(enabled)
        
        if not updates:
            return False
        
        params.append(path_id)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE core_paths SET {", ".join(updates)} WHERE id = ?', params)
            conn.commit()
            return cursor.rowcount > 0
    
    def get_path_by_id(self, path_id: int, path_type: str) -> Optional[Dict]:
        """Get a path by its ID and type
        
        Args:
            path_id: ID of the path
            path_type: Type of path ('rom_paths', 'bios_paths', 'core_paths')
            
        Returns:
            Path information as dictionary, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM {path_type} WHERE id = ?', (path_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_path_type_by_id(self, path_id: int) -> Optional[str]:
        """Determine which table a path ID belongs to
        
        Args:
            path_id: ID to check
            
        Returns:
            Table name ('rom_paths', 'bios_paths', 'core_paths') or None
        """
        # Check each table
        for table in ['rom_paths', 'bios_paths', 'core_paths']:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'SELECT id FROM {table} WHERE id = ?', (path_id,))
                if cursor.fetchone():
                    return table
        return None
    
    def search_roms(self, query: str, rom_type: str = 'both') -> List[Dict]:
        """Search for ROMs by name
        
        Args:
            query: Search query string
            rom_type: 'game', 'bios', or 'both'
            
        Returns:
            List of matching ROMs
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if rom_type == 'game':
                cursor.execute('''
                    SELECT *, 'game' as type FROM game_roms 
                    WHERE name LIKE ? 
                    ORDER BY platform, name
                ''', (f'%{query}%',))
            elif rom_type == 'bios':
                cursor.execute('''
                    SELECT *, 'bios' as type FROM bios_roms 
                    WHERE name LIKE ? 
                    ORDER BY platform, name
                ''', (f'%{query}%',))
            else:  # both
                cursor.execute('''
                    SELECT *, 'game' as type FROM game_roms WHERE name LIKE ?
                    UNION ALL
                    SELECT *, 'bios' as type FROM bios_roms WHERE name LIKE ?
                    ORDER BY platform, name
                ''', (f'%{query}%', f'%{query}%'))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_rom_stats(self) -> Dict[str, int]:
        """Get statistics about ROMs in the database
        
        Returns:
            Dictionary with statistics
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Count game ROMs
            cursor.execute('SELECT COUNT(*) as count FROM game_roms')
            game_rom_count = cursor.fetchone()['count']
            
            # Count BIOS ROMs
            cursor.execute('SELECT COUNT(*) as count FROM bios_roms')
            bios_rom_count = cursor.fetchone()['count']
            
            # Count unique platforms
            cursor.execute('SELECT COUNT(DISTINCT platform) as count FROM game_roms WHERE platform IS NOT NULL')
            platform_count = cursor.fetchone()['count']
            
            # Count ROM paths
            cursor.execute('SELECT COUNT(*) as count FROM rom_paths WHERE enabled = 1')
            rom_path_count = cursor.fetchone()['count']
            
            # Count BIOS paths
            cursor.execute('SELECT COUNT(*) as count FROM bios_paths WHERE enabled = 1')
            bios_path_count = cursor.fetchone()['count']
            
            # Count core paths
            cursor.execute('SELECT COUNT(*) as count FROM core_paths WHERE enabled = 1')
            core_path_count = cursor.fetchone()['count']
            
            return {
                'game_roms': game_rom_count,
                'bios_roms': bios_rom_count,
                'total_roms': game_rom_count + bios_rom_count,
                'platforms': platform_count,
                'rom_paths': rom_path_count,
                'bios_paths': bios_path_count,
                'core_paths': core_path_count
            }
    
    def backup_database(self, backup_path: Path) -> bool:
        """Backup the database to a file
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create backup directory if it doesn't exist
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the database file
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Error backing up database: {e}")
            return False
    
    def restore_database(self, backup_path: Path) -> bool:
        """Restore the database from a backup file
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not backup_path.exists():
                print(f"Backup file does not exist: {backup_path}")
                return False
            
            # Copy the backup to the current database location
            import shutil
            shutil.copy2(backup_path, self.db_path)
            return True
        except Exception as e:
            print(f"Error restoring database: {e}")
            return False
    
    def get_database_path(self) -> Path:
        """Get the current database file path
        
        Returns:
            Path to the database file
        """
        return self.db_path


def test_database_manager():
    """Test function for Database Manager"""
    print("Testing Database Manager...")
    
    # Create database manager
    db_manager = DatabaseManager(Path("./test_database.db"))
    
    # Test adding paths
    rom_path_id = db_manager.add_rom_path("/home/user/roms/nes", "Nintendo Entertainment System", "NES ROMs")
    bios_path_id = db_manager.add_bios_path("/home/user/bios", "Main BIOS directory")
    core_path_id = db_manager.add_core_path("/home/user/cores", "Custom cores")
    
    print(f"Added ROM path with ID: {rom_path_id}")
    print(f"Added BIOS path with ID: {bios_path_id}")
    print(f"Added core path with ID: {core_path_id}")
    
    # Test adding ROMs
    game_rom_id = db_manager.add_game_rom("Super Mario Bros", "/home/user/roms/nes/smb.nes", "Nintendo Entertainment System", 256000, ".nes")
    bios_rom_id = db_manager.add_bios_rom("NES BIOS", "/home/user/bios/nes_bios.bin", "Nintendo Entertainment System", 24576, True)
    
    print(f"Added game ROM with ID: {game_rom_id}")
    print(f"Added BIOS ROM with ID: {bios_rom_id}")
    
    # Test getting paths
    rom_paths = db_manager.get_rom_paths()
    print(f"ROM paths: {rom_paths}")
    
    bios_paths = db_manager.get_bios_paths()
    print(f"BIOS paths: {bios_paths}")
    
    core_paths = db_manager.get_core_paths()
    print(f"Core paths: {core_paths}")
    
    # Test getting ROMs
    game_roms = db_manager.get_game_roms()
    print(f"Game ROMs: {game_roms}")
    
    bios_roms = db_manager.get_bios_roms()
    print(f"BIOS ROMs: {bios_roms}")
    
    # Test stats
    stats = db_manager.get_rom_stats()
    print(f"Database stats: {stats}")
    
    # Clean up test database
    import os
    if os.path.exists("./test_database.db"):
        os.remove("./test_database.db")
    
    print("Database Manager test completed!")


if __name__ == "__main__":
    test_database_manager()