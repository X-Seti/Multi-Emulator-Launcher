"""
Core Launcher
Launches games using libretro cores via RetroArch command line
"""

import os
import subprocess
from pathlib import Path
from src.rom_loader import RomLoader


class CoreLauncher:
    def __init__(self, config, platform_manager):
        self.config = config
        self.platform_manager = platform_manager
        self.rom_loader = RomLoader(config, platform_manager.platforms)
    
    def launch_game(self, game_entry):
        """Launch a game using the appropriate core"""
        platform = game_entry['platform']
        platform_config = self.platform_manager.get_platform(platform)
        
        if not platform_config:
            raise Exception(f"Unknown platform: {platform}")
        
        # Get core path
        core_path = self.platform_manager.get_core_path(
            platform,
            self.config['core_path']
        )
        
        if not core_path or not core_path.exists():
            raise Exception(
                f"Core not found: {core_path}\n\n"
                f"Please place {platform_config['core']} in the cores/ directory"
            )
        
        # Load ROM (handles ZIP extraction, etc.)
        try:
            rom_path = self.rom_loader.load_rom(game_entry)
        except Exception as e:
            raise Exception(f"Failed to load ROM: {e}")
        
        # Set up BIOS path
        bios_path = Path(self.config['bios_path']) / platform
        
        # Set up save path
        save_path = Path(self.config['save_path']) / platform
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Build RetroArch command
        retroarch_cmd = self.build_retroarch_command(
            core_path,
            rom_path,
            bios_path,
            save_path,
            platform_config
        )
        
        print(f"Launching: {' '.join(retroarch_cmd)}")
        
        # Launch RetroArch
        try:
            result = subprocess.run(
                retroarch_cmd,
                env=self.build_environment(bios_path, save_path)
            )
            
            if result.returncode != 0:
                print(f"RetroArch exited with code: {result.returncode}")
        
        except FileNotFoundError:
            raise Exception(
                "RetroArch not found!\n\n"
                "Please install RetroArch and ensure it's in your PATH"
            )
        
        except Exception as e:
            raise Exception(f"Failed to launch emulator: {e}")
        
        finally:
            # Cleanup temporary ROM extractions
            self.rom_loader.cleanup()
    
    def build_retroarch_command(self, core_path, rom_path, bios_path, save_path, platform_config):
        """Build RetroArch command line arguments"""
        cmd = [
            'retroarch',
            '-L', str(core_path),  # Load core
            str(rom_path),  # ROM file
        ]
        
        # Display settings
        display_config = self.config.get('display', {})
        
        if display_config.get('fullscreen', True):
            cmd.append('--fullscreen')
        
        # System directory (BIOS)
        cmd.extend(['--system', str(bios_path)])
        
        # Save directory
        cmd.extend(['--savefile', str(save_path)])
        cmd.extend(['--savestate', str(save_path)])
        
        # Additional settings
        if display_config.get('vsync', True):
            cmd.append('--vsync')
        
        # Verbose output for debugging
        cmd.append('--verbose')
        
        return cmd
    
    def build_environment(self, bios_path, save_path):
        """Build environment variables for RetroArch"""
        env = os.environ.copy()
        
        # Set system directory for cores to find BIOS
        env['SYSTEM_DIRECTORY'] = str(bios_path)
        env['SRAM_DIRECTORY'] = str(save_path)
        env['SAVESTATE_DIRECTORY'] = str(save_path)
        
        return env
    
    def check_retroarch_installed(self):
        """Check if RetroArch is installed and accessible"""
        try:
            result = subprocess.run(
                ['retroarch', '--version'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def get_retroarch_version(self):
        """Get RetroArch version"""
        try:
            result = subprocess.run(
                ['retroarch', '--version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
