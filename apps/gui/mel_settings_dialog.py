#!/usr/bin/env python3
#this belongs in apps/gui/mel_settings_dialog.py - Version: 6
# X-Seti - November27 2025 - Multi-Emulator Launcher - Settings Dialog

"""
MEL Settings Dialog - Complete settings with tabs
- Paths: ROM, BIOS, cores, saves, cache
- Emulators: Per-platform emulator selection
- Debug: Enable debug mode and set level
- Display: Icon mode and themed titlebar
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QGroupBox, QLineEdit,
                             QRadioButton, QButtonGroup, QCheckBox, QTabWidget,
                             QWidget, QComboBox, QScrollArea, QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt
from pathlib import Path

##Methods list -
# __init__
# _create_debug_tab
# _create_display_tab
# _create_emulators_tab
# _create_path_selector
# _create_paths_tab
# _get_settings
# _rescan_emulators
# _save_settings
# _select_bios_path
# _select_cache_path
# _select_core_path
# _select_rom_path
# _select_save_path
# _setup_ui

class MELSettingsDialog(QDialog): #vers 6
    """Settings dialog with multiple tabs for all MEL settings"""
    
    def __init__(self, settings_manager, parent=None): #vers 6
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("Multi-Emulator Launcher - Settings")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        # Path inputs
        self.rom_path_input = None
        self.bios_path_input = None
        self.core_path_input = None
        self.save_path_input = None
        self.cache_path_input = None
        
        # Display options
        self.icon_button_group = None
        self.icons_text_radio = None
        self.icons_only_radio = None
        self.text_only_radio = None
        self.themed_titlebar_check = None
        
        # Debug options
        self.debug_enabled_check = None
        self.debug_level_combo = None
        
        # Emulator options
        self.emulator_combos = {}  # platform -> QComboBox
        
        self._setup_ui()
        self._get_settings()
    
    def _setup_ui(self): #vers 6
        """Setup dialog UI with tabs"""
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.addTab(self._create_paths_tab(), "Paths")
        tabs.addTab(self._create_emulators_tab(), "Emulators")
        tabs.addTab(self._create_debug_tab(), "Debug")
        tabs.addTab(self._create_display_tab(), "Display")
        
        layout.addWidget(tabs)
        
        # Bottom buttons
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
    
    def _create_paths_tab(self): #vers 1
        """Create paths configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        info_label = QLabel("Configure directory paths for ROMs, BIOS files, cores, and saves.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Paths group
        paths_group = QGroupBox("Directory Paths")
        paths_layout = QVBoxLayout()
        
        # ROM path
        rom_row, self.rom_path_input = self._create_path_selector(
            "ROMs:", "roms", self._select_rom_path
        )
        paths_layout.addLayout(rom_row)
        
        # BIOS path
        bios_row, self.bios_path_input = self._create_path_selector(
            "BIOS:", "bios", self._select_bios_path
        )
        paths_layout.addLayout(bios_row)
        
        # Core path
        core_row, self.core_path_input = self._create_path_selector(
            "Cores:", "cores", self._select_core_path
        )
        paths_layout.addLayout(core_row)
        
        # Save path
        save_row, self.save_path_input = self._create_path_selector(
            "Saves:", "saves", self._select_save_path
        )
        paths_layout.addLayout(save_row)
        
        # Cache path
        cache_row, self.cache_path_input = self._create_path_selector(
            "Cache:", "cache", self._select_cache_path
        )
        paths_layout.addLayout(cache_row)
        
        paths_group.setLayout(paths_layout)
        layout.addWidget(paths_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def _create_emulators_tab(self): #vers 1
        """Create emulators configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        info_label = QLabel(
            "Select which emulator to use for each platform.\n"
            "'Auto-detect' will automatically choose the best available emulator."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Rescan button
        rescan_btn = QPushButton("🔄 Re-scan for Emulators")
        rescan_btn.clicked.connect(self._rescan_emulators)
        layout.addWidget(rescan_btn)
        
        # Scroll area for platforms
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QFormLayout()
        
        # Get installed emulators
        installed = self.settings_manager.scan_installed_emulators()
        
        # Get all platforms (from emulator_map keys)
        all_platforms = set()
        for platforms_list in self.settings_manager.emulator_map.values():
            all_platforms.update(platforms_list)
        
        for platform in sorted(all_platforms):
            combo = QComboBox()
            combo.addItem("Auto-detect (Recommended)")
            
            # Add installed emulators for this platform
            if platform in installed:
                for emu in installed[platform]:
                    combo.addItem(emu)
            
            self.emulator_combos[platform] = combo
            scroll_layout.addRow(f"{platform}:", combo)
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        tab.setLayout(layout)
        return tab
    
    def _create_debug_tab(self): #vers 1
        """Create debug settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        info_label = QLabel(
            "Enable debug mode to see detailed console output.\n"
            "Choose debug level to control verbosity."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Debug group
        debug_group = QGroupBox("Debug Settings")
        debug_layout = QVBoxLayout()
        
        # Enable checkbox
        self.debug_enabled_check = QCheckBox("Enable debug mode")
        debug_layout.addWidget(self.debug_enabled_check)
        
        # Level selector
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Debug Level:"))
        
        self.debug_level_combo = QComboBox()
        self.debug_level_combo.addItems([
            "ERROR - Only errors",
            "WARNING - Errors and warnings",
            "INFO - General information",
            "DEBUG - Detailed debugging",
            "VERBOSE - Everything"
        ])
        level_layout.addWidget(self.debug_level_combo)
        level_layout.addStretch()
        
        debug_layout.addLayout(level_layout)
        
        # Info text
        info_text = QLabel(
            "Debug output will appear in the terminal/console where you launched the application."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #888888; font-size: 10px; font-style: italic;")
        debug_layout.addWidget(info_text)
        
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def _create_display_tab(self): #vers 1
        """Create display options tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        info_label = QLabel("Customize how the launcher displays icons and UI elements.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Icon display group
        icon_group = QGroupBox("Platform Icons")
        icon_layout = QVBoxLayout()
        
        self.icon_button_group = QButtonGroup()
        
        self.icons_text_radio = QRadioButton("Icons & Text (Recommended)")
        self.icons_only_radio = QRadioButton("Icons Only")
        self.text_only_radio = QRadioButton("Text Only")
        
        self.icon_button_group.addButton(self.icons_text_radio, 0)
        self.icon_button_group.addButton(self.icons_only_radio, 1)
        self.icon_button_group.addButton(self.text_only_radio, 2)
        
        icon_layout.addWidget(self.icons_text_radio)
        icon_layout.addWidget(self.icons_only_radio)
        icon_layout.addWidget(self.text_only_radio)
        
        icon_group.setLayout(icon_layout)
        layout.addWidget(icon_group)
        
        # Titlebar group
        titlebar_group = QGroupBox("Titlebar Options")
        titlebar_layout = QVBoxLayout()
        
        self.themed_titlebar_check = QCheckBox("Use themed titlebar colors")
        self.themed_titlebar_check.setToolTip(
            "When checked: titlebar uses theme colors\n"
            "When unchecked: titlebar uses high-contrast colors"
        )
        titlebar_layout.addWidget(self.themed_titlebar_check)
        
        hint_label = QLabel("💡 Disable if titlebar buttons are hard to see in light themes")
        hint_label.setStyleSheet("color: #888888; font-size: 10px; font-style: italic;")
        hint_label.setWordWrap(True)
        titlebar_layout.addWidget(hint_label)
        
        titlebar_group.setLayout(titlebar_layout)
        layout.addWidget(titlebar_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def _create_path_selector(self, label_text, default_path, select_method): #vers 1
        """Create a path selector row"""
        container = QHBoxLayout()
        
        label = QLabel(label_text)
        label.setMinimumWidth(80)
        
        path_input = QLineEdit()
        path_input.setText(str(default_path))
        path_input.setReadOnly(True)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(select_method)
        
        container.addWidget(label)
        container.addWidget(path_input)
        container.addWidget(browse_btn)
        
        return container, path_input
    
    def _get_settings(self): #vers 6
        """Load current settings into UI"""
        # Paths
        self.rom_path_input.setText(str(self.settings_manager.get_rom_path()))
        self.bios_path_input.setText(str(self.settings_manager.get_bios_path()))
        self.core_path_input.setText(str(self.settings_manager.get_core_path()))
        self.save_path_input.setText(str(self.settings_manager.get_save_path()))
        self.cache_path_input.setText(str(self.settings_manager.get_cache_path()))
        
        # Icon display mode
        mode = self.settings_manager.get_icon_display_mode()
        if mode == 'icons_and_text':
            self.icons_text_radio.setChecked(True)
        elif mode == 'icons_only':
            self.icons_only_radio.setChecked(True)
        else:
            self.text_only_radio.setChecked(True)
        
        # Themed titlebar
        self.themed_titlebar_check.setChecked(
            self.settings_manager.get_themed_titlebar()
        )
        
        # Debug settings
        self.debug_enabled_check.setChecked(
            self.settings_manager.get_debug_enabled()
        )
        
        level = self.settings_manager.get_debug_level()
        level_map = {
            'ERROR': 0, 'WARNING': 1, 'INFO': 2, 'DEBUG': 3, 'VERBOSE': 4
        }
        self.debug_level_combo.setCurrentIndex(level_map.get(level, 2))
        
        # Emulator preferences
        for platform, combo in self.emulator_combos.items():
            pref = self.settings_manager.get_emulator_for_platform(platform)
            if pref == 'auto':
                combo.setCurrentIndex(0)
            else:
                # Try to find matching emulator in combo
                for i in range(1, combo.count()):
                    if combo.itemText(i) == pref:
                        combo.setCurrentIndex(i)
                        break
    
    def _save_settings(self): #vers 6
        """Save all settings"""
        # Save paths
        self.settings_manager.set_rom_path(self.rom_path_input.text())
        self.settings_manager.set_bios_path(self.bios_path_input.text())
        self.settings_manager.set_core_path(self.core_path_input.text())
        self.settings_manager.set_save_path(self.save_path_input.text())
        self.settings_manager.set_cache_path(self.cache_path_input.text())
        
        # Save icon display mode
        if self.icons_text_radio.isChecked():
            self.settings_manager.set_icon_display_mode('icons_and_text')
        elif self.icons_only_radio.isChecked():
            self.settings_manager.set_icon_display_mode('icons_only')
        else:
            self.settings_manager.set_icon_display_mode('text_only')
        
        # Save themed titlebar
        self.settings_manager.set_themed_titlebar(
            self.themed_titlebar_check.isChecked()
        )
        
        # Save debug settings
        self.settings_manager.set_debug_enabled(
            self.debug_enabled_check.isChecked()
        )
        
        level_map = ['ERROR', 'WARNING', 'INFO', 'DEBUG', 'VERBOSE']
        self.settings_manager.set_debug_level(
            level_map[self.debug_level_combo.currentIndex()]
        )
        
        # Save emulator preferences
        for platform, combo in self.emulator_combos.items():
            if combo.currentIndex() == 0:
                self.settings_manager.set_emulator_for_platform(platform, 'auto')
            else:
                emulator = combo.currentText()
                self.settings_manager.set_emulator_for_platform(platform, emulator)
        
        QMessageBox.information(
            self,
            "Settings Saved",
            "All settings have been saved successfully."
        )
        
        self.accept()
    
    def _rescan_emulators(self): #vers 1
        """Re-scan for installed emulators"""
        installed = self.settings_manager.scan_installed_emulators()
        
        QMessageBox.information(
            self,
            "Scan Complete",
            f"Found emulators for {len(installed)} platform(s).\n\n"
            f"Close and reopen this dialog to see updated options."
        )
    
    # Path selector methods
    def _select_rom_path(self): #vers 1
        """Select ROM directory"""
        path = QFileDialog.getExistingDirectory(
            self, "Select ROM Directory",
            self.rom_path_input.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.rom_path_input.setText(path)
    
    def _select_bios_path(self): #vers 1
        """Select BIOS directory"""
        path = QFileDialog.getExistingDirectory(
            self, "Select BIOS Directory",
            self.bios_path_input.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.bios_path_input.setText(path)
    
    def _select_core_path(self): #vers 1
        """Select cores directory"""
        path = QFileDialog.getExistingDirectory(
            self, "Select Cores Directory",
            self.core_path_input.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.core_path_input.setText(path)
    
    def _select_save_path(self): #vers 1
        """Select saves directory"""
        path = QFileDialog.getExistingDirectory(
            self, "Select Saves Directory",
            self.save_path_input.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.save_path_input.setText(path)
    
    def _select_cache_path(self): #vers 1
        """Select cache directory"""
        path = QFileDialog.getExistingDirectory(
            self, "Select Cache Directory",
            self.cache_path_input.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.cache_path_input.setText(path)
