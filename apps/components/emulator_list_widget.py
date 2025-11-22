# X-Seti - November21 2025 - Multi-Emulator Launcher - Platform List Widget
# This file goes in /apps/components/emulator_list_widget.py - Version: 2
"""
Emulator Platform List Widget - Shows platforms with icons
Supports multiple display modes: icons_only, text_only, icons_and_text
"""

from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon

##Methods list -
# __init__
# on_selection_changed
# populate_platforms
# set_display_mode

class EmulatorListWidget(QListWidget): #vers 2
    """Panel 1: List of emulator platforms with icon support"""
    
    platform_selected = pyqtSignal(str)
    
    def __init__(self, parent=None, display_mode="icons_and_text"): #vers 2
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.currentRowChanged.connect(self.on_selection_changed)
        self.display_mode = display_mode
        self.setIconSize(QSize(32, 32))
        
    def on_selection_changed(self, row): #vers 2
        """Handle platform selection"""
        if row >= 0:
            item = self.item(row)
            platform = item.data(Qt.ItemDataRole.UserRole)
            if not platform:
                platform = item.text()
            self.platform_selected.emit(platform)
    
    def populate_platforms(self, platforms, icon_factory=None): #vers 2
        """Populate with platform names and optional icons
        
        Args:
            platforms: List of platform names
            icon_factory: PlatformIcons instance for generating icons
        """
        self.clear()
        for platform in platforms:
            item = QListWidgetItem()
            
            # Set icon if available and mode allows
            if icon_factory and self.display_mode != "text_only":
                icon = icon_factory.get_platform_icon(platform, size=32)
                item.setIcon(icon)
            
            # Set text based on display mode
            if self.display_mode == "icons_only":
                item.setText("")
                item.setToolTip(platform)  # Show name on hover
            else:
                item.setText(platform)
            
            # Store platform name in data
            item.setData(Qt.ItemDataRole.UserRole, platform)
            self.addItem(item)
    
    def set_display_mode(self, mode): #vers 1
        """Change display mode and refresh
        
        Args:
            mode: "icons_only", "text_only", or "icons_and_text"
        """
        self.display_mode = mode
        
        # Update existing items
        for i in range(self.count()):
            item = self.item(i)
            platform = item.data(Qt.ItemDataRole.UserRole)
            
            if mode == "icons_only":
                item.setText("")
                item.setToolTip(platform)
            elif mode == "text_only":
                item.setText(platform)
                item.setIcon(QIcon())  # Remove icon
            else:  # icons_and_text
                item.setText(platform)
