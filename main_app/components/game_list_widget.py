# X-Seti - October15 2025 - Multi-Emulator Launcher - Game List Widget
# This belongs in components/game_list_widget.py - Version: 1
"""
Game List Widget - Custom list widget for displaying games with themed styling.
"""

##Methods list -
# populate_games

from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt


class GameListWidget(QListWidget): #vers 1
    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
    
    def populate_games(self, games): #vers 1
        """Populate the list with games"""
        self.clear()
        
        for game in games:
            display_text = game['display_name']
            
            if game.get('disk_count', 0) > 1:
                display_text += f" ({game['disk_count']} disks)"
            
            type_indicator = ""
            if game['type'] == 'zip':
                type_indicator = " 📦"
            elif game['type'] == 'folder':
                type_indicator = " 📁"
            elif game['type'] == 'multidisk':
                type_indicator = " 💾"
            
            display_text += type_indicator
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, game)
            self.addItem(item)
