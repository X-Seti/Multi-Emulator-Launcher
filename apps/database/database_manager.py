import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """SQLite database manager for the emulator launcher"""
    
    def __init__(self, db_path: str = "apps/database/mel_database.db"):
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_database()
    
    def ensure_db_directory(self):
        """Ensure the database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        os.makedirs(db_dir, exist_ok=True)
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Platforms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS platforms (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                normalized_name TEXT,
                rom_directory TEXT,
                bios_directory TEXT,
                core_path TEXT,
                extension_filter TEXT,
                total_games INTEGER DEFAULT 0,
                has_bios INTEGER DEFAULT 0,
                last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Games table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY,
                platform_id INTEGER,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                file_hash TEXT,
                is_multidisk INTEGER DEFAULT 0,
                disk_number INTEGER,
                total_disks INTEGER,
                has_bios INTEGER DEFAULT 0,
                last_played TIMESTAMP,
                play_count INTEGER DEFAULT 0,
                FOREIGN KEY (platform_id) REFERENCES platforms (id)
            )
        ''')
        
        # Cores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cores (
                id INTEGER PRIMARY KEY,
                platform_name TEXT UNIQUE,
                core_name TEXT,
                core_path TEXT,
                available_cores TEXT, -- JSON array of available cores
                preferred_core TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # BIOS files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bios_files (
                id INTEGER PRIMARY KEY,
                platform_id INTEGER,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                required INTEGER DEFAULT 1,
                size INTEGER,
                md5_hash TEXT,
                FOREIGN KEY (platform_id) REFERENCES platforms (id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_platforms_name ON platforms(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_platform ON games(platform_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_name ON games(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bios_platform ON bios_files(platform_id)')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def add_platform(self, name: str, normalized_name: str = None, rom_directory: str = None, 
                     bios_directory: str = None, core_path: str = None, 
                     extension_filter: str = None, total_games: int = 0, 
                     has_bios: int = 0) -> int:
        """Add a platform to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if normalized_name is None:
            normalized_name = name.lower().replace(' ', '_')
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO platforms 
                (name, normalized_name, rom_directory, bios_directory, core_path, extension_filter, total_games, has_bios)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, normalized_name, rom_directory, bios_directory, core_path, extension_filter, total_games, has_bios))
            
            platform_id = cursor.lastrowid or cursor.execute(
                "SELECT id FROM platforms WHERE name = ?", (name,)
            ).fetchone()[0]
            
            conn.commit()
            logger.info(f"Added/updated platform: {name} (ID: {platform_id})")
            return platform_id
        except Exception as e:
            logger.error(f"Error adding platform {name}: {e}")
            raise
        finally:
            conn.close()
    
    def get_platform(self, platform_name: str) -> Optional[Dict[str, Any]]:
        """Get a platform by name"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM platforms WHERE name = ? OR normalized_name = ?", 
                      (platform_name, platform_name.lower().replace(' ', '_')))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_platforms(self) -> List[Dict[str, Any]]:
        """Get all platforms from the database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM platforms ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_platform_games_count(self, platform_name: str, count: int):
        """Update the total games count for a platform"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE platforms SET total_games = ? WHERE name = ?", 
                      (count, platform_name))
        conn.commit()
        conn.close()
    
    def add_game(self, platform_id: int, name: str, file_path: str, file_size: int = 0,
                 file_hash: str = None, is_multidisk: int = 0, disk_number: int = None,
                 total_disks: int = None, has_bios: int = 0) -> int:
        """Add a game to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO games 
                (platform_id, name, file_path, file_size, file_hash, 
                 is_multidisk, disk_number, total_disks, has_bios)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (platform_id, name, file_path, file_size, file_hash, 
                  is_multidisk, disk_number, total_disks, has_bios))
            
            game_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Added game: {name} to platform ID {platform_id}")
            return game_id
        except Exception as e:
            logger.error(f"Error adding game {name}: {e}")
            raise
        finally:
            conn.close()
    
    def get_platform_games(self, platform_id: int) -> List[Dict[str, Any]]:
        """Get all games for a specific platform"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM games WHERE platform_id = ? ORDER BY name", (platform_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def add_bios_file(self, platform_id: int, filename: str, file_path: str, 
                      required: int = 1, size: int = None, md5_hash: str = None):
        """Add a BIOS file to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO bios_files 
            (platform_id, filename, file_path, required, size, md5_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (platform_id, filename, file_path, required, size, md5_hash))
        
        conn.commit()
        conn.close()
        logger.info(f"Added BIOS file: {filename} for platform ID {platform_id}")
    
    def get_platform_bios(self, platform_id: int) -> List[Dict[str, Any]]:
        """Get all BIOS files for a specific platform"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM bios_files WHERE platform_id = ?", (platform_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def add_core_info(self, platform_name: str, core_name: str = None, core_path: str = None,
                      available_cores: List[str] = None, preferred_core: str = None):
        """Add or update core information for a platform"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        available_cores_json = json.dumps(available_cores) if available_cores else None
        
        cursor.execute('''
            INSERT OR REPLACE INTO cores 
            (platform_name, core_name, core_path, available_cores, preferred_core)
            VALUES (?, ?, ?, ?, ?)
        ''', (platform_name, core_name, core_path, available_cores_json, preferred_core))
        
        conn.commit()
        conn.close()
        logger.info(f"Added/updated core info for platform: {platform_name}")
    
    def get_core_info(self, platform_name: str) -> Optional[Dict[str, Any]]:
        """Get core information for a platform"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cores WHERE platform_name = ?", (platform_name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result = dict(row)
            # Parse the JSON available_cores field
            if result.get('available_cores'):
                result['available_cores'] = json.loads(result['available_cores'])
            return result
        return None
    
    def clear_platform_games(self, platform_id: int):
        """Clear all games for a specific platform (useful when rescanning)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM games WHERE platform_id = ?", (platform_id,))
        conn.commit()
        conn.close()
        logger.info(f"Cleared games for platform ID {platform_id}")
    
    def clear_all_games(self):
        """Clear all games from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM games")
        conn.commit()
        conn.close()
        logger.info("Cleared all games from database")
    
    def clear_all_platforms(self):
        """Clear all platforms from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM platforms")
        cursor.execute("DELETE FROM games")  # Also clear games since they reference platforms
        cursor.execute("DELETE FROM bios_files")  # Also clear BIOS files
        conn.commit()
        conn.close()
        logger.info("Cleared all platforms from database")
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get statistics about the database contents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        stats['platforms'] = cursor.execute("SELECT COUNT(*) FROM platforms").fetchone()[0]
        stats['games'] = cursor.execute("SELECT COUNT(*) FROM games").fetchone()[0]
        stats['bios_files'] = cursor.execute("SELECT COUNT(*) FROM bios_files").fetchone()[0]
        stats['cores'] = cursor.execute("SELECT COUNT(*) FROM cores").fetchone()[0]
        
        conn.close()
        return stats

# Example usage and testing
if __name__ == "__main__":
    db = DatabaseManager()
    
    # Add a test platform
    platform_id = db.add_platform("Amiga", "amiga", "/home/user/roms/amiga")
    
    # Add a test game
    db.add_game(platform_id, "Test Game", "/home/user/roms/amiga/test.uae", 1024000)
    
    # Get the platform back
    platform = db.get_platform("Amiga")
    print(f"Retrieved platform: {platform}")
    
    # Get all platforms
    all_platforms = db.get_all_platforms()
    print(f"All platforms: {all_platforms}")
    
    # Print database stats
    stats = db.get_database_stats()
    print(f"Database stats: {stats}")
