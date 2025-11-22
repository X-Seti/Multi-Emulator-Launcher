# X-Seti - November21 2025 - Multi-Emulator Launcher - Settings Path Manager
# This file goes in /apps/utils/mel_settings_manager.py - Version: 1
"""
MEL Settings Manager Extension - Handles MEL-specific path settings
Extends app_settings_system for emulator launcher configuration.
"""

from pathlib import Path
import json

##Methods list -
# __init__
# get_bios_path
# get_cache_path
# get_core_path
# get_rom_path
# get_save_path
# save_mel_settings
# set_bios_path
# set_cache_path
# set_core_path
# set_rom_path
# set_save_path

class MELSettingsManager: #vers 1
    """Manages MEL-specific directory paths"""
    
    def __init__(self, settings_file="mel_settings.json"): #vers 1
        self.settings_file = Path(settings_file)
        self.settings = self._load_settings()
    
    def _load_settings(self): #vers 1
        """Load MEL settings from file"""
        defaults = {
            'rom_path': 'roms',
            'bios_path': 'bios',
            'core_path': 'cores',
            'save_path': 'saves',
            'cache_path': 'cache'
        }
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    defaults.update(loaded)
            except Exception as e:
                print(f"Error loading MEL settings: {e}")
        
        return defaults
    
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
