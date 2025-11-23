#!/usr/bin/env python3
#this belongs in root /emu_launcher_main.py - Version: 2
# X-Seti - November19 2025 - Multi-Emulator Launcher - Main Entry Point

"""
Multi-Emulator Launcher
Main entry point for the emulator launcher application
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Import application components
from apps.gui.emu_launcher_gui import EmuLauncherGUI
from apps.core.core_downloader import CoreDownloader, create_directory_structure
from apps.core.core_launcher import CoreLauncher
from apps.core.gamepad_config import GamepadConfig

# Optional AppSettings
try:
    from apps.utils.app_settings_system import AppSettings
    APPSETTINGS_AVAILABLE = True
except ImportError:
    APPSETTINGS_AVAILABLE = False
    AppSettings = None

##Methods list -
# check_dependencies
# initialize_directories
# main

##class EmulatorLauncher -
# __init__
# run

class EmulatorLauncher: #vers 2
    """Main launcher class"""
    
    def __init__(self): #vers 2
        """Initialize launcher"""
        self.base_dir = Path.cwd()
        self.app_settings = None
        self.core_downloader = None
        self.core_launcher = None
        self.gamepad_config = None
        
    def run(self): #vers 2
        """Run the launcher"""
        print("=" * 60)
        print("Multi-Emulator Launcher v1.0")
        print("=" * 60)
        
        # Check dependencies
        if not check_dependencies():
            print("\n⚠️  Missing dependencies detected")
            print("Run: pip install -r requirements.txt")
            return 1
            
        # Initialize directories
        if not initialize_directories(self.base_dir):
            print("\n⚠️  Failed to initialize directories")
            return 1
            
        # Initialize core systems
        print("\nInitializing core systems...")
        
        if APPSETTINGS_AVAILABLE and AppSettings:
            self.app_settings = AppSettings()
        else:
            print("  ⚠️  AppSettings not available - using defaults")
            self.app_settings = None
            
        self.core_downloader = CoreDownloader(self.base_dir)
        
        # Initialize CoreLauncher with database from CoreDownloader
        self.core_launcher = CoreLauncher(
            self.base_dir, 
            self.core_downloader.CORE_DATABASE,
            self.core_downloader
        )
        
        from apps.gui.game_manager_dialog import GameConfig
        self.game_config = GameConfig(self.base_dir / "config")
        self.gamepad_config = GamepadConfig(self.base_dir)
        
        # Check for installed cores
        installed_cores = self.core_downloader.get_installed_cores()
        print(f"  ✓ Found {len(installed_cores)} installed cores")
        
        # Check for controllers
        controllers = self.gamepad_config.detect_controllers()
        print(f"  ✓ Detected {len(controllers)} controller(s)")
        
        # Launch GUI
        print("\nLaunching GUI...")
        app = QApplication(sys.argv)
        
        # Apply theme if available
        if self.app_settings:
            stylesheet = self.app_settings.get_stylesheet()
            app.setStyleSheet(stylesheet)
            
        # Create main window with all systems
        window = EmuLauncherGUI(
            core_downloader=self.core_downloader,
            core_launcher=self.core_launcher,
            gamepad_config=self.gamepad_config,
            game_config=self.game_config
        )
        window.show()
        
        print("✓ Multi-Emulator Launcher started\n")
        
        return app.exec()


def check_dependencies() -> bool: #vers 1
    """Check if required dependencies are installed"""
    required_modules = {
        'PyQt6': 'PyQt6',
        'pygame': 'pygame (for controller support)',
    }
    
    missing = []
    
    for module, description in required_modules.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(description)
            
    if missing:
        print("\nMissing dependencies:")
        for dep in missing:
            print(f"  ✗ {dep}")
        return False
        
    return True


def initialize_directories(base_dir: Path) -> bool: #vers 1
    """Initialize directory structure if needed"""
    required_dirs = [
        'apps',
        'cores', 
        'roms',
        'bios',
        'saves',
        'config',
        'screenshots',
        'playlists',
        'system'
    ]
    
    # Check if main directories exist
    missing_dirs = [d for d in required_dirs if not (base_dir / d).exists()]
    
    if missing_dirs:
        print(f"\n⚠️  Missing directories detected: {', '.join(missing_dirs)}")
        response = input("Create directory structure? [Y/n]: ").strip().lower()
        
        if response in ['', 'y', 'yes']:
            try:
                create_directory_structure(base_dir)
                print("✓ Directory structure created")
                return True
            except Exception as e:
                print(f"✗ Error creating directories: {e}")
                return False
        else:
            print("✗ Directory structure required to run")
            return False
            
    return True


def main(): #vers 1
    """Main entry point"""
    launcher = EmulatorLauncher()
    sys.exit(launcher.run())


if __name__ == "__main__":
    main()
