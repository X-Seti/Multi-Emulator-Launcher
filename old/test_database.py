#!/usr/bin/env python3
"""
Test script to verify database functionality
"""

import os
import sqlite3
import sys
from pathlib import Path

# Add the workspace to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from apps.database.database_manager import DatabaseManager
from apps.methods.platform_scanner import PlatformScanner

def test_database():
    print("Testing database functionality...")
    
    # Initialize database manager
    db = DatabaseManager()
    
    # Test initial state
    stats = db.get_database_stats()
    print(f"Initial database stats: {stats}")
    
    # Add a test platform
    platform_id = db.add_platform(
        name="Amiga",
        normalized_name="amiga",
        rom_directory="/workspace/roms/Amiga"
    )
    # Update the total games count and has_bios
    db.update_platform_games_count("Amiga", 5)
    
    # Update has_bios directly in the database
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE platforms SET has_bios = 1 WHERE name = ?", ("Amiga",))
    conn.commit()
    conn.close()
    print(f"Added platform with ID: {platform_id}")
    
    # Add core info for the platform
    db.add_core_info(
        platform_name="Amiga",
        available_cores=["puae", "uae"],
        preferred_core="puae"
    )
    
    # Add a test game
    game_id = db.add_game(
        platform_id=platform_id,
        name="Test Game",
        file_path="/workspace/roms/Amiga/test.adf",
        file_size=819200,
        file_hash="abc123"
    )
    print(f"Added game with ID: {game_id}")
    
    # Add a BIOS file
    db.add_bios_file(
        platform_id=platform_id,
        filename="kick13.rom",
        file_path="/workspace/bios/kick13.rom",
        required=1,
        size=262144,
        md5_hash="def456"
    )
    
    # Get updated stats
    stats = db.get_database_stats()
    print(f"Updated database stats: {stats}")
    
    # Get the platform back
    platform = db.get_platform("Amiga")
    print(f"Retrieved platform: {platform}")
    
    # Get all platforms
    all_platforms = db.get_all_platforms()
    print(f"All platforms: {all_platforms}")
    
    # Get games for the platform
    games = db.get_platform_games(platform_id)
    print(f"Games for platform: {games}")
    
    # Get core info
    core_info = db.get_core_info("Amiga")
    print(f"Core info for Amiga: {core_info}")
    
    # Get BIOS files
    bios_files = db.get_platform_bios(platform_id)
    print(f"BIOS files for platform: {bios_files}")
    
    print("Database test completed successfully!")

def test_platform_scanner():
    print("\nTesting platform scanner with database...")
    
    # Create a test ROM structure
    test_roms_dir = Path("/workspace/test_roms")
    os.makedirs(test_roms_dir / "Amiga", exist_ok=True)
    os.makedirs(test_roms_dir / "NES", exist_ok=True)
    
    # Create dummy ROM files
    (test_roms_dir / "Amiga" / "test.adf").touch()
    (test_roms_dir / "NES" / "test.nes").touch()
    
    # Initialize platform scanner with database
    scanner = PlatformScanner(test_roms_dir)
    
    # Scan platforms
    platforms = scanner.scan_platforms()
    print(f"Discovered platforms: {list(platforms.keys())}")
    
    # Check database
    stats = scanner.db_manager.get_database_stats()
    print(f"Database stats after scan: {stats}")
    
    # Get all platforms from database
    db_platforms = scanner.db_manager.get_all_platforms()
    print(f"Platforms in database: {db_platforms}")
    
    print("Platform scanner test completed successfully!")

if __name__ == "__main__":
    test_database()
    test_platform_scanner()
    print("\nAll tests completed successfully!")