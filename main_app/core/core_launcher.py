# X-Seti - October15 2025 - Multi-Emulator Launcher - Core Launcher
# This belongs in core/core_launcher.py - Version: 1
"""
Core Launcher - Launches games using libretro cores via RetroArch command line.
"""

##Methods list -
# build_environment
# build_retroarch_command
# check_retroarch_installed
# get_retroarch_version
# launch_game

import os
import subprocess
from pathlib import Path


class CoreLauncher: #vers 1
    def __init__(self, config, platform_manager): #vers 1
        self.config = config
        self.platform_manager = platform_manager
    
    def build_environment(self, bios_path, save_path): #vers 1
        """Build environment variables for RetroArch"""
        env = os.environ.copy()
        
        env['SYSTEM_DIRECTORY'] = str(bios_path)
        env['SRAM_DIRECTORY'] = str(save_path)
        env['SAVESTATE_DIRECTORY'] = str(save_path)
        
        return env
    
    def build_retroarch_command(self, core_path, rom_path, bios_path, save_path, platform_config): #vers 1
        """Build RetroArch command line arguments"""
        cmd = [
            'retroarch',
            '-L', str(core_path),
            str(rom_path),
        ]
        
        display_config = self.config.get('display', {})
        
        if display_config.get('fullscreen', True):
            cmd.append('--fullscreen')
        
        cmd.extend(['--system', str(bios_path)])
        cmd.extend(['--savefile', str(save_path)])
        cmd.extend(['--savestate', str(save_path)])
        
        if display_config.get('vsync', True):
            cmd.append('--vsync')
        
        cmd.append('--verbose')
        
        return cmd
    
    def check_retroarch_installed(self): #vers 1
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
    
    def get_retroarch_version(self): #vers 1
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
    
    def launch_game(self, game_entry): #vers 1
        """Launch a game using the appropriate core"""
        from methods.rom_loader import RomLoader
        
        platform = game_entry['platform']
        platform_config = self.platform_manager.get_platform(platform)
        
        if not platform_config:
            raise Exception(f"Unknown platform: {platform}")
        
        core_path = self.platform_manager.get_core_path(
            platform,
            self.config['core_path']
        )
        
        if not core_path or not core_path.exists():
            raise Exception(
                f"Core not found: {core_path}\n\n"
                f"Please place {platform_config['core']} in the cores/ directory"
            )
        
        rom_loader = RomLoader(self.config, self.platform_manager.platforms)
        
        try:
            rom_path = rom_loader.load_rom(game_entry)
        except Exception as e:
            raise Exception(f"Failed to load ROM: {e}")
        
        bios_path = Path(self.config['bios_path']) / platform
        
        save_path = Path(self.config['save_path']) / platform
        save_path.mkdir(parents=True, exist_ok=True)
        
        retroarch_cmd = self.build_retroarch_command(
            core_path,
            rom_path,
            bios_path,
            save_path,
            platform_config
        )
        
        print(f"Launching: {' '.join(retroarch_cmd)}")
        
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
            rom_loader.cleanup()
