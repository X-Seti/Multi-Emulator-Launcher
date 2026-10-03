#!/usr/bin/env python3
#this belongs in apps/tools/caprice32_debugger.py - Version: 1
# X-Seti - December27 2025 - Multi-Emulator Launcher - Caprice32 Debugger

"""
Caprice32 Window Size Debugger
Tests different Caprice32 launch arguments to find what works
"""

import subprocess
import time
from pathlib import Path

##Methods list -
# test_caprice32_args
# get_caprice32_help
# test_config_file

def get_caprice32_help(): #vers 1
    """Get Caprice32 help output to see available options"""
    print("=" * 60)
    print("CAPRICE32 HELP OUTPUT")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            ['cap32', '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        print(result.stdout)
        print(result.stderr)
        
    except Exception as e:
        print(f"Error getting help: {e}")
        
    # Also try -h
    try:
        result = subprocess.run(
            ['cap32', '-h'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        print("\n--- With -h flag ---")
        print(result.stdout)
        print(result.stderr)
        
    except Exception as e:
        print(f"Error with -h: {e}")

def test_caprice32_args(rom_path): #vers 1
    """Test different argument combinations
    
    Args:
        rom_path: Path to a test ROM file
    """
    rom_path = Path(rom_path)
    
    if not rom_path.exists():
        print(f"ROM not found: {rom_path}")
        return
    
    # Different argument combinations to test
    test_configs = [
        {
            'name': 'Default (no args)',
            'args': []
        },
        {
            'name': 'Screen width/height only',
            'args': ['-scr_width', '800', '-scr_height', '600']
        },
        {
            'name': 'With style 1 (resizable)',
            'args': ['-scr_width', '800', '-scr_height', '600', '-scr_style', '1']
        },
        {
            'name': 'With style 2',
            'args': ['-scr_width', '800', '-scr_height', '600', '-scr_style', '2']
        },
        {
            'name': 'With style 3',
            'args': ['-scr_width', '800', '-scr_height', '600', '-scr_style', '3']
        },
        {
            'name': 'Window mode flag',
            'args': ['-w']
        },
        {
            'name': 'Aspect ratio',
            'args': ['-scr_width', '800', '-scr_height', '600', '-scr_aspect', '1']
        },
        {
            'name': 'Remanency',
            'args': ['-scr_width', '800', '-scr_height', '600', '-scr_remanency', '0']
        },
        {
            'name': 'BPP 32',
            'args': ['-scr_width', '800', '-scr_height', '600', '-scr_bpp', '32']
        },
        {
            'name': 'Intensity 10',
            'args': ['-scr_width', '800', '-scr_height', '600', '-scr_intensity', '10']
        },
    ]
    
    print("=" * 60)
    print("TESTING CAPRICE32 ARGUMENTS")
    print("=" * 60)
    print(f"ROM: {rom_path.name}")
    print()
    
    for i, config in enumerate(test_configs, 1):
        print(f"\nTest {i}/{len(test_configs)}: {config['name']}")
        print(f"Arguments: {' '.join(config['args'])}")
        
        cmd = ['cap32'] + config['args'] + [str(rom_path)]
        print(f"Command: {' '.join(cmd)}")
        
        response = input("Press ENTER to launch (or 's' to skip): ")
        if response.lower() == 's':
            print("Skipped")
            continue
        
        try:
            print("Launching...")
            proc = subprocess.Popen(cmd)
            
            print("Emulator launched. Check the window size.")
            print("Close the emulator window when done testing.")
            
            # Wait for process to finish
            proc.wait()
            
            result = input("Did this work? (y/n): ")
            if result.lower() == 'y':
                print(f"✓ SUCCESS! Use these arguments: {config['args']}")
                return config['args']
            
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nAll tests complete.")

def test_config_file(): #vers 1
    """Check Caprice32 config file location and settings"""
    print("=" * 60)
    print("CAPRICE32 CONFIG FILE")
    print("=" * 60)
    
    possible_locations = [
        Path.home() / '.caprice32',
        Path.home() / '.config' / 'caprice32',
        Path('/etc/caprice32'),
        Path('/usr/share/caprice32'),
    ]
    
    for loc in possible_locations:
        if loc.exists():
            print(f"\n✓ Found: {loc}")
            
            # List files
            if loc.is_dir():
                files = list(loc.iterdir())
                for f in files:
                    print(f"  - {f.name}")
                    
                    # If it's a config file, show contents
                    if f.suffix in ['.cfg', '.conf', '.ini']:
                        print(f"\nContents of {f.name}:")
                        print("-" * 40)
                        try:
                            with open(f, 'r') as cf:
                                print(cf.read()[:1000])  # First 1000 chars
                        except:
                            print("Could not read file")
        else:
            print(f"✗ Not found: {loc}")

if __name__ == "__main__":
    import sys
    
    print("Caprice32 Window Size Debugger")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python caprice32_debugger.py help          # Show cap32 help")
        print("  python caprice32_debugger.py config        # Check config files")
        print("  python caprice32_debugger.py test ROM.dsk # Test arguments")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'help':
        get_caprice32_help()
    elif command == 'config':
        test_config_file()
    elif command == 'test' and len(sys.argv) > 2:
        test_caprice32_args(sys.argv[2])
    else:
        print("Invalid command")
