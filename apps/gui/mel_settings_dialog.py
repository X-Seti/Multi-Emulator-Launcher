#!/usr/bin/env python3
#this belongs in apps/gui/mel_settings_dialog.py - Version: 8
# X-Seti - November30 2025 - Multi-Emulator Launcher - Settings Dialog

"""
MEL Settings Dialog - Complete settings with tabs
NOW SUPPORTS MULTIPLE ROM PATHS + BIOS FILE BROWSER
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QGroupBox, QLineEdit,
                             QRadioButton, QButtonGroup, QCheckBox, QTabWidget,
                             QWidget, QComboBox, QScrollArea, QFormLayout, 
                             QMessageBox, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
from pathlib import Path

class MELSettingsDialog(QDialog):
    """Settings dialog with multiple ROM paths support"""
    
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("Multi-Emulator Launcher - Settings")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        # Path inputs
        self.rom_paths_list = None
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
        self.emulator_combos = {}
        
        self._setup_ui()
        self._get_settings()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        tabs = QTabWidget()
        tabs.addTab(self._create_paths_tab(), "Paths")
        tabs.addTab(self._create_emulators_tab(), "Emulators")
        tabs.addTab(self._create_debug_tab(), "Debug")
        tabs.addTab(self._create_display_tab(), "Display")
        tabs.addTab(self._create_emulator_display_tab(), "Emulator Display")

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
    
    def _create_paths_tab(self):
        """Create paths tab with MULTIPLE ROM PATHS"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        info_label = QLabel("Configure directory paths. You can add multiple ROM directories (e.g., external drives).")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # ROM Paths group - MULTIPLE PATHS
        rom_group = QGroupBox("ROM Directories (Multiple Allowed)")
        rom_layout = QVBoxLayout()
        
        # List widget for ROM paths
        self.rom_paths_list = QListWidget()
        self.rom_paths_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        rom_layout.addWidget(self.rom_paths_list)
        
        # Buttons for ROM paths
        rom_btn_layout = QHBoxLayout()
        add_rom_btn = QPushButton("âž• Add ROM Directory")
        add_rom_btn.clicked.connect(self._add_rom_path)
        remove_rom_btn = QPushButton("âž– Remove Selected")
        remove_rom_btn.clicked.connect(self._remove_rom_path)
        
        rom_btn_layout.addWidget(add_rom_btn)
        rom_btn_layout.addWidget(remove_rom_btn)
        rom_btn_layout.addStretch()
        rom_layout.addLayout(rom_btn_layout)
        
        rom_group.setLayout(rom_layout)
        layout.addWidget(rom_group)
        
        # Other paths group
        other_group = QGroupBox("Other Directories")
        other_layout = QVBoxLayout()
        
        # BIOS path
        bios_row = QHBoxLayout()
        bios_label = QLabel("BIOS:")
        bios_label.setMinimumWidth(80)
        self.bios_path_input = QLineEdit()
        self.bios_path_input.setText("bios")
        self.bios_path_input.setReadOnly(True)
        
        browse_bios_dir_btn = QPushButton("Browse Dir...")
        browse_bios_dir_btn.clicked.connect(self._select_bios_path)
        
        browse_bios_file_btn = QPushButton("Browse Files...")
        browse_bios_file_btn.clicked.connect(self._browse_bios_files)
        browse_bios_file_btn.setToolTip("Browse and view BIOS files in directory")
        
        bios_row.addWidget(bios_label)
        bios_row.addWidget(self.bios_path_input)
        bios_row.addWidget(browse_bios_dir_btn)
        bios_row.addWidget(browse_bios_file_btn)
        other_layout.addLayout(bios_row)
        
        # Core path
        core_row, self.core_path_input = self._create_path_selector(
            "Cores:", "cores", self._select_core_path
        )
        other_layout.addLayout(core_row)
        
        # Save path
        save_row, self.save_path_input = self._create_path_selector(
            "Saves:", "saves", self._select_save_path
        )
        other_layout.addLayout(save_row)
        
        # Cache path
        cache_row, self.cache_path_input = self._create_path_selector(
            "Cache:", "cache", self._select_cache_path
        )
        other_layout.addLayout(cache_row)
        
        other_group.setLayout(other_layout)
        layout.addWidget(other_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def _add_rom_path(self):
        """Add a new ROM directory"""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select ROM Directory",
            str(Path.home()),
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            # Check if already exists
            for i in range(self.rom_paths_list.count()):
                if self.rom_paths_list.item(i).text() == path:
                    QMessageBox.warning(self, "Duplicate", "This path is already in the list.")
                    return
            
            self.rom_paths_list.addItem(path)
    
        # Emulator display settings
    def get_emulator_display_mode(self, emulator): #vers 1
        """Get display mode for emulator

        Args:
            emulator: Emulator name (e.g., 'stella', 'hatari')

        Returns:
            Display mode string (e.g., 'fullscreen', 'windowed', 'zoom_2x')
        """
        display_settings = self.settings.get('emulator_display_settings', {})
        return display_settings.get(emulator, 'auto')

    def set_emulator_display_mode(self, emulator, mode): #vers 1
        """Set display mode for emulator"""
        if 'emulator_display_settings' not in self.settings:
            self.settings['emulator_display_settings'] = {}

        self.settings['emulator_display_settings'][emulator] = mode
        self.save_mel_settings()

    def get_all_emulator_display_settings(self): #vers 1
        """Get all emulator display settings"""
        return self.settings.get('emulator_display_settings', {})

    def _remove_rom_path(self):
        """Remove selected ROM directory"""
        current_item = self.rom_paths_list.currentItem()
        if current_item:
            if self.rom_paths_list.count() <= 1:
                QMessageBox.warning(self, "Cannot Remove", 
                    "You must have at least one ROM directory.")
                return
            
            row = self.rom_paths_list.row(current_item)
            self.rom_paths_list.takeItem(row)
    
    def _create_emulators_tab(self):
        """Create emulators tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        info_label = QLabel(
            "Select which emulator to use for each platform.\n"
            "'Auto-detect' will automatically choose the best available emulator."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        rescan_btn = QPushButton("ðŸ”„ Re-scan for Emulators")
        rescan_btn.clicked.connect(self._rescan_emulators)
        layout.addWidget(rescan_btn)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QFormLayout()
        
        installed = self.settings_manager.scan_installed_emulators()
        
        all_platforms = set()
        for platforms_list in self.settings_manager.emulator_map.values():
            all_platforms.update(platforms_list)
        
        for platform in sorted(all_platforms):
            combo = QComboBox()
            combo.addItem("Auto-detect (Recommended)")
            
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
    
    def _create_debug_tab(self):
        """Create debug tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        info_label = QLabel(
            "Enable debug mode to see detailed console output.\n"
            "Choose debug level to control verbosity."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        debug_group = QGroupBox("Debug Settings")
        debug_layout = QVBoxLayout()
        
        self.debug_enabled_check = QCheckBox("Enable debug mode")
        debug_layout.addWidget(self.debug_enabled_check)
        
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
    
    def _create_emulator_display_tab(self): #vers 1
        """Create emulator display settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        info_label = QLabel("Configure how each emulator opens (fullscreen, windowed, zoom level).\nOnly detected emulators are shown.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Scan button
        scan_btn = QPushButton("Rescan Emulators")
        scan_btn.clicked.connect(self._rescan_emulator_displays)
        layout.addWidget(scan_btn)

        # Scroll area for emulator settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Emulator display mode options
        self.emulator_display_combos = {}

        # Define emulator display options
        emulator_options = {
            'stella': {  # Atari 2600
                'Auto': 'auto',
                'Fullscreen': '-fullscreen 1',
                'Windowed': '-fullscreen 0',
                '1x Zoom (320x210)': '-zoom 1',
                '2x Zoom (640x420)': '-zoom 2',
                '3x Zoom (960x630)': '-zoom 3',
                '4x Zoom (1280x840)': '-zoom 4',
            },
            'hatari': {  # Atari ST
                'Auto': 'auto',
                'Fullscreen': '--fullscreen',
                'Windowed': '--window',
                '1x Zoom': '--zoom 1',
                '2x Zoom': '--zoom 2',
            },
            'fs-uae': {  # Amiga
                'Auto': 'auto',
                'Fullscreen': '--fullscreen',
                'Windowed': '--window',
            },
            'amiberry': {  # Amiga
                'Auto': 'auto',
                'Fullscreen': '-f',
                'Windowed': '-W',
            },
            'mupen64plus': {  # N64
                'Auto': 'auto',
                'Fullscreen': '--fullscreen',
                'Windowed': '--windowed',
            },
            'pcsx2': {  # PS2
                'Auto': 'auto',
                'Fullscreen': '--fullscreen',
                'Windowed': '--nogui',
            },
            'desmume': {  # DS
                'Auto': 'auto',
                '1x (256x384)': '--3d-engine=1 --filter-mode=0',
                '2x (512x768)': '--3d-engine=1 --filter-mode=1',
                '3x (768x1152)': '--3d-engine=1 --filter-mode=2',
            },
            'fuse': {  # ZX Spectrum
                'Auto': 'auto',
                'Fullscreen': '--full-screen',
                '1x': '--graphics-filter none',
                '2x': '--graphics-filter 2xsai',
                '3x': '--graphics-filter 3xsai',
            },
            'fceux': {  # NES
                'Auto': 'auto',
                'Fullscreen': '--fullscreen 1',
                '1x': '--xscale 1 --yscale 1',
                '2x': '--xscale 2 --yscale 2',
                '3x': '--xscale 3 --yscale 3',
            },
            'snes9x-gtk': {  # SNES
                'Auto': 'auto',
                'Fullscreen': '--fullscreen',
            },
            'mgba-qt': {  # GBA
                'Auto': 'auto',
                'Fullscreen': '-f',
                '1x': '-1',
                '2x': '-2',
                '3x': '-3',
                '4x': '-4',
            },
            'ppsspp-qt': {  # PSP
                'Auto': 'auto',
                'Fullscreen': '--fullscreen',
            },
            'dolphin-emu': {  # GameCube/Wii
                'Auto': 'auto',
                'Fullscreen': '--batch --exec',
            },
            'blastem': {  # Genesis
                'Auto': 'auto',
                'Fullscreen': '-f',
            },
        }

        # Scan for installed emulators
        installed_emulators = self._scan_installed_emulators_simple()

        if not installed_emulators:
            no_emu_label = QLabel("No emulators detected. Install emulators and click 'Rescan'.")
            scroll_layout.addWidget(no_emu_label)
        else:
            for emulator in sorted(installed_emulators):
                if emulator in emulator_options:
                    group = QGroupBox(f"{emulator.upper()}")
                    group_layout = QFormLayout()

                    combo = QComboBox()
                    for label, value in emulator_options[emulator].items():
                        combo.addItem(label, value)

                    # Load saved setting
                    saved_mode = self.settings_manager.get_emulator_display_mode(emulator)
                    for i in range(combo.count()):
                        if combo.itemData(i) == saved_mode:
                            combo.setCurrentIndex(i)
                            break

                    self.emulator_display_combos[emulator] = combo
                    group_layout.addRow("Display Mode:", combo)

                    group.setLayout(group_layout)
                    scroll_layout.addWidget(group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        tab.setLayout(layout)
        return tab

    def _scan_installed_emulators_simple(self): #vers 2
            """Comprehensive scan for installed emulators"""
            from apps.methods.emulator_detector import detect_all_emulators

            # Get cores directory from settings
            cores_dir = Path(self.settings_manager.get_core_path())

            # Detect all emulators
            all_emulators, summary = detect_all_emulators(cores_dir)

            # Return just the emulator names
            return list(all_emulators.keys())

    def _rescan_emulator_displays(self): #vers 1
        """Rescan and rebuild emulator display tab"""
        QMessageBox.information(
            self,
            "Rescan Complete",
            "Close and reopen Settings to see updated emulator list."
        )

    def _create_display_tab(self):
        """Create display tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        info_label = QLabel("Customize how the launcher displays icons and UI elements.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
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
        
        titlebar_group = QGroupBox("Titlebar Options")
        titlebar_layout = QVBoxLayout()
        
        self.themed_titlebar_check = QCheckBox("Use themed titlebar colors")
        titlebar_layout.addWidget(self.themed_titlebar_check)
        
        hint_label = QLabel("ðŸ’¡ Disable if titlebar buttons are hard to see in light themes")
        hint_label.setStyleSheet("color: #888888; font-size: 10px; font-style: italic;")
        hint_label.setWordWrap(True)
        titlebar_layout.addWidget(hint_label)
        
        titlebar_group.setLayout(titlebar_layout)
        layout.addWidget(titlebar_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def _create_path_selector(self, label_text, default_path, select_method):
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
    
    def _get_settings(self):
        """Load current settings"""
        # ROM paths - MULTIPLE
        rom_paths = self.settings_manager.get_rom_paths()
        for path in rom_paths:
            self.rom_paths_list.addItem(str(path))
        
        # Other paths
        self.bios_path_input.setText(str(self.settings_manager.get_bios_path()))
        self.core_path_input.setText(str(self.settings_manager.get_core_path()))
        self.save_path_input.setText(str(self.settings_manager.get_save_path()))
        self.cache_path_input.setText(str(self.settings_manager.get_cache_path()))
        
        # Icon display
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
        
        # Debug
        self.debug_enabled_check.setChecked(
            self.settings_manager.get_debug_enabled()
        )
        
        level = self.settings_manager.get_debug_level()
        level_map = {'ERROR': 0, 'WARNING': 1, 'INFO': 2, 'DEBUG': 3, 'VERBOSE': 4}
        self.debug_level_combo.setCurrentIndex(level_map.get(level, 2))
        
        # Emulators
        for platform, combo in self.emulator_combos.items():
            pref = self.settings_manager.get_emulator_for_platform(platform)
            if pref == 'auto':
                combo.setCurrentIndex(0)
            else:
                for i in range(1, combo.count()):
                    if combo.itemText(i) == pref:
                        combo.setCurrentIndex(i)
                        break
    
    def _browse_bios_files(self): #vers 1
        """Browse and view BIOS files in BIOS directory"""
        bios_path = Path(self.bios_path_input.text())
        
        if not bios_path.exists():
            QMessageBox.warning(
                self,
                "Directory Not Found",
                f"BIOS directory does not exist:\n{bios_path}\n\n"
                "Please select a valid directory first."
            )
            return
        
        # Scan for BIOS files
        bios_files = []
        extensions = ['.bin', '.rom', '.bios', '.zip', '.img']
        
        for ext in extensions:
            bios_files.extend(list(bios_path.glob(f'*{ext}')))
            bios_files.extend(list(bios_path.glob(f'**/*{ext}')))
        
        if not bios_files:
            QMessageBox.information(
                self,
                "No BIOS Files",
                f"No BIOS files found in:\n{bios_path}\n\n"
                f"Looking for: {', '.join(extensions)}"
            )
            return
        
        # Create dialog to show BIOS files
        dialog = QDialog(self)
        dialog.setWindowTitle("BIOS Files")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        info_label = QLabel(f"Found {len(bios_files)} BIOS file(s) in: {bios_path}")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # List widget
        file_list = QListWidget()
        for bios_file in sorted(bios_files):
            relative_path = bios_file.relative_to(bios_path)
            size = bios_file.stat().st_size
            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
            file_list.addItem(f"{relative_path} ({size_str})")
        
        layout.addWidget(file_list)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    

    def _save_settings(self): #vers 1
        """Save all settings"""
        # Save ROM paths - MULTIPLE
        rom_paths = []
        for i in range(self.rom_paths_list.count()):
            rom_paths.append(self.rom_paths_list.item(i).text())
        self.settings_manager.set_rom_paths(rom_paths)
        
        # Save other paths
        self.settings_manager.set_bios_path(self.bios_path_input.text())
        self.settings_manager.set_core_path(self.core_path_input.text())
        self.settings_manager.set_save_path(self.save_path_input.text())
        self.settings_manager.set_cache_path(self.cache_path_input.text())
        
        # Save icon display
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
        
        # Save debug
        self.settings_manager.set_debug_enabled(
            self.debug_enabled_check.isChecked()
        )
        
        level_map = ['ERROR', 'WARNING', 'INFO', 'DEBUG', 'VERBOSE']
        self.settings_manager.set_debug_level(
            level_map[self.debug_level_combo.currentIndex()]
        )
        
        # Save emulators
        for platform, combo in self.emulator_combos.items():
            if combo.currentIndex() == 0:
                self.settings_manager.set_emulator_for_platform(platform, 'auto')
            else:
                emulator = combo.currentText()
                self.settings_manager.set_emulator_for_platform(platform, emulator)

        # Save emulator display settings
        for emulator, combo in self.emulator_display_combos.items():
            mode = combo.currentData()
            self.settings_manager.set_emulator_display_mode(emulator, mode)

        QMessageBox.information(
            self,
            "Settings Saved",
            "All settings have been saved successfully.\n\n"
            "Restart the application to scan new ROM directories."
        )
        
        self.accept()
    
    def _rescan_emulators(self):
        installed = self.settings_manager.scan_installed_emulators()
        QMessageBox.information(
            self,
            "Scan Complete",
            f"Found emulators for {len(installed)} platform(s).\n\n"
            f"Close and reopen this dialog to see updated options."
        )
    
    # Path selectors
    def _select_bios_path(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select BIOS Directory",
            self.bios_path_input.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.bios_path_input.setText(path)
    
    def _select_core_path(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Cores Directory",
            self.core_path_input.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.core_path_input.setText(path)
    
    def _select_save_path(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Saves Directory",
            self.save_path_input.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.save_path_input.setText(path)
    
    def _select_cache_path(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Cache Directory",
            self.cache_path_input.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.cache_path_input.setText(path)
