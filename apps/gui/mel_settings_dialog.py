#!/usr/bin/env python3
#this belongs in apps/gui/mel_settings_dialog.py - Version: 5
# X-Seti - November22 2025 - Multi-Emulator Launcher - Settings Dialog

"""
MEL Settings Dialog - Folder path configuration for MEL 1.0
Includes titlebar theming toggle
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QGroupBox, QLineEdit,
                             QRadioButton, QButtonGroup, QCheckBox)
from PyQt6.QtCore import Qt
from pathlib import Path

##Methods list -
# __init__
# _create_path_selector
# _get_settings
# _save_settings
# _select_bios_path
# _select_cache_path
# _select_core_path
# _select_rom_path
# _select_save_path
# _setup_ui

class MELSettingsDialog(QDialog): #vers 4
    """Settings dialog for configuring MEL paths and display options"""
    
    def __init__(self, settings_manager, parent=None): #vers 4
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("Multi-Emulator Launcher - Settings")
        self.setMinimumWidth(600)
        self.setModal(True)
        
        # Path inputs
        self.rom_path_input = None
        self.bios_path_input = None
        self.core_path_input = None
        self.save_path_input = None
        self.cache_path_input = None
        
        # Icon display mode
        self.icon_button_group = None
        self.icons_text_radio = None
        self.icons_only_radio = None
        self.text_only_radio = None
        
        # Themed titlebar checkbox
        self.themed_titlebar_check = None
        
        self._setup_ui()
        self._get_settings()
    
    def _create_path_selector(self, label_text, current_path, select_method): #vers 1
        """Create a path selector row"""
        container = QHBoxLayout()
        
        label = QLabel(label_text)
        label.setMinimumWidth(100)
        
        path_input = QLineEdit()
        path_input.setText(str(current_path))
        path_input.setReadOnly(True)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(select_method)
        browse_btn.setMaximumWidth(100)
        
        container.addWidget(label)
        container.addWidget(path_input)
        container.addWidget(browse_btn)
        
        return container, path_input
    
    def _get_settings(self): #vers 4
        """Load current settings into dialog"""
        self.rom_path_input.setText(str(self.settings_manager.get_rom_path()))
        self.bios_path_input.setText(str(self.settings_manager.get_bios_path()))
        self.core_path_input.setText(str(self.settings_manager.get_core_path()))
        self.save_path_input.setText(str(self.settings_manager.get_save_path()))
        self.cache_path_input.setText(str(self.settings_manager.get_cache_path()))
        
        # Load icon display mode
        icon_mode = self.settings_manager.settings.get('icon_display_mode', 'icons_and_text')
        if icon_mode == 'icons_and_text':
            self.icons_text_radio.setChecked(True)
        elif icon_mode == 'icons_only':
            self.icons_only_radio.setChecked(True)
        else:
            self.text_only_radio.setChecked(True)
        
        # Load themed titlebar setting
        use_themed = self.settings_manager.settings.get('use_themed_titlebar', True)
        self.themed_titlebar_check.setChecked(use_themed)
    
    def _save_settings(self): #vers 4
        """Save settings and close dialog"""
        # Update paths
        self.settings_manager.set_rom_path(Path(self.rom_path_input.text()))
        self.settings_manager.set_bios_path(Path(self.bios_path_input.text()))
        self.settings_manager.set_core_path(Path(self.core_path_input.text()))
        self.settings_manager.set_save_path(Path(self.save_path_input.text()))
        self.settings_manager.set_cache_path(Path(self.cache_path_input.text()))
        
        # Save icon display mode
        if self.icons_text_radio.isChecked():
            self.settings_manager.settings['icon_display_mode'] = 'icons_and_text'
        elif self.icons_only_radio.isChecked():
            self.settings_manager.settings['icon_display_mode'] = 'icons_only'
        else:
            self.settings_manager.settings['icon_display_mode'] = 'text_only'
        
        # Save themed titlebar setting
        self.settings_manager.settings['use_themed_titlebar'] = self.themed_titlebar_check.isChecked()
        
        # Save to file - CORRECT METHOD NAME
        self.settings_manager.save_mel_settings()
        
        self.accept()
    
    def _select_bios_path(self): #vers 1
        """Open folder dialog for BIOS path"""
        current = self.bios_path_input.text()
        path = QFileDialog.getExistingDirectory(
            self,
            "Select BIOS Directory",
            current,
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.bios_path_input.setText(path)
    
    def _select_cache_path(self): #vers 1
        """Open folder dialog for cache path"""
        current = self.cache_path_input.text()
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Cache Directory",
            current,
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.cache_path_input.setText(path)
    
    def _select_core_path(self): #vers 1
        """Open folder dialog for cores path"""
        current = self.core_path_input.text()
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Cores Directory",
            current,
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.core_path_input.setText(path)
    
    def _select_rom_path(self): #vers 1
        """Open folder dialog for ROM path"""
        current = self.rom_path_input.text()
        path = QFileDialog.getExistingDirectory(
            self,
            "Select ROM Directory",
            current,
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.rom_path_input.setText(path)
    
    def _select_save_path(self): #vers 1
        """Open folder dialog for saves path"""
        current = self.save_path_input.text()
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Saves Directory",
            current,
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.save_path_input.setText(path)
    
    def _setup_ui(self): #vers 3
        """Setup dialog UI elements"""
        layout = QVBoxLayout()
        
        # Paths group
        paths_group = QGroupBox("Directory Paths")
        paths_layout = QVBoxLayout()
        
        # ROM path
        rom_row, self.rom_path_input = self._create_path_selector(
            "ROMs:", 
            "roms", 
            self._select_rom_path
        )
        paths_layout.addLayout(rom_row)
        
        # BIOS path
        bios_row, self.bios_path_input = self._create_path_selector(
            "BIOS:", 
            "bios", 
            self._select_bios_path
        )
        paths_layout.addLayout(bios_row)
        
        # Core path
        core_row, self.core_path_input = self._create_path_selector(
            "Cores:", 
            "cores", 
            self._select_core_path
        )
        paths_layout.addLayout(core_row)
        
        # Save path
        save_row, self.save_path_input = self._create_path_selector(
            "Saves:", 
            "saves", 
            self._select_save_path
        )
        paths_layout.addLayout(save_row)
        
        # Cache path
        cache_row, self.cache_path_input = self._create_path_selector(
            "Cache:", 
            "cache", 
            self._select_cache_path
        )
        paths_layout.addLayout(cache_row)
        
        paths_group.setLayout(paths_layout)
        layout.addWidget(paths_group)
        
        # Display Options group
        display_group = QGroupBox("Display Options")
        display_layout = QVBoxLayout()
        
        # Icon display mode
        display_label = QLabel("Platform Icons:")
        display_layout.addWidget(display_label)
        
        self.icon_button_group = QButtonGroup()
        
        self.icons_text_radio = QRadioButton("Icons & Text")
        self.icons_only_radio = QRadioButton("Icons Only")
        self.text_only_radio = QRadioButton("Text Only")
        
        self.icon_button_group.addButton(self.icons_text_radio, 0)
        self.icon_button_group.addButton(self.icons_only_radio, 1)
        self.icon_button_group.addButton(self.text_only_radio, 2)
        
        display_layout.addWidget(self.icons_text_radio)
        display_layout.addWidget(self.icons_only_radio)
        display_layout.addWidget(self.text_only_radio)
        
        # Themed titlebar checkbox
        display_layout.addSpacing(15)
        titlebar_label = QLabel("Titlebar Options:")
        titlebar_label.setStyleSheet("font-weight: bold;")
        display_layout.addWidget(titlebar_label)
        
        self.themed_titlebar_check = QCheckBox("Use themed titlebar colors")
        self.themed_titlebar_check.setToolTip(
            "When checked: titlebar uses theme colors\n"
            "When unchecked: titlebar uses high-contrast colors for visibility"
        )
        display_layout.addWidget(self.themed_titlebar_check)
        
        hint_label = QLabel("💡 Disable themed titlebar if buttons are hard to see in light themes")
        hint_label.setStyleSheet("color: gray; font-size: 9pt; font-style: italic;")
        hint_label.setWordWrap(True)
        display_layout.addWidget(hint_label)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save_settings)
        save_btn.setDefault(True)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
