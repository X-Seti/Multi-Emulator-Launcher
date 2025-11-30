#!/usr/bin/env python3
#this belongs in apps/gui/database_manager_dialog.py - Version: 1
# X-Seti - November30 2025 - Multi-Emulator Launcher - Database Manager Dialog

"""
Database Manager Dialog
GUI for managing the dynamic database for Game ROMs, BIOS ROMs, and editable paths
Allows adding/editing paths for cores, game ROMs, and BIOS ROMs
"""

from pathlib import Path
from typing import Dict, List
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                            QTabWidget, QWidget, QFormLayout, QLineEdit, 
                            QComboBox, QCheckBox, QGroupBox, QFileDialog,
                            QMessageBox, QSplitter, QTextEdit, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

##Methods list -
# __init__
# _create_ui
# _create_paths_tab
# _create_roms_tab
# _create_bios_tab
# _refresh_paths
# _refresh_roms
# _refresh_bios
# _add_rom_path
# _remove_rom_path
# _add_bios_path
# _remove_bios_path
# _add_core_path
# _remove_core_path
# _add_game_rom
# _remove_game_rom
# _add_bios_rom
# _remove_bios_rom
# _browse_rom_path
# _browse_bios_path
# _browse_core_path
# _browse_game_rom
# _browse_bios_rom
# _update_rom_path
# _update_bios_path
# _update_core_path
# _search_roms
# _show_rom_stats

class DatabaseManagerDialog(QDialog): #vers 1
    """Dialog for managing the dynamic database"""
    
    def __init__(self, database_manager, parent=None): #vers 1
        """Initialize database manager dialog
        
        Args:
            database_manager: DatabaseManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.database_manager = database_manager
        
        self.setWindowTitle("Database Manager")
        self.resize(1000, 700)
        
        self._create_ui()
        self._refresh_paths()
        self._refresh_roms()
        self._refresh_bios()
    
    def _create_ui(self): #vers 1
        """Create the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Dynamic Database Manager")
        title.setFont(QFont("Sans", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Manage ROM paths, BIOS paths, core paths, and ROM files")
        desc.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(desc)
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        
        # Paths tab
        self.paths_tab = self._create_paths_tab()
        self.tab_widget.addTab(self.paths_tab, "Paths")
        
        # ROMs tab
        self.roms_tab = self._create_roms_tab()
        self.tab_widget.addTab(self.roms_tab, "Game ROMs")
        
        # BIOS tab
        self.bios_tab = self._create_bios_tab()
        self.tab_widget.addTab(self.bios_tab, "BIOS ROMs")
        
        layout.addWidget(self.tab_widget)
        
        # Stats label
        self.stats_label = QLabel()
        #self.stats_label.setStyleSheet("background-color: #f0f0f0; padding: 5px;")
        layout.addWidget(self.stats_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._refresh_all)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Update stats
        self._update_stats()
    
    def _create_paths_tab(self): #vers 1
        """Create the paths management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Splitter for different path types
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # ROM Paths section
        rom_paths_group = QGroupBox("ROM Paths")
        rom_paths_layout = QVBoxLayout(rom_paths_group)
        
        # ROM Paths table
        self.rom_paths_table = QTableWidget()
        self.rom_paths_table.setColumnCount(4)
        self.rom_paths_table.setHorizontalHeaderLabels(["ID", "Path", "Platform", "Description"])
        header = self.rom_paths_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        rom_paths_layout.addWidget(self.rom_paths_table)
        
        # ROM Paths buttons
        rom_paths_btn_layout = QHBoxLayout()
        
        self.add_rom_path_btn = QPushButton("Add ROM Path")
        self.add_rom_path_btn.clicked.connect(self._add_rom_path)
        rom_paths_btn_layout.addWidget(self.add_rom_path_btn)
        
        self.remove_rom_path_btn = QPushButton("Remove ROM Path")
        self.remove_rom_path_btn.clicked.connect(self._remove_rom_path)
        rom_paths_btn_layout.addWidget(self.remove_rom_path_btn)
        
        self.browse_rom_path_btn = QPushButton("Browse...")
        self.browse_rom_path_btn.clicked.connect(self._browse_rom_path)
        rom_paths_btn_layout.addWidget(self.browse_rom_path_btn)
        
        rom_paths_layout.addLayout(rom_paths_btn_layout)
        splitter.addWidget(rom_paths_group)
        
        # BIOS Paths section
        bios_paths_group = QGroupBox("BIOS Paths")
        bios_paths_layout = QVBoxLayout(bios_paths_group)
        
        # BIOS Paths table
        self.bios_paths_table = QTableWidget()
        self.bios_paths_table.setColumnCount(3)
        self.bios_paths_table.setHorizontalHeaderLabels(["ID", "Path", "Description"])
        header = self.bios_paths_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        bios_paths_layout.addWidget(self.bios_paths_table)
        
        # BIOS Paths buttons
        bios_paths_btn_layout = QHBoxLayout()
        
        self.add_bios_path_btn = QPushButton("Add BIOS Path")
        self.add_bios_path_btn.clicked.connect(self._add_bios_path)
        bios_paths_btn_layout.addWidget(self.add_bios_path_btn)
        
        self.remove_bios_path_btn = QPushButton("Remove BIOS Path")
        self.remove_bios_path_btn.clicked.connect(self._remove_bios_path)
        bios_paths_btn_layout.addWidget(self.remove_bios_path_btn)
        
        self.browse_bios_path_btn = QPushButton("Browse...")
        self.browse_bios_path_btn.clicked.connect(self._browse_bios_path)
        bios_paths_btn_layout.addWidget(self.browse_bios_path_btn)
        
        bios_paths_layout.addLayout(bios_paths_btn_layout)
        splitter.addWidget(bios_paths_group)
        
        # Core Paths section
        core_paths_group = QGroupBox("Core Paths")
        core_paths_layout = QVBoxLayout(core_paths_group)
        
        # Core Paths table
        self.core_paths_table = QTableWidget()
        self.core_paths_table.setColumnCount(3)
        self.core_paths_table.setHorizontalHeaderLabels(["ID", "Path", "Description"])
        header = self.core_paths_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        core_paths_layout.addWidget(self.core_paths_table)
        
        # Core Paths buttons
        core_paths_btn_layout = QHBoxLayout()
        
        self.add_core_path_btn = QPushButton("Add Core Path")
        self.add_core_path_btn.clicked.connect(self._add_core_path)
        core_paths_btn_layout.addWidget(self.add_core_path_btn)
        
        self.remove_core_path_btn = QPushButton("Remove Core Path")
        self.remove_core_path_btn.clicked.connect(self._remove_core_path)
        core_paths_btn_layout.addWidget(self.remove_core_path_btn)
        
        self.browse_core_path_btn = QPushButton("Browse...")
        self.browse_core_path_btn.clicked.connect(self._browse_core_path)
        core_paths_btn_layout.addWidget(self.browse_core_path_btn)
        
        core_paths_layout.addLayout(core_paths_btn_layout)
        splitter.addWidget(core_paths_group)
        
        layout.addWidget(splitter)
        
        return tab
    
    def _create_roms_tab(self): #vers 1
        """Create the ROMs management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.roms_search_box = QLineEdit()
        self.roms_search_box.setPlaceholderText("Enter ROM name to search...")
        self.roms_search_box.textChanged.connect(self._search_roms)
        search_layout.addWidget(self.roms_search_box)
        
        search_type_layout = QHBoxLayout()
        search_type_layout.addWidget(QLabel("Type:"))
        self.roms_search_type = QComboBox()
        self.roms_search_type.addItems(["All", "Game", "BIOS"])
        search_type_layout.addWidget(self.roms_search_type)
        
        search_btn_layout = QHBoxLayout()
        search_btn_layout.addLayout(search_layout)
        search_btn_layout.addLayout(search_type_layout)
        
        layout.addLayout(search_btn_layout)
        
        # Game ROMs table
        self.game_roms_table = QTableWidget()
        self.game_roms_table.setColumnCount(6)
        self.game_roms_table.setHorizontalHeaderLabels(["ID", "Name", "Path", "Platform", "Size", "Extension"])
        header = self.game_roms_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.game_roms_table)
        
        # Game ROMs buttons
        roms_btn_layout = QHBoxLayout()
        
        self.add_game_rom_btn = QPushButton("Add Game ROM")
        self.add_game_rom_btn.clicked.connect(self._add_game_rom)
        roms_btn_layout.addWidget(self.add_game_rom_btn)
        
        self.remove_game_rom_btn = QPushButton("Remove Game ROM")
        self.remove_game_rom_btn.clicked.connect(self._remove_game_rom)
        roms_btn_layout.addWidget(self.remove_game_rom_btn)
        
        self.browse_game_rom_btn = QPushButton("Browse...")
        self.browse_game_rom_btn.clicked.connect(self._browse_game_rom)
        roms_btn_layout.addWidget(self.browse_game_rom_btn)
        
        layout.addLayout(roms_btn_layout)
        
        return tab
    
    def _create_bios_tab(self): #vers 1
        """Create the BIOS management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # BIOS ROMs table
        self.bios_roms_table = QTableWidget()
        self.bios_roms_table.setColumnCount(7)
        self.bios_roms_table.setHorizontalHeaderLabels(["ID", "Name", "Path", "Platform", "Size", "Required", "Verified"])
        header = self.bios_roms_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.bios_roms_table)
        
        # BIOS ROMs buttons
        bios_btn_layout = QHBoxLayout()
        
        self.add_bios_rom_btn = QPushButton("Add BIOS ROM")
        self.add_bios_rom_btn.clicked.connect(self._add_bios_rom)
        bios_btn_layout.addWidget(self.add_bios_rom_btn)
        
        self.remove_bios_rom_btn = QPushButton("Remove BIOS ROM")
        self.remove_bios_rom_btn.clicked.connect(self._remove_bios_rom)
        bios_btn_layout.addWidget(self.remove_bios_rom_btn)
        
        self.browse_bios_rom_btn = QPushButton("Browse...")
        self.browse_bios_rom_btn.clicked.connect(self._browse_bios_rom)
        bios_btn_layout.addWidget(self.browse_bios_rom_btn)
        
        layout.addLayout(bios_btn_layout)
        
        return tab
    
    def _refresh_paths(self): #vers 1
        """Refresh all path tables"""
        # Refresh ROM paths
        rom_paths = self.database_manager.get_rom_paths()
        self.rom_paths_table.setRowCount(len(rom_paths))
        for row, path in enumerate(rom_paths):
            self.rom_paths_table.setItem(row, 0, QTableWidgetItem(str(path['id'])))
            self.rom_paths_table.setItem(row, 1, QTableWidgetItem(path['path']))
            self.rom_paths_table.setItem(row, 2, QTableWidgetItem(path.get('platform', '')))
            self.rom_paths_table.setItem(row, 3, QTableWidgetItem(path.get('description', '')))
        
        # Refresh BIOS paths
        bios_paths = self.database_manager.get_bios_paths()
        self.bios_paths_table.setRowCount(len(bios_paths))
        for row, path in enumerate(bios_paths):
            self.bios_paths_table.setItem(row, 0, QTableWidgetItem(str(path['id'])))
            self.bios_paths_table.setItem(row, 1, QTableWidgetItem(path['path']))
            self.bios_paths_table.setItem(row, 2, QTableWidgetItem(path.get('description', '')))
        
        # Refresh core paths
        core_paths = self.database_manager.get_core_paths()
        self.core_paths_table.setRowCount(len(core_paths))
        for row, path in enumerate(core_paths):
            self.core_paths_table.setItem(row, 0, QTableWidgetItem(str(path['id'])))
            self.core_paths_table.setItem(row, 1, QTableWidgetItem(path['path']))
            self.core_paths_table.setItem(row, 2, QTableWidgetItem(path.get('description', '')))
    
    def _refresh_roms(self): #vers 1
        """Refresh game ROMs table"""
        game_roms = self.database_manager.get_game_roms()
        self.game_roms_table.setRowCount(len(game_roms))
        for row, rom in enumerate(game_roms):
            self.game_roms_table.setItem(row, 0, QTableWidgetItem(str(rom['id'])))
            self.game_roms_table.setItem(row, 1, QTableWidgetItem(rom['name']))
            self.game_roms_table.setItem(row, 2, QTableWidgetItem(rom['path']))
            self.game_roms_table.setItem(row, 3, QTableWidgetItem(rom['platform']))
            self.game_roms_table.setItem(row, 4, QTableWidgetItem(str(rom.get('size', 0))))
            self.game_roms_table.setItem(row, 5, QTableWidgetItem(rom.get('extension', '')))
    
    def _refresh_bios(self): #vers 1
        """Refresh BIOS ROMs table"""
        bios_roms = self.database_manager.get_bios_roms()
        self.bios_roms_table.setRowCount(len(bios_roms))
        for row, rom in enumerate(bios_roms):
            self.bios_roms_table.setItem(row, 0, QTableWidgetItem(str(rom['id'])))
            self.bios_roms_table.setItem(row, 1, QTableWidgetItem(rom['name']))
            self.bios_roms_table.setItem(row, 2, QTableWidgetItem(rom['path']))
            self.bios_roms_table.setItem(row, 3, QTableWidgetItem(rom.get('platform', '')))
            self.bios_roms_table.setItem(row, 4, QTableWidgetItem(str(rom.get('size', 0))))
            self.bios_roms_table.setItem(row, 5, QTableWidgetItem(str(rom.get('required', False))))
            self.bios_roms_table.setItem(row, 6, QTableWidgetItem(str(rom.get('verified', False))))
    
    def _refresh_all(self): #vers 1
        """Refresh all tables"""
        self._refresh_paths()
        self._refresh_roms()
        self._refresh_bios()
        self._update_stats()
    
    def _add_rom_path(self): #vers 1
        """Add a new ROM path"""
        # Create a simple dialog to get path details
        from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add ROM Path")
        dialog.resize(400, 150)
        
        layout = QFormLayout(dialog)
        
        path_edit = QLineEdit()
        path_edit.setPlaceholderText("Enter path to ROM directory")
        layout.addRow("Path:", path_edit)
        
        platform_edit = QLineEdit()
        platform_edit.setPlaceholderText("Enter platform name (optional)")
        layout.addRow("Platform:", platform_edit)
        
        desc_edit = QLineEdit()
        desc_edit.setPlaceholderText("Enter description (optional)")
        layout.addRow("Description:", desc_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            path = path_edit.text().strip()
            platform = platform_edit.text().strip() or None
            description = desc_edit.text().strip() or ""
            
            if path:
                try:
                    path_id = self.database_manager.add_rom_path(path, platform, description)
                    QMessageBox.information(self, "Success", f"ROM path added with ID: {path_id}")
                    self._refresh_paths()
                    self._update_stats()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to add ROM path: {str(e)}")
            else:
                QMessageBox.warning(self, "Error", "Path cannot be empty")
    
    def _remove_rom_path(self): #vers 1
        """Remove selected ROM path"""
        current_row = self.rom_paths_table.currentRow()
        if current_row >= 0:
            item = self.rom_paths_table.item(current_row, 0)  # ID column
            if item:
                path_id = int(item.text())
                reply = QMessageBox.question(self, "Confirm", f"Remove ROM path with ID {path_id}?")
                if reply == QMessageBox.StandardButton.Yes:
                    if self.database_manager.remove_rom_path(path_id):
                        QMessageBox.information(self, "Success", f"ROM path {path_id} removed")
                        self._refresh_paths()
                        self._update_stats()
                    else:
                        QMessageBox.warning(self, "Error", f"Failed to remove ROM path {path_id}")
    
    def _add_bios_path(self): #vers 1
        """Add a new BIOS path"""
        from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add BIOS Path")
        dialog.resize(400, 120)
        
        layout = QFormLayout(dialog)
        
        path_edit = QLineEdit()
        path_edit.setPlaceholderText("Enter path to BIOS directory")
        layout.addRow("Path:", path_edit)
        
        desc_edit = QLineEdit()
        desc_edit.setPlaceholderText("Enter description (optional)")
        layout.addRow("Description:", desc_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            path = path_edit.text().strip()
            description = desc_edit.text().strip() or ""
            
            if path:
                try:
                    path_id = self.database_manager.add_bios_path(path, description)
                    QMessageBox.information(self, "Success", f"BIOS path added with ID: {path_id}")
                    self._refresh_paths()
                    self._update_stats()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to add BIOS path: {str(e)}")
            else:
                QMessageBox.warning(self, "Error", "Path cannot be empty")
    
    def _remove_bios_path(self): #vers 1
        """Remove selected BIOS path"""
        current_row = self.bios_paths_table.currentRow()
        if current_row >= 0:
            item = self.bios_paths_table.item(current_row, 0)  # ID column
            if item:
                path_id = int(item.text())
                reply = QMessageBox.question(self, "Confirm", f"Remove BIOS path with ID {path_id}?")
                if reply == QMessageBox.StandardButton.Yes:
                    if self.database_manager.remove_bios_path(path_id):
                        QMessageBox.information(self, "Success", f"BIOS path {path_id} removed")
                        self._refresh_paths()
                        self._update_stats()
                    else:
                        QMessageBox.warning(self, "Error", f"Failed to remove BIOS path {path_id}")
    
    def _add_core_path(self): #vers 1
        """Add a new core path"""
        from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Core Path")
        dialog.resize(400, 120)
        
        layout = QFormLayout(dialog)
        
        path_edit = QLineEdit()
        path_edit.setPlaceholderText("Enter path to core directory")
        layout.addRow("Path:", path_edit)
        
        desc_edit = QLineEdit()
        desc_edit.setPlaceholderText("Enter description (optional)")
        layout.addRow("Description:", desc_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            path = path_edit.text().strip()
            description = desc_edit.text().strip() or ""
            
            if path:
                try:
                    path_id = self.database_manager.add_core_path(path, description)
                    QMessageBox.information(self, "Success", f"Core path added with ID: {path_id}")
                    self._refresh_paths()
                    self._update_stats()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to add core path: {str(e)}")
            else:
                QMessageBox.warning(self, "Error", "Path cannot be empty")
    
    def _remove_core_path(self): #vers 1
        """Remove selected core path"""
        current_row = self.core_paths_table.currentRow()
        if current_row >= 0:
            item = self.core_paths_table.item(current_row, 0)  # ID column
            if item:
                path_id = int(item.text())
                reply = QMessageBox.question(self, "Confirm", f"Remove core path with ID {path_id}?")
                if reply == QMessageBox.StandardButton.Yes:
                    if self.database_manager.remove_core_path(path_id):
                        QMessageBox.information(self, "Success", f"Core path {path_id} removed")
                        self._refresh_paths()
                        self._update_stats()
                    else:
                        QMessageBox.warning(self, "Error", f"Failed to remove core path {path_id}")
    
    def _add_game_rom(self): #vers 1
        """Add a new game ROM"""
        from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Game ROM")
        dialog.resize(400, 200)
        
        layout = QFormLayout(dialog)
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Enter ROM name")
        layout.addRow("Name:", name_edit)
        
        path_edit = QLineEdit()
        path_edit.setPlaceholderText("Enter path to ROM file")
        layout.addRow("Path:", path_edit)
        
        platform_edit = QLineEdit()
        platform_edit.setPlaceholderText("Enter platform name")
        layout.addRow("Platform:", platform_edit)
        
        extension_edit = QLineEdit()
        extension_edit.setPlaceholderText("Enter file extension (e.g., .nes)")
        layout.addRow("Extension:", extension_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_edit.text().strip()
            path = path_edit.text().strip()
            platform = platform_edit.text().strip()
            extension = extension_edit.text().strip()
            
            if name and path and platform:
                try:
                    rom_id = self.database_manager.add_game_rom(name, path, platform, extension=extension)
                    QMessageBox.information(self, "Success", f"Game ROM added with ID: {rom_id}")
                    self._refresh_roms()
                    self._update_stats()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to add game ROM: {str(e)}")
            else:
                QMessageBox.warning(self, "Error", "Name, path, and platform cannot be empty")
    
    def _remove_game_rom(self): #vers 1
        """Remove selected game ROM"""
        current_row = self.game_roms_table.currentRow()
        if current_row >= 0:
            item = self.game_roms_table.item(current_row, 0)  # ID column
            if item:
                rom_id = int(item.text())
                reply = QMessageBox.question(self, "Confirm", f"Remove game ROM with ID {rom_id}?")
                if reply == QMessageBox.StandardButton.Yes:
                    if self.database_manager.remove_game_rom(rom_id):
                        QMessageBox.information(self, "Success", f"Game ROM {rom_id} removed")
                        self._refresh_roms()
                        self._update_stats()
                    else:
                        QMessageBox.warning(self, "Error", f"Failed to remove game ROM {rom_id}")
    
    def _add_bios_rom(self): #vers 1
        """Add a new BIOS ROM"""
        from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QCheckBox, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add BIOS ROM")
        dialog.resize(400, 180)
        
        layout = QFormLayout(dialog)
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Enter BIOS name")
        layout.addRow("Name:", name_edit)
        
        path_edit = QLineEdit()
        path_edit.setPlaceholderText("Enter path to BIOS file")
        layout.addRow("Path:", path_edit)
        
        platform_edit = QLineEdit()
        platform_edit.setPlaceholderText("Enter platform name (optional)")
        layout.addRow("Platform:", platform_edit)
        
        required_check = QCheckBox("Required BIOS")
        layout.addRow(required_check)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_edit.text().strip()
            path = path_edit.text().strip()
            platform = platform_edit.text().strip() or None
            required = required_check.isChecked()
            
            if name and path:
                try:
                    rom_id = self.database_manager.add_bios_rom(name, path, platform, required=required)
                    QMessageBox.information(self, "Success", f"BIOS ROM added with ID: {rom_id}")
                    self._refresh_bios()
                    self._update_stats()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to add BIOS ROM: {str(e)}")
            else:
                QMessageBox.warning(self, "Error", "Name and path cannot be empty")
    
    def _remove_bios_rom(self): #vers 1
        """Remove selected BIOS ROM"""
        current_row = self.bios_roms_table.currentRow()
        if current_row >= 0:
            item = self.bios_roms_table.item(current_row, 0)  # ID column
            if item:
                rom_id = int(item.text())
                reply = QMessageBox.question(self, "Confirm", f"Remove BIOS ROM with ID {rom_id}?")
                if reply == QMessageBox.StandardButton.Yes:
                    if self.database_manager.remove_bios_rom(rom_id):
                        QMessageBox.information(self, "Success", f"BIOS ROM {rom_id} removed")
                        self._refresh_bios()
                        self._update_stats()
                    else:
                        QMessageBox.warning(self, "Error", f"Failed to remove BIOS ROM {rom_id}")
    
    def _browse_rom_path(self): #vers 1
        """Browse for a ROM path"""
        path = QFileDialog.getExistingDirectory(self, "Select ROM Directory")
        if path:
            # Show dialog to add the path
            from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Add ROM Path")
            dialog.resize(400, 120)
            
            layout = QFormLayout(dialog)
            
            path_edit = QLineEdit(path)
            layout.addRow("Path:", path_edit)
            
            platform_edit = QLineEdit()
            platform_edit.setPlaceholderText("Enter platform name (optional)")
            layout.addRow("Platform:", platform_edit)
            
            desc_edit = QLineEdit()
            desc_edit.setPlaceholderText("Enter description (optional)")
            layout.addRow("Description:", desc_edit)
            
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                path = path_edit.text().strip()
                platform = platform_edit.text().strip() or None
                description = desc_edit.text().strip() or ""
                
                if path:
                    try:
                        path_id = self.database_manager.add_rom_path(path, platform, description)
                        QMessageBox.information(self, "Success", f"ROM path added with ID: {path_id}")
                        self._refresh_paths()
                        self._update_stats()
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to add ROM path: {str(e)}")
    
    def _browse_bios_path(self): #vers 1
        """Browse for a BIOS path"""
        path = QFileDialog.getExistingDirectory(self, "Select BIOS Directory")
        if path:
            # Show dialog to add the path
            from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Add BIOS Path")
            dialog.resize(400, 100)
            
            layout = QFormLayout(dialog)
            
            path_edit = QLineEdit(path)
            layout.addRow("Path:", path_edit)
            
            desc_edit = QLineEdit()
            desc_edit.setPlaceholderText("Enter description (optional)")
            layout.addRow("Description:", desc_edit)
            
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                path = path_edit.text().strip()
                description = desc_edit.text().strip() or ""
                
                if path:
                    try:
                        path_id = self.database_manager.add_bios_path(path, description)
                        QMessageBox.information(self, "Success", f"BIOS path added with ID: {path_id}")
                        self._refresh_paths()
                        self._update_stats()
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to add BIOS path: {str(e)}")
    
    def _browse_core_path(self): #vers 1
        """Browse for a core path"""
        path = QFileDialog.getExistingDirectory(self, "Select Core Directory")
        if path:
            # Show dialog to add the path
            from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Add Core Path")
            dialog.resize(400, 100)
            
            layout = QFormLayout(dialog)
            
            path_edit = QLineEdit(path)
            layout.addRow("Path:", path_edit)
            
            desc_edit = QLineEdit()
            desc_edit.setPlaceholderText("Enter description (optional)")
            layout.addRow("Description:", desc_edit)
            
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                path = path_edit.text().strip()
                description = desc_edit.text().strip() or ""
                
                if path:
                    try:
                        path_id = self.database_manager.add_core_path(path, description)
                        QMessageBox.information(self, "Success", f"Core path added with ID: {path_id}")
                        self._refresh_paths()
                        self._update_stats()
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to add core path: {str(e)}")
    
    def _browse_game_rom(self): #vers 1
        """Browse for a game ROM file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Game ROM", "", "ROM Files (*.*)")
        if file_path:
            # Show dialog to add the ROM
            from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Add Game ROM")
            dialog.resize(400, 150)
            
            layout = QFormLayout(dialog)
            
            name_edit = QLineEdit(Path(file_path).stem)
            layout.addRow("Name:", name_edit)
            
            path_edit = QLineEdit(file_path)
            layout.addRow("Path:", path_edit)
            
            platform_edit = QLineEdit()
            platform_edit.setPlaceholderText("Enter platform name")
            layout.addRow("Platform:", platform_edit)
            
            extension_edit = QLineEdit(Path(file_path).suffix)
            layout.addRow("Extension:", extension_edit)
            
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                name = name_edit.text().strip()
                path = path_edit.text().strip()
                platform = platform_edit.text().strip()
                extension = extension_edit.text().strip()
                
                if name and path and platform:
                    try:
                        rom_id = self.database_manager.add_game_rom(name, path, platform, extension=extension)
                        QMessageBox.information(self, "Success", f"Game ROM added with ID: {rom_id}")
                        self._refresh_roms()
                        self._update_stats()
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to add game ROM: {str(e)}")
                else:
                    QMessageBox.warning(self, "Error", "Name, path, and platform cannot be empty")
    
    def _browse_bios_rom(self): #vers 1
        """Browse for a BIOS ROM file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select BIOS ROM", "", "BIOS Files (*.rom *.bin *.img *.iso)")
        if file_path:
            # Show dialog to add the ROM
            from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QCheckBox, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Add BIOS ROM")
            dialog.resize(400, 150)
            
            layout = QFormLayout(dialog)
            
            name_edit = QLineEdit(Path(file_path).stem)
            layout.addRow("Name:", name_edit)
            
            path_edit = QLineEdit(file_path)
            layout.addRow("Path:", path_edit)
            
            platform_edit = QLineEdit()
            platform_edit.setPlaceholderText("Enter platform name (optional)")
            layout.addRow("Platform:", platform_edit)
            
            required_check = QCheckBox("Required BIOS")
            layout.addRow(required_check)
            
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                name = name_edit.text().strip()
                path = path_edit.text().strip()
                platform = platform_edit.text().strip() or None
                required = required_check.isChecked()
                
                if name and path:
                    try:
                        rom_id = self.database_manager.add_bios_rom(name, path, platform, required=required)
                        QMessageBox.information(self, "Success", f"BIOS ROM added with ID: {rom_id}")
                        self._refresh_bios()
                        self._update_stats()
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to add BIOS ROM: {str(e)}")
                else:
                    QMessageBox.warning(self, "Error", "Name and path cannot be empty")
    
    def _search_roms(self): #vers 1
        """Search for ROMs based on the search box"""
        query = self.roms_search_box.text().strip()
        search_type = self.roms_search_type.currentText()
        
        if not query:
            # If no query, show all ROMs
            self._refresh_roms()
            return
        
        # Search for ROMs
        if search_type == "Game":
            roms = self.database_manager.get_game_roms()
            # Filter by query
            roms = [rom for rom in roms if query.lower() in rom['name'].lower()]
        elif search_type == "BIOS":
            roms = self.database_manager.get_bios_roms()
            # Filter by query
            roms = [rom for rom in roms if query.lower() in rom['name'].lower()]
        else:  # All
            # Search in both game and BIOS ROMs
            game_roms = self.database_manager.get_game_roms()
            bios_roms = self.database_manager.get_bios_roms()
            roms = [rom for rom in game_roms if query.lower() in rom['name'].lower()] + \
                   [rom for rom in bios_roms if query.lower() in rom['name'].lower()]
        
        # Update the table
        self.game_roms_table.setRowCount(len(roms))
        for row, rom in enumerate(roms):
            self.game_roms_table.setItem(row, 0, QTableWidgetItem(str(rom['id'])))
            self.game_roms_table.setItem(row, 1, QTableWidgetItem(rom['name']))
            self.game_roms_table.setItem(row, 2, QTableWidgetItem(rom['path']))
            self.game_roms_table.setItem(row, 3, QTableWidgetItem(rom.get('platform', '')))
            self.game_roms_table.setItem(row, 4, QTableWidgetItem(str(rom.get('size', 0))))
            self.game_roms_table.setItem(row, 5, QTableWidgetItem(rom.get('extension', '')))
    
    def _update_stats(self): #vers 1
        """Update the stats label"""
        stats = self.database_manager.get_rom_stats()
        stats_text = (f"Total ROMs: {stats['total_roms']} "
                     f"(Game: {stats['game_roms']}, BIOS: {stats['bios_roms']}) | "
                     f"Platforms: {stats['platforms']} | "
                     f"ROM Paths: {stats['rom_paths']}, BIOS Paths: {stats['bios_paths']}, Core Paths: {stats['core_paths']}")
        self.stats_label.setText(stats_text)
