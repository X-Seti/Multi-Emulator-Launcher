#!/usr/bin/env python3
#this belongs in apps/gui/emulator_settings_dialog.py - Version: 1
# X-Seti - November27 2025 - Multi-Emulator Launcher - Emulator Settings

"""
Emulator Settings Dialog
Configure which emulator/core to use for each platform
Detects installed emulators and shows available options
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QGroupBox, QFormLayout,
                             QScrollArea, QWidget, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt
from pathlib import Path
import json

##Methods list -
# __init__
# save_settings
# _create_platform_row
# _detect_available_emulators
# _load_settings
# _scan_installed_emulators
# _setup_ui

class EmulatorSettingsDialog(QDialog): #vers 1
    """Dialog for configuring emulator preferences per platform"""
    
    def __init__(self, core_launcher, parent=None): #vers 1
        """Initialize emulator settings dialog
        
        Args:
            core_launcher: CoreLauncher instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.core_launcher = core_launcher
        self.config_file = core_launcher.base_dir / "config" / "emulator_preferences.json"
        
        # Platform -> emulator dropdown mapping
        self.emulator_combos = {}
        
        # Platform -> auto-detect checkbox mapping
        self.auto_detect_checks = {}
        
        # Load current settings
        self.settings = self._load_settings()
        
        # Scan for installed emulators
        self.installed_emulators = self._scan_installed_emulators()
        
        self.setWindowTitle("Emulator Settings")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        self._setup_ui()
    
    def _setup_ui(self): #vers 1
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel(
            "Configure which emulator to use for each platform.\n"
            "Leave as 'Auto-detect' to automatically choose the best available emulator."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Scroll area for platforms
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Get all platforms from core database
        platforms = sorted(self.core_launcher.core_database.keys())
        
        for platform in platforms:
            platform_group = self._create_platform_row(platform)
            scroll_layout.addWidget(platform_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        detect_btn = QPushButton("Re-scan Emulators")
        detect_btn.clicked.connect(self._rescan_emulators)
        button_layout.addWidget(detect_btn)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setDefault(True)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _create_platform_row(self, platform): #vers 1
        """Create settings row for a platform
        
        Args:
            platform: Platform name
            
        Returns:
            QGroupBox with platform settings
        """
        group = QGroupBox(platform)
        layout = QFormLayout()
        
        # Get available emulators for this platform
        available = self._detect_available_emulators(platform)
        
        # Emulator selection dropdown
        emulator_combo = QComboBox()
        emulator_combo.addItem("Auto-detect (Recommended)")
        
        for emu_name, emu_path in available:
            emulator_combo.addItem(f"{emu_name} - {emu_path}")
        
        # Load saved preference
        saved_emulator = self.settings.get(platform, {}).get('emulator', 'auto')
        if saved_emulator == 'auto':
            emulator_combo.setCurrentIndex(0)
        else:
            # Try to find matching entry
            for i in range(1, emulator_combo.count()):
                if saved_emulator in emulator_combo.itemText(i):
                    emulator_combo.setCurrentIndex(i)
                    break
        
        self.emulator_combos[platform] = emulator_combo
        layout.addRow("Emulator:", emulator_combo)
        
        # Show available count
        count_label = QLabel(f"{len(available)} emulator(s) available")
        count_label.setStyleSheet("color: #888888; font-size: 10px;")
        layout.addRow("", count_label)
        
        group.setLayout(layout)
        return group
    
    def _detect_available_emulators(self, platform): #vers 1
        """Detect available emulators for platform
        
        Args:
            platform: Platform name
            
        Returns:
            List of (emulator_name, path) tuples
        """
        available = []
        
        # Check installed standalone emulators
        if platform in self.installed_emulators:
            for emu_name, emu_path in self.installed_emulators[platform]:
                available.append((emu_name, emu_path))
        
        # Check libretro cores
        platform_info = self.core_launcher.core_database.get(platform, {})
        cores = platform_info.get('cores', [])
        
        for core_name in cores:
            core_path = self.core_launcher.get_core_path(core_name)
            if core_path and core_path.exists():
                available.append((f"Libretro: {core_name}", str(core_path)))
        
        return available
    
    def _scan_installed_emulators(self): #vers 1
        """Scan system for installed emulators
        
        Returns:
            Dict of platform -> [(name, path), ...] 
        """
        import subprocess
        
        # Emulator -> platforms mapping
        emulator_map = {
            # PlayStation
            'pcsx2': ['PlayStation 2'],
            'pcsx2-qt': ['PlayStation 2'],
            'duckstation-qt': ['PlayStation 1', 'PlayStation'],
            'epsxe': ['PlayStation 1', 'PlayStation'],
            'ppsspp': ['PSP'],
            'ppsspp-qt': ['PSP'],
            
            # Nintendo
            'mupen64plus': ['Nintendo 64'],
            'snes9x-gtk': ['Super Nintendo', 'SNES'],
            'bsnes': ['Super Nintendo', 'SNES'],
            'fceux': ['Nintendo Entertainment System', 'NES'],
            'mgba-qt': ['Game Boy Advance', 'GBA'],
            'visualboyadvance': ['Game Boy Advance', 'GBA'],
            'desmume': ['Nintendo DS'],
            'melonDS': ['Nintendo DS'],
            'dolphin-emu': ['Nintendo GameCube', 'GameCube', 'Nintendo Wii', 'Wii'],
            
            # Sega
            'kega-fusion': ['Sega Genesis', 'Genesis', 'Sega Mega Drive', 'Mega Drive'],
            'blastem': ['Sega Genesis', 'Genesis'],
            
            # Retro computers
            'fs-uae': ['Amiga'],
            'hatari': ['Atari ST'],
            'stella': ['Atari 2600'],
            'atari800': ['Atari 800'],
            'cap32': ['Amstrad CPC'],
            'vice': ['Commodore 64', 'C64'],
            'fuse': ['ZX Spectrum'],
        }
        
        installed = {}
        
        for emu_name, platforms in emulator_map.items():
            try:
                result = subprocess.run(
                    ['which', emu_name],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                if result.returncode == 0:
                    emu_path = result.stdout.strip()
                    
                    # Add to each platform
                    for platform in platforms:
                        if platform not in installed:
                            installed[platform] = []
                        installed[platform].append((emu_name, emu_path))
                        
            except Exception:
                pass
        
        return installed
    
    def _rescan_emulators(self): #vers 1
        """Re-scan for installed emulators"""
        self.installed_emulators = self._scan_installed_emulators()
        
        # Refresh dialog
        QMessageBox.information(
            self,
            "Scan Complete",
            f"Found emulators for {len(self.installed_emulators)} platform(s)"
        )
        
        # TODO: Refresh the UI to show newly detected emulators
    
    def _load_settings(self): #vers 1
        """Load saved emulator preferences
        
        Returns:
            Dict of settings
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                from apps.utils.debug_logger import error
                error(f"Failed to load emulator settings: {e}", "CONFIG")
        
        return {}
    
    def save_settings(self): #vers 1
        """Save emulator preferences"""
        settings = {}
        
        for platform, combo in self.emulator_combos.items():
            selected = combo.currentText()
            
            if selected == "Auto-detect (Recommended)":
                settings[platform] = {'emulator': 'auto'}
            else:
                # Extract emulator name from "name - path" format
                emulator_name = selected.split(' - ')[0]
                settings[platform] = {'emulator': emulator_name}
        
        # Save to file
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            from apps.utils.debug_logger import info
            info("Emulator settings saved", "CONFIG")
            
            QMessageBox.information(
                self,
                "Settings Saved",
                "Emulator preferences have been saved successfully."
            )
            
            self.accept()
            
        except Exception as e:
            from apps.utils.debug_logger import error
            error(f"Failed to save emulator settings: {e}", "CONFIG")
            
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Failed to save settings:\n{e}"
            )
