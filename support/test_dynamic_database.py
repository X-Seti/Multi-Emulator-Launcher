#!/usr/bin/env python3
"""Test script for dynamic database functionality"""

from pathlib import Path
from apps.core.core_downloader import CoreDownloader

def test_dynamic_database():
    """Test the new dynamic database functionality"""
    print("=" * 60)
    print("Testing Dynamic Database Functionality")
    print("=" * 60)
    
    # Initialize core downloader
    base_dir = Path.cwd()
    downloader = CoreDownloader(base_dir)
    
    print(f"\n1. Scanning cores directory: {downloader.cores_dir}")
    
    # Get installed cores
    installed_cores = downloader.get_installed_cores()
    print(f"2. Found {len(installed_cores)} installed cores:")
    for core in installed_cores:
        print(f"   - {core}")
    
    # Get available cores (mapped to platforms)
    available_cores = downloader.scan_available_cores()
    print(f"\n3. Available cores mapped to platforms ({len(available_cores)} platforms):")
    
    for platform, info in available_cores.items():
        if info["cores"]:  # Only show platforms that have available cores
            print(f"   {platform}: {info['cores']}")
    
    # Get dynamic database
    dynamic_db = downloader.get_dynamic_core_database()
    print(f"\n4. Dynamic database has {len(dynamic_db)} platforms total:")
    
    platforms_with_cores = 0
    for platform, info in dynamic_db.items():
        if info["cores"]:
            platforms_with_cores += 1
            print(f"   ✓ {platform}: {info['cores']}")
    
    print(f"\n   Platforms with available cores: {platforms_with_cores}")
    print(f"   Platforms without cores: {len(dynamic_db) - platforms_with_cores}")
    
    # Compare with static database
    static_cores_count = sum(1 for p, info in downloader.CORE_DATABASE.items() if info["cores"])
    print(f"\n5. Static database has {static_cores_count} platforms with cores (regardless of availability)")
    
    print(f"\n6. Testing specific platform lookups:")
    test_platforms = ["Atari 5200", "Amstrad CPC", "Amiga", "BBC Micro", "MSX", "ZX Spectrum"]
    for platform in test_platforms:
        static_info = downloader.CORE_DATABASE.get(platform, {})
        dynamic_info = dynamic_db.get(platform, {})
        
        static_cores = static_info.get("cores", [])
        dynamic_cores = dynamic_info.get("cores", [])
        
        status = "✓ Available" if dynamic_cores else "✗ Not Available"
        print(f"   {platform}: {status} (static: {static_cores}, dynamic: {dynamic_cores})")
    
    print("\n" + "=" * 60)
    print("Dynamic database test completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_dynamic_database()