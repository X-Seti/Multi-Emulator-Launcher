# X-Seti - November21 2025 - Multi-Emulator Launcher - Icon Display Manager
# This file goes in /apps/utils/icon_display_manager.py - Version: 1
"""
Icon Display Manager - Handles icon/text display modes for lists
Supports: icons_only, text_only, icons_and_text
"""

from enum import Enum

##Methods list -
# get_display_mode
# set_display_mode

class IconDisplayMode(Enum): #vers 1
    """Display mode options for list items"""
    ICONS_ONLY = "icons_only"
    TEXT_ONLY = "text_only"
    ICONS_AND_TEXT = "icons_and_text"

class IconDisplayManager: #vers 1
    """Manages icon display mode settings"""
    
    def __init__(self, default_mode=IconDisplayMode.ICONS_AND_TEXT): #vers 1
        self.current_mode = default_mode
    
    def get_display_mode(self): #vers 1
        """Get current display mode"""
        return self.current_mode
    
    def set_display_mode(self, mode): #vers 1
        """Set display mode
        
        Args:
            mode: IconDisplayMode enum value
        """
        if isinstance(mode, str):
            # Convert string to enum
            mode = IconDisplayMode(mode)
        self.current_mode = mode
