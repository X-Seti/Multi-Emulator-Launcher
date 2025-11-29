#!/usr/bin/env python3
#this belongs in root /emu_launcher_main.py - Version: 3
# X-Seti - November28 2025 - Multi-Emulator Launcher - Main Entry Point

"""
Multi-Emulator Launcher
Main entry point for the emulator launcher application
Updated to use dynamic core detection and BIOS management
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
from apps.methods.core_downloader import CoreDownloader
from apps.methods.system_core_scanner import SystemCoreScanner
from apps.methods.bios_manager import BiosManager
from apps.methods.platform_scanner import PlatformScanner
from apps.methods.game_scanner import GameScanner
from apps.methods.rom_loader import RomLoader
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

class EmulatorLauncher: #vers 3
    """Main launcher class with dynamic core detection"""
    
    def __init__(self): #vers 3
        """Initialize launcher with dynamic detection systems"""
        self.base_dir = Path.cwd()
        self.app_settings = None
        self.core_downloader = None
        self.core_launcher = None
        self.gamepad_config = None
        self.platform_scanner = None
        self.game_scanner = None
        self.rom_loader = None
        self.bios_manager = None
        self.system_core_scanner = None
        
    def run(self): #vers 3
        """Run the launcher with dynamic core detection"""
        print("=" * 60)
        print("Multi-Emulator Launcher v2.0 - Dynamic Detection System")
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
            
        # Initialize dynamic detection systems
        self.system_core_scanner = SystemCoreScanner(self.base_dir / "cores")
        self.bios_manager = BiosManager(self.base_dir / "bios")
        self.core_downloader = CoreDownloader(self.base_dir / "cores")
        
        # Initialize scanners with dynamic detection
        self.platform_scanner = PlatformScanner(
            self.base_dir / "roms", 
            self.base_dir / "cores"
        )
        
        # Get dynamically detected platforms
        dynamic_platforms = self.platform_scanner.scan_platforms()
        
        # Initialize game scanner and ROM loader with dynamic platforms
        config = {
            'rom_path': str(self.base_dir / "roms"),
            'cache_path': str(self.base_dir / "cache")
        }
        
        self.game_scanner = GameScanner(config, dynamic_platforms)
        self.rom_loader = RomLoader(config, dynamic_platforms)
        
        # Initialize CoreLauncher with dynamic database
        self.core_launcher = CoreLauncher(
            self.base_dir, 
            dynamic_platforms,  # Use dynamic platform database
            self.core_downloader
        )
        
        from apps.gui.game_manager_dialog import GameConfig
        self.game_config = GameConfig(self.base_dir / "config")
        self.gamepad_config = GamepadConfig(self.base_dir)
        
        # Check for installed cores
        installed_cores = self.system_core_scanner.get_installed_cores()
        print(f"  ✓ Found {len(installed_cores)} installed cores: {list(installed_cores.keys())}")
        
        # Check for controllers
        controllers = self.gamepad_config.detect_controllers()
        print(f"  ✓ Detected {len(controllers)} controller(s)")
        
        # Launch GUI
        print("\nLaunching GUI with dynamic detection...")
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
            game_config=self.game_config,
            platform_scanner=self.platform_scanner,
            game_scanner=self.game_scanner,
            rom_loader=self.rom_loader,
            bios_manager=self.bios_manager
            #system_core_scanner=self.system_core_scanner
        )
        window.show()
        
        print("✓ Multi-Emulator Launcher started with dynamic detection\n")
        
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


def initialize_directories(base_dir: Path) -> bool: #vers 2
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
        'system',
        'cache'  # Added for ROM extraction cache
    ]
    
    # Check if main directories exist
    missing_dirs = [d for d in required_dirs if not (base_dir / d).exists()]
    
    if missing_dirs:
        print(f"\n⚠️  Missing directories detected: {', '.join(missing_dirs)}")
        response = input("Create directory structure? [Y/n]: ").strip().lower()
        
        if response in ['', 'y', 'yes']:
            try:
                for d in required_dirs:
                    (base_dir / d).mkdir(exist_ok=True)
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
