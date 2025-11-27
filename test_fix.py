#!/usr/bin/env python3
# Test script to verify the core detection fix

from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from apps.core.core_downloader import CoreDownloader
from apps.core.core_launcher import CoreLauncher

def test_fix():
    print("Testing core detection fix...")
    print("=" * 50)
    
    # Initialize core downloader and launcher
    base_dir = Path.cwd()
    core_downloader = CoreDownloader(base_dir)
    core_launcher = CoreLauncher(base_dir, core_downloader.CORE_DATABASE, core_downloader)
    
    # Test the problematic platforms that were showing "No core available"
    problematic_platforms = [
        "Atari 5200",
        "Amstrad 6128", 
        "Amstrad 464",
        "Amstrad CPC",
        "BBC Micro",
        "Oric Atmos",
        "MSX",
        "Z81-Spec256",
        "Amiga"
    ]
    
    print(f"Total platforms in database: {len(core_downloader.CORE_DATABASE)}")
    print(f"Total installed cores: {len(core_launcher.get_installed_cores())}")
    print()
    
    all_found = True
    for platform in problematic_platforms:
        print(f"Testing {platform}:")
        
        # Get core info
        core_info = core_downloader.get_core_info(platform)
        if core_info:
            print(f"  ✓ Platform exists in database")
            print(f"    Cores: {core_info['cores']}")
            
            # Try to find available core
            available_core = core_launcher._find_core_for_platform(platform)
            if available_core:
                print(f"  ✓ Found available core: {available_core}")
            else:
                print(f"  ✗ No available core found")
                all_found = False
        else:
            print(f"  ✗ Platform NOT in database")
            all_found = False
        
        print()
    
    print("=" * 50)
    if all_found:
        print("✓ SUCCESS: All problematic platforms now have available cores!")
    else:
        print("✗ Some platforms still don't have available cores")
    
    return all_found

if __name__ == "__main__":
    test_fix()