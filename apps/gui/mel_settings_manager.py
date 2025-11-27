# X-Seti - November27 2025 - Multi-Emulator Launcher - Settings Path Manager
# This file goes in /apps/utils/mel_settings_manager.py - Version: 3
"""
MEL Settings Manager - Handles MEL-specific settings
- Directory paths (ROMs, BIOS, cores, saves, cache)
- Icon display mode (icons_only, text_only, icons_and_text)
- Emulator preferences per platform
- Debug settings (enabled, level)
- Themed titlebar toggle
"""

from pathlib import Path
import json
import subprocess

##Methods list -
# __init__
# get_bios_path
# get_cache_path
# get_core_path
# get_debug_enabled
# get_debug_level
# get_emulator_for_platform
# get_icon_display_mode
# get_rom_path
# get_save_path
# get_themed_titlebar
# save_mel_settings
# scan_installed_emulators
# set_bios_path
# set_cache_path
# set_core_path
# set_debug_enabled
# set_debug_level
# set_emulator_for_platform
# set_icon_display_mode
# set_rom_path
# set_save_path
# set_themed_titlebar
# _load_settings

class MELSettingsManager: #vers 3
    """Manages all MEL-specific settings"""
    
    def __init__(self, settings_file="mel_settings.json"): #vers 3
        self.settings_file = Path(settings_file)
        self.settings = self._load_settings()
        
        # Emulator -> platforms mapping (from installed emulators)
        self.emulator_map = {
            # Amiga
            'amiberry': ['Amiga'],
            'amiberry-lite': ['Amiga'],
            'fs-uae': ['Amiga'],
            
            # Sega
            'blastem': ['Genesis', 'Mega Drive', 'Sega Genesis', 'Sega Mega Drive'],
            
            # Amstrad
            'cap32': ['Amstrad CPC', 'Amstrad 464', 'Amstrad 6128'],
            'caprice32': ['Amstrad CPC', 'Amstrad 464', 'Amstrad 6128'],
            
            # Nintendo Wii U
            'cemu': ['Wii U', 'Nintendo Wii U'],
            
            # Nintendo DS
            'desmume': ['Nintendo DS', 'DS'],
            
            # MSX
            'bluemsx': ['MSX', 'MSX2'],
            
            # PlayStation
            'pcsx2': ['PlayStation 2', 'PS2'],
            'pcsx2-qt': ['PlayStation 2', 'PS2'],
            'duckstation-qt': ['PlayStation 1', 'PlayStation', 'PS1', 'PSX'],
            'epsxe': ['PlayStation 1', 'PlayStation', 'PS1', 'PSX'],
            'ppsspp': ['PSP', 'PlayStation Portable'],
            'ppsspp-qt': ['PSP', 'PlayStation Portable'],
            
            # Nintendo
            'mupen64plus': ['Nintendo 64', 'N64'],
            'snes9x-gtk': ['Super Nintendo', 'SNES'],
            'bsnes': ['Super Nintendo', 'SNES'],
            'fceux': ['Nintendo Entertainment System', 'NES'],
            'mgba-qt': ['Game Boy Advance', 'GBA'],
            'visualboyadvance': ['Game Boy Advance', 'GBA'],
            'melonDS': ['Nintendo DS', 'DS'],
            'dolphin-emu': ['GameCube', 'Nintendo GameCube', 'Wii', 'Nintendo Wii'],
            
            # Atari
            'hatari': ['Atari ST'],
            'stella': ['Atari 2600'],
            'atari800': ['Atari 800'],
            
            # Other
            'vice': ['Commodore 64', 'C64'],
            'fuse': ['ZX Spectrum'],
            '86box': ['IBM PC', 'DOS'],
            'mame': ['Arcade', 'MAME'],
        }
    
    def _load_settings(self): #vers 3
        """Load MEL settings from file"""
        defaults = {
            'rom_path': 'roms',
            'bios_path': 'bios',
            'core_path': 'cores',
            'save_path': 'saves',
            'cache_path': 'cache',
            'icon_display_mode': 'icons_and_text',
            'use_themed_titlebar': True,
            'debug_enabled': False,
            'debug_level': 'INFO',
            'emulator_preferences': {}  # platform -> emulator_name mapping
        }
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    defaults.update(loaded)
            except Exception as e:
                print(f"Error loading MEL settings: {e}")
        
        return defaults
    
    # Path getters
    def get_bios_path(self): #vers 1
        """Get BIOS directory path"""
        return Path(self.settings.get('bios_path', 'bios'))
    
    def get_cache_path(self): #vers 1
        """Get cache directory path"""
        return Path(self.settings.get('cache_path', 'cache'))
    
    def get_core_path(self): #vers 1
        """Get cores directory path"""
        return Path(self.settings.get('core_path', 'cores'))
    
    def get_rom_path(self): #vers 1
        """Get ROM directory path"""
        return Path(self.settings.get('rom_path', 'roms'))
    
    def get_save_path(self): #vers 1
        """Get saves directory path"""
        return Path(self.settings.get('save_path', 'saves'))
    
    # Display settings
    def get_icon_display_mode(self): #vers 1
        """Get icon display mode (icons_only, text_only, icons_and_text)"""
        return self.settings.get('icon_display_mode', 'icons_and_text')
    
    def get_themed_titlebar(self): #vers 1
        """Get themed titlebar preference"""
        return self.settings.get('use_themed_titlebar', True)
    
    # Debug settings
    def get_debug_enabled(self): #vers 1
        """Get debug mode enabled status"""
        return self.settings.get('debug_enabled', False)
    
    def get_debug_level(self): #vers 1
        """Get debug level (ERROR, WARNING, INFO, DEBUG, VERBOSE)"""
        return self.settings.get('debug_level', 'INFO')
    
    # Emulator preferences
    def get_emulator_for_platform(self, platform): #vers 1
        """Get preferred emulator for platform
        
        Args:
            platform: Platform name
            
        Returns:
            Emulator name or 'auto' for auto-detect
        """
        prefs = self.settings.get('emulator_preferences', {})
        return prefs.get(platform, 'auto')
    
    def scan_installed_emulators(self): #vers 1
        """Scan system for installed emulators
        
        Returns:
            Dict of platform -> [emulator_names]
        """
        installed = {}
        
        for emu_name, platforms in self.emulator_map.items():
            try:
                result = subprocess.run(
                    ['which', emu_name],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                if result.returncode == 0:
                    # Emulator is installed
                    for platform in platforms:
                        if platform not in installed:
                            installed[platform] = []
                        installed[platform].append(emu_name)
                        
            except Exception:
                pass
        
        return installed
    
    # Save method
    def save_mel_settings(self): #vers 1
        """Save MEL settings to file"""
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving MEL settings: {e}")
            return False
    
    # Path setters
    def set_bios_path(self, path): #vers 1
        """Set BIOS directory path"""
        self.settings['bios_path'] = str(path)
        self.save_mel_settings()
    
    def set_cache_path(self, path): #vers 1
        """Set cache directory path"""
        self.settings['cache_path'] = str(path)
        self.save_mel_settings()
    
    def set_core_path(self, path): #vers 1
        """Set cores directory path"""
        self.settings['core_path'] = str(path)
        self.save_mel_settings()
    
    def set_rom_path(self, path): #vers 1
        """Set ROM directory path"""
        self.settings['rom_path'] = str(path)
        self.save_mel_settings()
    
    def set_save_path(self, path): #vers 1
        """Set saves directory path"""
        self.settings['save_path'] = str(path)
        self.save_mel_settings()
    
    # Display setters
    def set_icon_display_mode(self, mode): #vers 1
        """Set icon display mode
        
        Args:
            mode: "icons_only", "text_only", or "icons_and_text"
        """
        valid_modes = ['icons_only', 'text_only', 'icons_and_text']
        if mode in valid_modes:
            self.settings['icon_display_mode'] = mode
            self.save_mel_settings()
    
    def set_themed_titlebar(self, enabled): #vers 1
        """Set themed titlebar enabled"""
        self.settings['use_themed_titlebar'] = bool(enabled)
        self.save_mel_settings()
    
    # Debug setters
    def set_debug_enabled(self, enabled): #vers 1
        """Set debug mode enabled"""
        self.settings['debug_enabled'] = bool(enabled)
        self.save_mel_settings()
    
    def set_debug_level(self, level): #vers 1
        """Set debug level"""
        valid_levels = ['ERROR', 'WARNING', 'INFO', 'DEBUG', 'VERBOSE']
        if level in valid_levels:
            self.settings['debug_level'] = level
            self.save_mel_settings()
    
    # Emulator setters
    def set_emulator_for_platform(self, platform, emulator): #vers 1
        """Set preferred emulator for platform
        
        Args:
            platform: Platform name
            emulator: Emulator name or 'auto'
        """
        if 'emulator_preferences' not in self.settings:
            self.settings['emulator_preferences'] = {}
        
        self.settings['emulator_preferences'][platform] = emulator
        self.save_mel_settings()
