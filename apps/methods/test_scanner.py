#!/usr/bin/env python3
"""
Test Script for Game Scanner
Run this to test your ROM folder setup without launching the full GUI
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.game_scanner import GameScanner
from src.platform_config import PlatformManager


def main():
    print("=" * 60)
    print("Multi-Emulator Launcher - Scanner Test")
    print("=" * 60)
    print()
    
    # Load configuration
    config_path = Path('config/settings.json')
    if not config_path.exists():
        print("❌ Error: config/settings.json not found")
        print("Run setup.sh first or create config manually")
        return
    
    with open(config_path) as f:
        config = json.load(f)
    
    print(f"ROM Path: {config['rom_path']}")
    print()
    
    # Check if ROM path exists
    rom_path = Path(config['rom_path'])
    if not rom_path.exists():
        print(f"❌ ROM directory not found: {rom_path}")
        print(f"Create it with: mkdir -p {rom_path}")
        return
    
    # Load platform manager
    platform_manager = PlatformManager(Path('config'))
    print(f"✅ Loaded {len(platform_manager.platforms)} platform configurations")
    print()
    
    # Create scanner
    scanner = GameScanner(config, platform_manager.platforms)
    
    # Discover platforms
    print("Scanning for platforms...")
    platforms = scanner.discover_platforms()
    
    if not platforms:
        print("⚠️  No platforms found!")
        print()
        print("To add platforms, create folders in roms/ with these names:")
        for platform_name in sorted(platform_manager.platforms.keys())[:10]:
            print(f"  - {platform_name}")
        print("  ... and more")
        return
    
    print(f"✅ Found {len(platforms)} platform(s):")
    print()
    
    # Scan each platform
    total_games = 0
    
    for platform_name in platforms:
        print(f"📁 {platform_name}")
        print("-" * 60)
        
        # Scan games
        games = scanner.scan_platform(platform_name)
        total_games += len(games)
        
        if not games:
            print("  ⚠️  No games found")
            print()
            continue
        
        print(f"  Found {len(games)} game(s):")
        print()
        
        # Show first 10 games
        for i, game in enumerate(games[:10], 1):
            # Type indicator
            if game['type'] == 'zip':
                icon = "📦"
            elif game['type'] == 'multidisk' or game.get('disk_count', 0) > 1:
                icon = "💾"
            elif game['type'] == 'folder':
                icon = "📁"
            else:
                icon = "📄"
            
            # Game info
            name = game['display_name']
            disk_info = ""
            if game.get('disk_count', 0) > 1:
                disk_info = f" ({game['disk_count']} disks)"
            
            print(f"  {i:2}. {icon} {name}{disk_info}")
        
        if len(games) > 10:
            print(f"  ... and {len(games) - 10} more")
        
        print()
    
    print("=" * 60)
    print(f"Total: {total_games} games across {len(platforms)} platforms")
    print("=" * 60)
    print()
    
    # Check for cores
    core_path = Path(config['core_path'])
    if core_path.exists():
        cores = list(core_path.glob('*_libretro.*'))
        if cores:
            print(f"✅ Found {len(cores)} core(s) in {core_path}")
            for core in cores[:5]:
                print(f"  - {core.name}")
            if len(cores) > 5:
                print(f"  ... and {len(cores) - 5} more")
        else:
            print(f"⚠️  No cores found in {core_path}")
            print("Add libretro cores (.so/.dll/.dylib) to launch games")
    else:
        print(f"⚠️  Core directory not found: {core_path}")
    
    print()
    
    # Check for BIOS
    bios_path = Path(config['bios_path'])
    if bios_path.exists():
        bios_platforms = [d for d in bios_path.iterdir() if d.is_dir()]
        if bios_platforms:
            print(f"✅ Found BIOS for {len(bios_platforms)} platform(s)")
            for platform_dir in bios_platforms[:5]:
                bios_files = list(platform_dir.glob('*'))
                print(f"  - {platform_dir.name}: {len(bios_files)} file(s)")
            if len(bios_platforms) > 5:
                print(f"  ... and {len(bios_platforms) - 5} more")
        else:
            print(f"⚠️  No BIOS platforms found in {bios_path}")
    else:
        print(f"⚠️  BIOS directory not found: {bios_path}")
    
    print()
    print("Test complete! If everything looks good, run: python main.py")
    print()


if __name__ == "__main__":
    main()
