#!/usr/bin/env python3
#this belongs in apps/gui/ports_manager_dialog.py - Version: 1
# X-Seti - November23 2025 - Multi-Emulator Launcher - Ports Manager

"""
Ports Manager Dialog
Shows games that exist on multiple platforms (ports/versions)
Allows easy navigation between different versions of the same game
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QListWidget, QListWidgetItem, QGroupBox,
                            QMessageBox, QTextEdit, QSplitter, QWidget,
                            QTreeWidget, QTreeWidgetItem, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

##Methods list -
# __init__
# find_ports
# _create_ui
# _filter_games
# _on_game_selected
# _on_port_double_clicked
# _on_port_selected
# _scan_all_platforms
# _switch_to_port

##class PortInfo -
# __init__

##class PortsManagerDialog -

class PortInfo: #vers 1
    """Information about a game port"""
    
    def __init__(self, game_name: str, platform: str, rom_path: Path, 
                 extensions: List[str] = None): #vers 1
        """Initialize port info
        
        Args:
            game_name: Name of the game
            platform: Platform name
            rom_path: Path to ROM file
            extensions: Valid extensions for this platform
        """
        self.game_name = game_name
        self.platform = platform
        self.rom_path = rom_path
        self.extensions = extensions or []
        self.file_count = 1
        
        # Check if multi-disk
        if rom_path.exists():
            parent_dir = rom_path.parent
            similar_files = list(parent_dir.glob(f"{rom_path.stem}*"))
            self.file_count = len(similar_files)


class PortsManagerDialog(QDialog): #vers 1
    """Dialog for viewing and managing game ports"""
    
    port_selected = pyqtSignal(str, str)  # platform, game_name
    
    def __init__(self, platform_scanner, available_roms: Dict[str, List[Path]], 
                 core_downloader, parent=None): #vers 1
        """Initialize ports manager
        
        Args:
            platform_scanner: PlatformScanner instance
            available_roms: Dict of platform -> [rom_paths]
            core_downloader: CoreDownloader instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.platform_scanner = platform_scanner
        self.available_roms = available_roms
        self.core_downloader = core_downloader
        
        self.ports_data = {}  # game_name -> [PortInfo]
        self.current_game = None
        
        self.setWindowTitle("Game Ports Manager")
        self.resize(900, 600)
        
        # Scan for ports
        self._scan_all_platforms()
        
        self._create_ui()
        
        # Auto-select first game with ports
        if self.game_list.count() > 0:
            self.game_list.setCurrentRow(0)
    
    def _scan_all_platforms(self): #vers 1
        """Scan all platforms and find games with multiple ports"""
        print("Scanning for game ports...")
        
        # Build index of all games across platforms
        game_index = {}  # normalized_name -> [PortInfo]
        
        for platform, rom_paths in self.available_roms.items():
            platform_info = self.core_downloader.get_core_info(platform)
            extensions = platform_info.get("extensions", []) if platform_info else []
            
            for rom_path in rom_paths:
                game_name = rom_path.stem
                
                # Normalize name for matching (remove common suffixes)
                normalized_name = self._normalize_game_name(game_name)
                
                port_info = PortInfo(game_name, platform, rom_path, extensions)
                
                if normalized_name not in game_index:
                    game_index[normalized_name] = []
                
                game_index[normalized_name].append(port_info)
        
        # Filter to only games with multiple ports
        self.ports_data = {
            name: ports 
            for name, ports in game_index.items() 
            if len(ports) > 1
        }
        
        print(f"Found {len(self.ports_data)} game(s) with multiple ports")
    
    def _normalize_game_name(self, game_name: str) -> str: #vers 1
        """Normalize game name for matching
        
        Removes common suffixes like (USA), [!], (Disk 1), etc.
        
        Args:
            game_name: Original game name
            
        Returns:
            Normalized name
        """
        import re
        
        name = game_name
        
        # Remove common ROM tags
        patterns = [
            r'\(USA\)',
            r'\(Europe\)',
            r'\(Japan\)',
            r'\(World\)',
            r'\[!\]',
            r'\[a\d*\]',
            r'\[b\d*\]',
            r'\[t\d*\]',
            r'\[h\d*\]',
            r'\(Disk \d+\)',
            r'\(Disc \d+\)',
            r'\(Side \w\)',
            r'\(Rev \w+\)',
            r'\(v\d+\.\d+\)',
            r'_Disk_?\d+',
            r'_Disc_?\d+',
        ]
        
        for pattern in patterns:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        
        # Clean up whitespace and underscores
        name = re.sub(r'[\s_]+', ' ', name).strip()
        
        return name.lower()
    
    def _create_ui(self): #vers 1
        """Create dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(f"<b>Games with Multiple Ports</b> ({len(self.ports_data)} games)")
        header.setFont(QFont("Sans", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Info label
        info = QLabel("Select a game to see all available platforms")
        info.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info)
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type to filter games...")
        self.search_box.textChanged.connect(self._filter_games)
        search_layout.addWidget(self.search_box)
        
        layout.addLayout(search_layout)
        
        # Splitter for game list and ports view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Game list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        games_label = QLabel("<b>Games with Ports</b>")
        left_layout.addWidget(games_label)
        
        self.game_list = QListWidget()
        self.game_list.currentRowChanged.connect(self._on_game_selected)
        
        # Populate game list
        for game_name in sorted(self.ports_data.keys(), key=str.lower):
            port_count = len(self.ports_data[game_name])
            item = QListWidgetItem(f"{game_name.title()} ({port_count} ports)")
            item.setData(Qt.ItemDataRole.UserRole, game_name)
            self.game_list.addItem(item)
        
        left_layout.addWidget(self.game_list)
        
        splitter.addWidget(left_widget)
        
        # Right: Ports details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.game_title = QLabel("<b>Select a game</b>")
        self.game_title.setFont(QFont("Sans", 11, QFont.Weight.Bold))
        right_layout.addWidget(self.game_title)
        
        ports_label = QLabel("Available Ports:")
        right_layout.addWidget(ports_label)
        
        self.ports_tree = QTreeWidget()
        self.ports_tree.setHeaderLabels(["Platform", "Game Name", "Files", "ROM Path"])
        self.ports_tree.itemDoubleClicked.connect(self._on_port_double_clicked)
        self.ports_tree.itemSelectionChanged.connect(self._on_port_selected)
        right_layout.addWidget(self.ports_tree)
        
        # Port info
        self.port_info = QTextEdit()
        self.port_info.setReadOnly(True)
        self.port_info.setMaximumHeight(100)
        right_layout.addWidget(self.port_info)
        
        splitter.addWidget(right_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.switch_btn = QPushButton("Switch to This Port")
        self.switch_btn.clicked.connect(self._switch_to_port)
        self.switch_btn.setEnabled(False)
        button_layout.addWidget(self.switch_btn)
        
        button_layout.addStretch()
        
        export_btn = QPushButton("Export List")
        export_btn.clicked.connect(self._export_ports_list)
        button_layout.addWidget(export_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _filter_games(self, text): #vers 1
        """Filter game list by search text"""
        for i in range(self.game_list.count()):
            item = self.game_list.item(i)
            game_name = item.data(Qt.ItemDataRole.UserRole)
            
            # Show item if text matches
            visible = text.lower() in game_name.lower()
            item.setHidden(not visible)
    
    def _on_game_selected(self, index): #vers 1
        """Handle game selection"""
        if index < 0:
            return
        
        item = self.game_list.item(index)
        self.current_game = item.data(Qt.ItemDataRole.UserRole)
        
        # Update title
        self.game_title.setText(f"<b>{self.current_game.title()}</b>")
        
        # Populate ports tree
        self.ports_tree.clear()
        
        ports = self.ports_data.get(self.current_game, [])
        
        for port in sorted(ports, key=lambda p: p.platform):
            tree_item = QTreeWidgetItem([
                port.platform,
                port.game_name,
                str(port.file_count),
                str(port.rom_path)
            ])
            tree_item.setData(0, Qt.ItemDataRole.UserRole, port)
            self.ports_tree.addTopLevelItem(tree_item)
        
        # Resize columns
        for i in range(4):
            self.ports_tree.resizeColumnToContents(i)
        
        # Update info
        self.port_info.clear()
        info_text = f"<b>{len(ports)} port(s) available:</b><br>"
        for port in ports:
            info_text += f"• {port.platform}: {port.game_name}<br>"
        self.port_info.setHtml(info_text)
    
    def _on_port_selected(self): #vers 1
        """Handle port selection in tree"""
        selected = self.ports_tree.selectedItems()
        self.switch_btn.setEnabled(len(selected) > 0)
    
    def _on_port_double_clicked(self, item, column): #vers 1
        """Handle double-click on port"""
        self._switch_to_port()
    
    def _switch_to_port(self): #vers 1
        """Switch to selected port"""
        selected = self.ports_tree.selectedItems()
        if not selected:
            return
        
        port = selected[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Emit signal to switch platform/game
        self.port_selected.emit(port.platform, port.game_name)
        
        QMessageBox.information(
            self,
            "Port Selected",
            f"Switching to:\n\n"
            f"Platform: {port.platform}\n"
            f"Game: {port.game_name}"
        )
        
        self.accept()
    
    def _export_ports_list(self): #vers 1
        """Export ports list to text file"""
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Ports List",
            "game_ports.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w') as f:
                f.write("Game Ports List\n")
                f.write("=" * 70 + "\n\n")
                
                for game_name in sorted(self.ports_data.keys(), key=str.lower):
                    ports = self.ports_data[game_name]
                    f.write(f"{game_name.title()} ({len(ports)} ports)\n")
                    f.write("-" * 70 + "\n")
                    
                    for port in sorted(ports, key=lambda p: p.platform):
                        f.write(f"  {port.platform:20} {port.game_name}\n")
                        f.write(f"    Path: {port.rom_path}\n")
                        if port.file_count > 1:
                            f.write(f"    Files: {port.file_count}\n")
                    
                    f.write("\n")
            
            QMessageBox.information(
                self,
                "Export Complete",
                f"Ports list exported to:\n{filename}"
            )
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Export Failed",
                f"Failed to export ports list:\n{str(e)}"
            )
    
    def find_ports(self, game_name: str) -> List[PortInfo]: #vers 1
        """Find all ports of a specific game
        
        Args:
            game_name: Name of the game
            
        Returns:
            List of PortInfo objects
        """
        normalized = self._normalize_game_name(game_name)
        return self.ports_data.get(normalized, [])


    def _show_statistics(self):
        """Show statistics about ports"""
        total_games = len(self.ports_data)

        # Count by port count
        two_ports = len([p for p in self.ports_data.values() if len(p) == 2])
        three_ports = len([p for p in self.ports_data.values() if len(p) == 3])
        four_plus = len([p for p in self.ports_data.values() if len(p) >= 4])

        # Most ported game
        most_ported = max(self.ports_data.items(), key=lambda x: len(x[1]))

        stats = f"""
        Port Statistics:

        Total games with ports: {total_games}

        Games with 2 ports: {two_ports}
        Games with 3 ports: {three_ports}
        Games with 4+ ports: {four_plus}

        Most ported game: {most_ported[0].title()}
        ({len(most_ported[1])} platforms)
        """

        QMessageBox.information(self, "Statistics", stats)

# Standalone testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Mock data
    available_roms = {
        "Amiga": [Path("roms/Amiga/Lemmings.adf")],
        "Atari ST": [Path("roms/Atari ST/Lemmings.st")],
        "Genesis": [Path("roms/Genesis/Lemmings.bin")],
        "SNES": [Path("roms/SNES/Lemmings.smc")]
    }
    
    dialog = PortsManagerDialog(
        None,  # platform_scanner
        available_roms,
        None,  # core_downloader
    )
    
    dialog.exec()
