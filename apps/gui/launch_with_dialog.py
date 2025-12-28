#!/usr/bin/env python3
#this belongs in apps/gui/launch_with_dialog.py - Version: 1
# X-Seti - December27 2025 - Multi-Emulator Launcher - Launch With Dialog

"""
Launch With Dialog
Allows user to manually select emulator/core when auto-detection fails
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QRadioButton, QButtonGroup, QGroupBox,
                             QListWidget, QListWidgetItem, QFileDialog, QLineEdit,
                             QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt
from pathlib import Path
import subprocess

##Methods list -
# __init__
# get_selected_launcher
# _browse_core
# _browse_emulator
# _create_ui
# _detect_emulators
# _detect_cores
# _on_launch
# _populate_emulators
# _populate_cores

class LaunchWithDialog(QDialog): #vers 1
    """Dialog for manually selecting emulator or core"""
    
    def __init__(self, platform, rom_path, mel_settings, parent=None): #vers 1
        """Initialize launch with dialog
        
        Args:
            platform: Platform name
            rom_path: Path to ROM file
            mel_settings: MELSettingsManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.platform = platform
        self.rom_path = Path(rom_path)
        self.mel_settings = mel_settings
        self.selected_launcher = None
        self.launcher_type = None  # 'emulator', 'core', or 'custom'
        self.set_as_default = False
        
        self.setWindowTitle(f"Launch {self.rom_path.name}")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        self._create_ui()
        
    def _create_ui(self): #vers 1
        """Create dialog UI"""
        layout = QVBoxLayout()
        
        # Info label
        info = QLabel(f"Select how to launch:\n{self.rom_path.name}\n\nPlatform: {self.platform}")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Method selection
        method_group = QGroupBox("Launch Method")
        method_layout = QVBoxLayout()
        
        self.method_group = QButtonGroup()
        
        self.emulator_radio = QRadioButton("Use Installed Emulator (Standalone)")
        self.core_radio = QRadioButton("Use Libretro Core (via RetroArch)")
        self.custom_radio = QRadioButton("Browse for Custom Binary")
        
        self.method_group.addButton(self.emulator_radio, 0)
        self.method_group.addButton(self.core_radio, 1)
        self.method_group.addButton(self.custom_radio, 2)
        
        self.emulator_radio.setChecked(True)
        self.emulator_radio.toggled.connect(self._on_method_changed)
        self.core_radio.toggled.connect(self._on_method_changed)
        self.custom_radio.toggled.connect(self._on_method_changed)
        
        method_layout.addWidget(self.emulator_radio)
        method_layout.addWidget(self.core_radio)
        method_layout.addWidget(self.custom_radio)
        
        method_group.setLayout(method_layout)
        layout.addWidget(method_group)
        
        # Emulator list
        self.emulator_group = QGroupBox("Installed Emulators")
        emulator_layout = QVBoxLayout()
        self.emulator_list = QListWidget()
        self.emulator_list.itemDoubleClicked.connect(self._on_launch)
        emulator_layout.addWidget(self.emulator_list)
        self.emulator_group.setLayout(emulator_layout)
        layout.addWidget(self.emulator_group)
        
        # Core list
        self.core_group = QGroupBox("Libretro Cores (Requires RetroArch)")
        core_layout = QVBoxLayout()
        self.core_list = QListWidget()
        self.core_list.itemDoubleClicked.connect(self._on_launch)
        core_layout.addWidget(self.core_list)
        self.core_group.setLayout(core_layout)
        layout.addWidget(self.core_group)
        self.core_group.hide()
        
        # Custom binary
        self.custom_group = QGroupBox("Custom Binary")
        custom_layout = QVBoxLayout()
        
        browse_layout = QHBoxLayout()
        self.custom_path = QLineEdit()
        self.custom_path.setPlaceholderText("Select emulator executable...")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_custom)
        browse_layout.addWidget(self.custom_path)
        browse_layout.addWidget(browse_btn)
        
        custom_layout.addLayout(browse_layout)
        self.custom_group.setLayout(custom_layout)
        layout.addWidget(self.custom_group)
        self.custom_group.hide()
        
        # Set as default checkbox
        self.default_check = QCheckBox("Remember this choice for all games on this platform")
        layout.addWidget(self.default_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        launch_btn = QPushButton("Launch")
        launch_btn.clicked.connect(self._on_launch)
        launch_btn.setDefault(True)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(launch_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Populate lists
        self._populate_emulators()
        self._populate_cores()
        
    def _on_method_changed(self): #vers 1
        """Handle method selection change"""
        if self.emulator_radio.isChecked():
            self.emulator_group.show()
            self.core_group.hide()
            self.custom_group.hide()
        elif self.core_radio.isChecked():
            self.emulator_group.hide()
            self.core_group.show()
            self.custom_group.hide()
        else:  # custom
            self.emulator_group.hide()
            self.core_group.hide()
            self.custom_group.show()
    
    def _populate_emulators(self): #vers 1
        """Populate emulator list with detected emulators"""
        self.emulator_list.clear()
        
        # Detect installed emulators
        emulators = self._detect_emulators()
        
        if not emulators:
            item = QListWidgetItem("No emulators detected")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.emulator_list.addItem(item)
            return
        
        for emu_name, emu_path in emulators.items():
            item = QListWidgetItem(f"{emu_name} ({emu_path})")
            item.setData(Qt.ItemDataRole.UserRole, emu_path)
            self.emulator_list.addItem(item)
    
    def _populate_cores(self): #vers 2
        """Populate core list with available cores"""
        self.core_list.clear()
        
        # Check if RetroArch is installed
        retroarch_available = False
        try:
            result = subprocess.run(['which', 'retroarch'], capture_output=True, timeout=1)
            retroarch_available = (result.returncode == 0)
        except:
            pass
        
        if not retroarch_available:
            item = QListWidgetItem("⚠️  RetroArch not installed")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.core_list.addItem(item)
            
            item2 = QListWidgetItem("Install with: sudo pacman -S retroarch")
            item2.setFlags(Qt.ItemFlag.NoItemFlags)
            self.core_list.addItem(item2)
            return
        
        # Get cores directory from settings
        cores_dir = self.mel_settings.get_core_path()
        
        if not cores_dir.exists():
            item = QListWidgetItem(f"Cores directory not found: {cores_dir}")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.core_list.addItem(item)
            return
        
        # Find .so files (Linux cores)
        cores = list(cores_dir.glob("*.so"))
        
        if not cores:
            item = QListWidgetItem("No cores found")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.core_list.addItem(item)
            return
        
        for core_path in sorted(cores):
            item = QListWidgetItem(f"{core_path.name}")
            item.setData(Qt.ItemDataRole.UserRole, str(core_path))
            self.core_list.addItem(item)
    
    def _detect_emulators(self): #vers 2
        """Detect installed emulators
        
        Returns:
            Dict of emulator_name -> path
        """
        # Common emulator names
        emulator_names = [
            # Atari
            'hatari', 'stella', 'atari800', 'atari++',
            'prosystem',  # Atari 7800
            # Amstrad
            'cap32', 'caprice32',
            # Acorn / BBC
            'b2', 'beebem', 'jsbeeb',  # BBC Micro
            'elkulator',  # Acorn Electron
            # PlayStation
            'pcsx2', 'pcsx2-qt', 'duckstation-qt', 'epsxe',
            # PSP
            'ppsspp', 'ppsspp-qt', 'ppsspp-sdl',
            # Nintendo
            'dolphin-emu', 'mupen64plus', 'snes9x-gtk', 'snes9x',
            'fceux', 'nestopia', 'mgba-qt', 'vba', 'visualboyadvance',
            'melonds', 'desmume', 'citra', 'citra-qt',
            # Sega
            'blastem', 'gens', 'fusion',
            # Amiga
            'amiberry', 'amiberry-lite', 'fs-uae',
            # Other
            'fuse', 'vice', 'mame', 'bluemsx', 'bsnes',
            'mednafen', 'retroarch'
        ]
        
        installed = {}
        
        for emu in emulator_names:
            try:
                result = subprocess.run(
                    ['which', emu],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                
                if result.returncode == 0:
                    path = result.stdout.strip()
                    installed[emu] = path
            except:
                pass
        
        return installed
    
    def _browse_custom(self): #vers 1
        """Browse for custom emulator binary"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Emulator Executable",
            str(Path.home()),
            "Executables (*);;All Files (*)"
        )
        
        if path:
            self.custom_path.setText(path)
    
    def _on_launch(self): #vers 2
        """Handle launch button"""
        if self.emulator_radio.isChecked():
            current = self.emulator_list.currentItem()
            if not current or not current.data(Qt.ItemDataRole.UserRole):
                QMessageBox.warning(self, "No Selection", "Please select an emulator")
                return
            
            self.selected_launcher = current.data(Qt.ItemDataRole.UserRole)
            self.launcher_type = 'emulator'
            
        elif self.core_radio.isChecked():
            current = self.core_list.currentItem()
            if not current or not current.data(Qt.ItemDataRole.UserRole):
                QMessageBox.warning(self, "No Selection", "Please select a core")
                return
            
            # Check if RetroArch is available
            try:
                result = subprocess.run(['which', 'retroarch'], capture_output=True, timeout=1)
                if result.returncode != 0:
                    QMessageBox.critical(
                        self,
                        "RetroArch Not Found",
                        "Libretro cores require RetroArch to run.\n\n"
                        "Please install RetroArch:\n"
                        "  sudo pacman -S retroarch\n\n"
                        "Or select an installed emulator instead."
                    )
                    return
            except:
                QMessageBox.critical(self, "Error", "Cannot check for RetroArch")
                return
            
            self.selected_launcher = current.data(Qt.ItemDataRole.UserRole)
            self.launcher_type = 'core'
            
        else:  # custom
            path = self.custom_path.text().strip()
            if not path:
                QMessageBox.warning(self, "No Path", "Please select a binary")
                return
            
            if not Path(path).exists():
                QMessageBox.warning(self, "Invalid Path", f"File not found:\n{path}")
                return
            
            self.selected_launcher = path
            self.launcher_type = 'custom'
        
        self.set_as_default = self.default_check.isChecked()
        self.accept()
    
    def get_selected_launcher(self): #vers 1
        """Get selected launcher info
        
        Returns:
            Tuple of (launcher_path, launcher_type, set_as_default)
        """
        return (self.selected_launcher, self.launcher_type, self.set_as_default)
