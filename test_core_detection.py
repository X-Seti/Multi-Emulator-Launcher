#!/usr/bin/env python3
# Test core detection for various platforms

from pathlib import Path
import sys
import json

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from apps.core.core_downloader import CoreDownloader
from apps.core.core_launcher import CoreLauncher

def test_core_detection():
    print("Testing core detection for various platforms...")
    print("=" * 60)
    
    # Initialize core downloader and launcher
    base_dir = Path.cwd()
    core_downloader = CoreDownloader(base_dir)
    core_launcher = CoreLauncher(base_dir, core_downloader.CORE_DATABASE, core_downloader)
    
    # Get list of installed cores directly from the cores directory
    cores_dir = base_dir / "cores"
    installed_core_files = list(cores_dir.glob("*_libretro.so")) + list(cores_dir.glob("*_libretro.dll")) + list(cores_dir.glob("*_libretro.dylib"))
    installed_core_names = [f.stem.replace('_libretro', '') for f in installed_core_files]
    
    # Test platforms that were showing as "No core available"
    test_platforms = [
        "Atari 5200",
        "Atari 7800", 
        "Amstrad 6128",
        "Amstrad 464",
        "Amstrad CPC",
        "BBC Micro",
        "Oric Atmos",
        "MSX",
        "Z81-Spec256",
        "Amiga",
        "Atari ST",
        "ZX Spectrum"
    ]
    
    print(f"Total platforms in database: {len(core_downloader.CORE_DATABASE)}")
    print(f"Total installed cores: {len(installed_core_names)}")
    print(f"Installed cores: {installed_core_names}")
    print()
    
    for platform in test_platforms:
        print(f"Testing platform: {platform}")
        
        # Normalize the platform name
        normalized = core_downloader.normalize_platform_name(platform)
        print(f"  Normalized to: {normalized}")
        
        # Get platform info
        platform_info = core_downloader.get_core_info(platform)
        if platform_info:
            print(f"  ✓ Platform found in database")
            print(f"    Cores: {platform_info.get('cores', [])}")
            print(f"    BIOS required: {platform_info.get('bios_required', False)}")
            
            # Try to find an available core
            available_core = core_launcher._find_core_for_platform(normalized)
            if available_core:
                print(f"  ✓ Found available core: {available_core}")
            else:
                print(f"  ✗ No available core found")
        else:
            print(f"  ✗ Platform NOT found in database")
        
        print()

if __name__ == "__main__":
    test_core_detection()