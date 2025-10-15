#!/usr/bin/env python3
# X-Seti - October15 2025 - Multi-Emulator Launcher - Main Entry Point
# This belongs in root /emu_launcher_main.py - Version: 2
"""
Multi-Emulator Launcher - A custom frontend for libretro cores with PS4 controller support.
"""

##Methods list -
# load_config
# run
# setup_directories

import os
import sys
import json
from pathlib import Path


class EmulatorLauncher: #vers 2
    def __init__(self): #vers 2
        self.base_dir = Path(__file__).parent.absolute()
        self.config = self.load_config()
        self.setup_directories()
    
    def load_config(self): #vers 2
        """Load or create default configuration"""
        config_path = self.base_dir / 'config' / 'settings.json'
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
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
                    "scale_quality": "linear"
                },
                "input": {
                    "controller_index": 0,
                    "deadzone": 0.15
                }
            }
            
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
    
    def run(self): #vers 2
        """Main application loop"""
        print("Multi-Emulator Launcher")
        print("=" * 50)
        print(f"Base Directory: {self.base_dir}")
        print(f"ROM Path: {self.config['rom_path']}")
        print(f"Core Path: {self.config['core_path']}")
        print(f"BIOS Path: {self.config['bios_path']}")
        print("=" * 50)
        
        from methods.game_scanner import GameScanner
        from core.platform_config import PlatformManager
        
        platform_manager = PlatformManager(self.base_dir / 'config')
        
        scanner = GameScanner(self.config, platform_manager.platforms)
        available_platforms = scanner.discover_platforms()
        
        print(f"\nFound {len(available_platforms)} platforms:")
        for platform in available_platforms:
            game_count = len(scanner.scan_platform(platform))
            print(f"  - {platform}: {game_count} games")
        
        print("\nLaunching GUI...")
        from PyQt6.QtWidgets import QApplication
        from gui.gui_main import EmulatorGUI
        from utils.app_settings_system import AppSettings
        
        app = QApplication(sys.argv)
        
        app_settings = AppSettings()
        
        stylesheet = app_settings.get_stylesheet()
        app.setStyleSheet(stylesheet)
        
        gui = EmulatorGUI(self.config, platform_manager, scanner, app_settings)
        sys.exit(gui.run())
    
    def setup_directories(self): #vers 2
        """Create necessary directories if they don't exist"""
        directories = [
            'cores',
            'bios',
            'roms',
            'saves',
            'cache/extracted',
            'config',
            'themes'
        ]
        
        for directory in directories:
            dir_path = self.base_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    launcher = EmulatorLauncher()
    launcher.run()
