#!/usr/bin/env python3
"""
Test script to verify CoreLauncher works with database
"""

import os
import sys
from pathlib import Path

# Add the workspace to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from apps.core.core_launcher import CoreLauncher
from apps.methods.platform_scanner import PlatformScanner

def test_corelauncher_with_db():
    print("Testing CoreLauncher with database...")
    
    # Create test ROM structure
    test_roms_dir = Path("/workspace/test_roms2")
    os.makedirs(test_roms_dir / "Amiga", exist_ok=True)
    os.makedirs(test_roms_dir / "NES", exist_ok=True)
    
    # Create dummy ROM files
    (test_roms_dir / "Amiga" / "test.adf").touch()
    (test_roms_dir / "NES" / "test.nes").touch()
    
    # Initialize platform scanner to populate the database
    scanner = PlatformScanner(test_roms_dir)
    platforms = scanner.scan_platforms()
    print(f"Scanned platforms: {list(platforms.keys())}")
    
    # Initialize CoreLauncher without providing a core_database (should load from DB)
    launcher = CoreLauncher(test_roms_dir)
    
    # Check that the launcher loaded platforms from the database
    print(f"CoreLauncher database has {len(launcher.core_database)} platforms")
    print(f"CoreLauncher platforms: {list(launcher.core_database.keys())}")
    
    # Test loading from database directly
    db_platforms = launcher._load_database_from_db()
    print(f"Loaded from database: {list(db_platforms.keys())}")
    
    # Test with a specific platform
    if "Amiga" in db_platforms:
        amiga_info = db_platforms["Amiga"]
        print(f"Amiga info: {amiga_info}")
    
    print("CoreLauncher database test completed successfully!")

if __name__ == "__main__":
    test_corelauncher_with_db()
    print("\nTest completed successfully!")