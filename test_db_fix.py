#!/usr/bin/env python3
"""
Test script to verify that the database permission issue has been fixed.
"""

import sys
import os
sys.path.append('/workspace')

from apps.database.database_manager import DatabaseManager

def test_database_creation():
    """Test that DatabaseManager can create database without permission errors."""
    try:
        print("Testing DatabaseManager with corrected path...")
        db = DatabaseManager()  # This should use the corrected default path
        print(f"Database created successfully at: {db.db_path}")
        
        # Test basic functionality
        platform_id = db.add_platform("Test Platform", "test_platform")
        print(f"Added test platform with ID: {platform_id}")
        
        db.add_game(platform_id, "Test Game", "/path/to/test/game", 1024)
        print("Added test game successfully")
        
        platforms = db.get_all_platforms()
        print(f"Retrieved platforms: {len(platforms)} found")
        
        stats = db.get_database_stats()
        print(f"Database stats: {stats}")
        
        print("SUCCESS: DatabaseManager works correctly with the new path!")
        return True
        
    except PermissionError as e:
        print(f"FAILED: Permission error still exists: {e}")
        return False
    except Exception as e:
        print(f"FAILED: Other error occurred: {e}")
        return False

if __name__ == "__main__":
    success = test_database_creation()
    if success:
        print("\nVERIFICATION: The database permission issue has been fixed!")
    else:
        print("\nVERIFICATION: The database permission issue still exists!")
    sys.exit(0 if success else 1)