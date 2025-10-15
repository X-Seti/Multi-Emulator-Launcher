#!/usr/bin/env python3
"""
Multi-Emulator Launcher
A custom frontend for libretro cores with PS4 controller support
"""

import os
import sys
import json
from pathlib import Path

# Main application structure
class EmulatorLauncher:
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.config = self.load_config()
        self.setup_directories()
        
    def load_config(self):
        """Load or create default configuration"""
        config_path = self.base_dir / 'config' / 'settings.json'
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Create default config
            default_config = {
                "rom_path": str(self.base_dir / "roms"),
                "core_path": str(self.base_dir / "cores"),
                "bios_path": str(self.base_dir / "bios"),
                "save_path": str(self.base_dir / "saves"),
                "cache_path": str(self.base_dir / "cache"),
                "display": {
                    "width": 1920,
                    "height": 1080,
                    "fullscreen": True,
                    "vsync": True,
                    "scale_quality": "linear"  # linear, nearest, or best
                },
                "input": {
                    "controller_index": 0,
                    "deadzone": 0.15
                }
            }
            
            # Create config directory
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save default config
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
    
    def setup_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            'cores',
            'bios',
            'roms',
            'saves',
            'cache/extracted',
            'config'
        ]
        
        for directory in directories:
            dir_path = self.base_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def run(self):
        """Main application loop"""
        print("Multi-Emulator Launcher")
        print("=" * 50)
        print(f"Base Directory: {self.base_dir}")
        print(f"ROM Path: {self.config['rom_path']}")
        print(f"Core Path: {self.config['core_path']}")
        print(f"BIOS Path: {self.config['bios_path']}")
        print("=" * 50)
        
        # Initialize components
        from src.game_scanner import GameScanner
        from src.platform_config import PlatformManager
        
        # Load platform configurations
        platform_manager = PlatformManager(self.base_dir / 'config')
        
        # Scan for games
        scanner = GameScanner(self.config, platform_manager.platforms)
        available_platforms = scanner.discover_platforms()
        
        print(f"\nFound {len(available_platforms)} platforms:")
        for platform in available_platforms:
            game_count = len(scanner.scan_platform(platform))
            print(f"  - {platform}: {game_count} games")
        
        # Launch GUI
        print("\nLaunching GUI...")
        from src.gui_main import EmulatorGUI
        
        app = EmulatorGUI(self.config, platform_manager, scanner)
        app.run()


if __name__ == "__main__":
    launcher = EmulatorLauncher()
    launcher.run()
