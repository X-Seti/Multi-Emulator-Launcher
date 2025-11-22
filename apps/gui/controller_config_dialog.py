# X-Seti - November21 2025 - Multi-Emulator Launcher - Controller Config Dialog
# This file goes in /apps/gui/controller_config_dialog.py - Version: 1
"""
Controller Configuration Dialog
- Global controller button mapping
- Per-platform controller overrides
- Save/load controller profiles
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QListWidget, QListWidgetItem,
                             QTabWidget, QWidget, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
from pathlib import Path
import json

##Methods list -
# __init__
# _create_button_mapping_row
# _create_global_tab
# _create_platform_tab
# _detect_controller
# _get_settings
# _remap_button
# _save_settings
# _setup_ui

class ControllerConfigDialog(QDialog): #vers 1
    """Controller configuration dialog"""
    
    # Standard controller buttons
    CONTROLLER_BUTTONS = [
        "A / Cross",
        "B / Circle", 
        "X / Square",
        "Y / Triangle",
        "L1 / LB",
        "R1 / RB",
        "L2 / LT",
        "R2 / RT",
        "L3 / LS",
        "R3 / RS",
        "D-Pad Up",
        "D-Pad Down",
        "D-Pad Left",
        "D-Pad Right",
        "Start",
        "Select / Back",
        "Guide / Home"
    ]
    
    # Emulator actions
    EMULATOR_ACTIONS = [
        "Not Mapped",
        "Accept / Confirm",
        "Cancel / Back",
        "Menu",
        "Fast Forward",
        "Rewind",
        "Save State",
        "Load State",
        "Screenshot",
        "Pause",
        "Reset",
        "Quit Emulator",
        "Next State Slot",
        "Previous State Slot",
        "Toggle Fullscreen",
        "Toggle FPS Display"
    ]
    
    def __init__(self, gamepad_config, parent=None): #vers 1
        super().__init__(parent)
        self.gamepad_config = gamepad_config
        self.setWindowTitle("Controller Configuration")
        self.setMinimumSize(700, 500)
        self.setModal(True)
        
        # Controller mappings
        self.global_mapping = {}
        self.platform_mappings = {}
        
        self._setup_ui()
        self._get_settings()
    
    def _create_button_mapping_row(self, button_name, parent_layout): #vers 1
        """Create a button mapping row"""
        row = QHBoxLayout()
        
        # Button label
        label = QLabel(button_name)
        label.setMinimumWidth(150)
        row.addWidget(label)
        
        # Action dropdown
        action_combo = QComboBox()
        action_combo.addItems(self.EMULATOR_ACTIONS)
        row.addWidget(action_combo)
        
        # Remap button
        remap_btn = QPushButton("Remap")
        remap_btn.setMaximumWidth(80)
        remap_btn.clicked.connect(lambda: self._remap_button(button_name, action_combo))
        row.addWidget(remap_btn)
        
        parent_layout.addLayout(row)
        
        return action_combo
    
    def _create_global_tab(self): #vers 1
        """Create global controller mapping tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Controller info
        info_group = QGroupBox("Detected Controller")
        info_layout = QVBoxLayout()
        
        self.controller_label = QLabel("No controller detected")
        info_layout.addWidget(self.controller_label)
        
        detect_btn = QPushButton("Detect Controller")
        detect_btn.clicked.connect(self._detect_controller)
        info_layout.addWidget(detect_btn)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Button mappings
        mapping_group = QGroupBox("Global Button Mapping")
        mapping_layout = QVBoxLayout()
        
        self.global_button_combos = {}
        for button in self.CONTROLLER_BUTTONS:
            combo = self._create_button_mapping_row(button, mapping_layout)
            self.global_button_combos[button] = combo
        
        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)
        
        layout.addStretch()
        return tab
    
    def _create_platform_tab(self): #vers 1
        """Create per-platform override tab"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Platform list
        platform_group = QGroupBox("Platforms")
        platform_layout = QVBoxLayout()
        
        self.platform_list = QListWidget()
        self.platform_list.addItems([
            "Amiga", "Atari ST", "PlayStation 1", "Nintendo 64",
            "SNES", "Genesis", "Game Boy Advance"
        ])
        self.platform_list.currentItemChanged.connect(self._on_platform_selected)
        platform_layout.addWidget(self.platform_list)
        
        platform_group.setLayout(platform_layout)
        layout.addWidget(platform_group, 1)
        
        # Platform-specific mappings
        mapping_group = QGroupBox("Platform Override Mapping")
        mapping_layout = QVBoxLayout()
        
        use_global_btn = QPushButton("Use Global Mapping")
        mapping_layout.addWidget(use_global_btn)
        
        self.platform_button_combos = {}
        for button in self.CONTROLLER_BUTTONS[:8]:  # Show first 8 buttons
            combo = self._create_button_mapping_row(button, mapping_layout)
            self.platform_button_combos[button] = combo
        
        mapping_layout.addStretch()
        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group, 2)
        
        return tab
    
    def _detect_controller(self): #vers 1
        """Detect connected controller"""
        if self.gamepad_config:
            controllers = self.gamepad_config.detect_controllers()
            if controllers:
                self.controller_label.setText(f"Controller: {controllers[0]}")
            else:
                self.controller_label.setText("No controller detected")
                QMessageBox.information(self, "No Controller", 
                    "No controller detected. Please connect a controller and try again.")
    
    def _get_settings(self): #vers 1
        """Load current controller settings"""
        # Load from gamepad_config if available
        if self.gamepad_config:
            # TODO: Load mappings from gamepad_config
            pass
        
        # Set default mappings
        self.global_button_combos["A / Cross"].setCurrentText("Accept / Confirm")
        self.global_button_combos["B / Circle"].setCurrentText("Cancel / Back")
        self.global_button_combos["Start"].setCurrentText("Menu")
        self.global_button_combos["Select / Back"].setCurrentText("Pause")
    
    def _on_platform_selected(self, current, previous): #vers 1
        """Handle platform selection for override mapping"""
        if current:
            platform = current.text()
            # Load platform-specific mappings
            pass
    
    def _remap_button(self, button_name, action_combo): #vers 1
        """Remap a button by detecting controller input"""
        QMessageBox.information(self, "Remap Button",
            f"Press the button you want to map to '{button_name}'...\n\n"
            "(This feature requires controller input detection)")
        # TODO: Implement actual button detection
    
    def _save_settings(self): #vers 1
        """Save controller configuration"""
        # Build mapping dict
        mapping = {}
        for button, combo in self.global_button_combos.items():
            mapping[button] = combo.currentText()
        
        # Save via gamepad_config
        if self.gamepad_config:
            # TODO: Implement save in gamepad_config
            config_file = Path("controller_config.json")
            with open(config_file, 'w') as f:
                json.dump(mapping, f, indent=2)
            
            QMessageBox.information(self, "Saved", 
                "Controller configuration saved successfully!")
        
        self.accept()
    
    def _setup_ui(self): #vers 1
        """Setup dialog UI"""
        layout = QVBoxLayout()
        
        # Tab widget
        tabs = QTabWidget()
        tabs.addTab(self._create_global_tab(), "Global Mapping")
        tabs.addTab(self._create_platform_tab(), "Platform Overrides")
        layout.addWidget(tabs)
        
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
