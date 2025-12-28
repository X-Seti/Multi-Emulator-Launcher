#!/usr/bin/env python3
#this belongs in apps/gui/mel_settings_manager.py - Version: 5
# X-Seti - December27 2025 - Multi-Emulator Launcher - Settings Path Manager
"""
MEL Settings Manager - Handles MEL-specific settings
- Directory paths (ROMs, BIOS, cores, saves, cache)
- Icon display mode (icons_only, text_only, icons_and_text)
- Emulator preferences per platform
- Emulator window settings (auto-resize, reembed)
- Debug settings (enabled, level)
- Themed titlebar toggle
"""

from pathlib import Path
import json
import subprocess

##Methods list -
# __init__
# add_rom_path
# get_auto_resize_embedded
# get_bios_path
# get_cache_path
# get_core_path
# get_debug_enabled
# get_debug_level
# get_emulator_for_platform
# get_icon_display_mode
# get_reembed_external
# get_rom_path
# get_rom_paths
# get_save_path
# get_themed_titlebar
# remove_rom_path
# save_mel_settings
# scan_installed_emulators
# set_auto_resize_embedded
# set_bios_path
# set_cache_path
# set_core_path
# set_debug_enabled
# set_debug_level
# set_emulator_for_platform
# set_icon_display_mode
# set_reembed_external
# set_rom_path
# set_rom_paths
# set_save_path
# set_themed_titlebar
# _load_settings

class MELSettingsManager: #vers 5
    """Manages all MEL-specific settings"""
    
    def __init__(self, settings_file="mel_settings.json"): #vers 5
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

            # Caprice32 specific settings
            'cap32_scale': 3,           # 1-8, default 3 (1152×810)
            'cap32_style': 11,          # 0-11, default 11 (OpenGL)
            'cap32_window': 1,          # 0=fullscreen, 1=windowed
            'cap32_preserve_aspect': 1, # 0 or 1
            'cap32_oglfilter': 1,       # 0 or 1
        }
    
    def _load_settings(self): #vers 5
        """Load MEL settings from file"""
        defaults = {
            'rom_paths': ['roms'],
            'bios_path': 'bios',
            'core_path': 'cores',
            'save_path': 'saves',
            'cache_path': 'cache',
            'icon_display_mode': 'icons_and_text',
            'use_themed_titlebar': True,
            'debug_enabled': False,
            'debug_level': 'INFO',
            'emulator_preferences': {},
            'auto_resize_embedded': True,
            'reembed_external': True,
            'emulator_window_width': 800,
            'emulator_window_height': 600
        }
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    
                    # Backward compatibility: convert single rom_path to rom_paths list
                    if 'rom_path' in loaded and 'rom_paths' not in loaded:
                        loaded['rom_paths'] = [loaded['rom_path']]
                        del loaded['rom_path']
                    
                    defaults.update(loaded)
            except Exception as e:
                print(f"Error loading MEL settings: {e}")
        
        return defaults
    
    # ROM path methods
    def add_rom_path(self, path): #vers 1
        """Add a ROM directory path"""
        path_str = str(path)
        if 'rom_paths' not in self.settings:
            self.settings['rom_paths'] = []
        if path_str not in self.settings['rom_paths']:
            self.settings['rom_paths'].append(path_str)
            self.save_mel_settings()
    
    def remove_rom_path(self, path): #vers 1
        """Remove a ROM directory path"""
        path_str = str(path)
        if 'rom_paths' in self.settings and path_str in self.settings['rom_paths']:
            self.settings['rom_paths'].remove(path_str)
            self.save_mel_settings()
    
    def set_rom_path(self, path): #vers 1
        """Set single ROM path (backward compatibility)"""
        self.settings['rom_paths'] = [str(path)]
        self.save_mel_settings()
    
    def set_rom_paths(self, paths): #vers 1
        """Set multiple ROM paths"""
        self.settings['rom_paths'] = [str(p) for p in paths]
        self.save_mel_settings()
    
    def get_cap32_scale(self): #vers 1
        """Get Caprice32 scale factor (1-8)"""
        return self.settings.get('cap32_scale', 3)

    def get_cap32_style(self): #vers 1
        """Get Caprice32 rendering style (0-11)"""
        return self.settings.get('cap32_style', 11)

    def get_cap32_window_mode(self): #vers 1
        """Get Caprice32 window mode (0=fullscreen, 1=windowed)"""
        return self.settings.get('cap32_window', 1)

    def get_cap32_preserve_aspect(self): #vers 1
        """Get Caprice32 preserve aspect ratio setting"""
        return self.settings.get('cap32_preserve_aspect', 1)

    def get_cap32_oglfilter(self): #vers 1
        """Get Caprice32 OpenGL filter setting"""
        return self.settings.get('cap32_oglfilter', 1)


    def set_cap32_scale(self, scale): #vers 1
        """Set Caprice32 scale factor

        Args:
            scale: 1-8 (1=384×270, 2=768×540, 3=1152×810, etc)
        """
        self.settings['cap32_scale'] = max(1, min(8, scale))
        self._save()

    def set_cap32_style(self, style): #vers 1
        """Set Caprice32 rendering style

        Args:
            style: 0-11 (see cap32.cfg for options)
        """
        self.settings['cap32_style'] = max(0, min(11, style))
        self._save()

    def set_cap32_window_mode(self, mode): #vers 1
        """Set Caprice32 window mode

        Args:
            mode: 0 (fullscreen) or 1 (windowed)
        """
        self.settings['cap32_window'] = 1 if mode else 0
        self._save()

    def set_cap32_preserve_aspect(self, preserve): #vers 1
        """Set Caprice32 preserve aspect ratio

        Args:
            preserve: 0 or 1
        """
        self.settings['cap32_preserve_aspect'] = 1 if preserve else 0
        self._save()

    def set_cap32_oglfilter(self, filter_on): #vers 1
        """Set Caprice32 OpenGL filter

        Args:
            filter_on: 0 or 1
        """
        self.settings['cap32_oglfilter'] = 1 if filter_on else 0
        self._save()

    def get_rom_path(self): #vers 1
        """Get first ROM path (backward compatibility)"""
        paths = self.get_rom_paths()
        return paths[0] if paths else Path('roms')
    
    def get_rom_paths(self): #vers 1
        """Get all ROM paths as Path objects"""
        paths = self.settings.get('rom_paths', ['roms'])
        if isinstance(paths, str):
            paths = [paths]
        return [Path(p) for p in paths]
    
    def get_bios_path(self): #vers 1
        """Get BIOS directory path"""
        return Path(self.settings.get('bios_path', 'bios'))
    
    def get_core_path(self): #vers 1
        """Get cores directory path"""
        return Path(self.settings.get('core_path', 'cores'))
    
    def get_save_path(self): #vers 1
        """Get saves directory path"""
        return Path(self.settings.get('save_path', 'saves'))
    
    def get_cache_path(self): #vers 1
        """Get cache directory path"""
        return Path(self.settings.get('cache_path', 'cache'))
    
    # Display settings
    def get_icon_display_mode(self): #vers 1
        """Get icon display mode (icons_only, text_only, icons_and_text)"""
        return self.settings.get('icon_display_mode', 'icons_and_text')
    
    def get_themed_titlebar(self): #vers 1
        """Get themed titlebar preference"""
        return self.settings.get('use_themed_titlebar', True)
    
    # Emulator window settings
    def get_auto_resize_embedded(self): #vers 1
        """Get auto-resize embedded windows setting"""
        return self.settings.get('auto_resize_embedded', True)
    
    def get_reembed_external(self): #vers 1
        """Get re-embed external windows setting"""
        return self.settings.get('reembed_external', True)
    
    # Debug settings
    def get_debug_enabled(self): #vers 1
        """Get debug mode enabled status"""
        return self.settings.get('debug_enabled', False)
    
    def get_debug_level(self): #vers 1
        """Get debug level (ERROR, WARNING, INFO, DEBUG, VERBOSE)"""
        return self.settings.get('debug_level', 'INFO')
    
    # Emulator preferences
    def get_emulator_for_platform(self, platform): #vers 1
        """Get preferred emulator for platform"""
        prefs = self.settings.get('emulator_preferences', {})
        return prefs.get(platform, 'auto')
    
    def scan_installed_emulators(self): #vers 1
        """Scan system for installed emulators"""
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
                    for platform in platforms:
                        if platform not in installed:
                            installed[platform] = []
                        installed[platform].append(emu_name)
                        
            except Exception:
                pass
        
        return installed
    
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
    
    def set_save_path(self, path): #vers 1
        """Set saves directory path"""
        self.settings['save_path'] = str(path)
        self.save_mel_settings()
    
    # Display setters
    def set_icon_display_mode(self, mode): #vers 1
        """Set icon display mode"""
        valid_modes = ['icons_only', 'text_only', 'icons_and_text']
        if mode in valid_modes:
            self.settings['icon_display_mode'] = mode
            self.save_mel_settings()
    
    def set_themed_titlebar(self, enabled): #vers 1
        """Set themed titlebar enabled"""
        self.settings['use_themed_titlebar'] = bool(enabled)
        self.save_mel_settings()
    
    # Emulator window setters
    def set_auto_resize_embedded(self, enabled): #vers 1
        """Set auto-resize embedded windows"""
        self.settings['auto_resize_embedded'] = bool(enabled)
        self.save_mel_settings()
    
    def set_reembed_external(self, enabled): #vers 1
        """Set re-embed external windows"""
        self.settings['reembed_external'] = bool(enabled)
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
        """Set preferred emulator for platform"""
        if 'emulator_preferences' not in self.settings:
            self.settings['emulator_preferences'] = {}
        self.settings['emulator_preferences'][platform] = emulator
        self.save_mel_settings()
    
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

    # Emulator window size getters
    def get_emulator_window_width(self): #vers 1
        """Get emulator window width"""
        return self.settings.get('emulator_window_width', 800)
    
    def get_emulator_window_height(self): #vers 1
        """Get emulator window height"""
        return self.settings.get('emulator_window_height', 600)
    
    def get_emulator_display_mode(self): #vers 1
        """Get emulator display mode (windowed, fullscreen, etc)
        
        Returns:
            str: Display mode setting
        """
        return self.settings.get('emulator_display_mode', 'windowed')
    
    # Emulator window size setters
    def set_emulator_window_width(self, width): #vers 1
        """Set emulator window width"""
        self.settings['emulator_window_width'] = int(width)
        self.save_mel_settings()
    
    def set_emulator_window_height(self, height): #vers 1
        """Set emulator window height"""
        self.settings['emulator_window_height'] = int(height)
        self.save_mel_settings()
