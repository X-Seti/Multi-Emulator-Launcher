#!/usr/bin/env python3
#this belongs in apps/gui/game_manager_dialog.py - Version: 1
# X-Seti - November23 2025 - Multi-Emulator Launcher - Game Manager

"""
Game Manager Dialog
Allows manual core assignment and game-specific configuration
Saves per-game settings to config files
"""

import json
from pathlib import Path
from typing import Optional, Dict, List
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QListWidget, QListWidgetItem, QComboBox,
                            QGroupBox, QFormLayout, QLineEdit, QCheckBox,
                            QMessageBox, QFileDialog, QTextEdit, QTabWidget,
                            QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

##Methods list -
# __init__
# load_game_config
# save_game_config
# _apply_config
# _browse_bios
# _browse_core
# _browse_working_dir
# _create_core_tab
# _create_launch_tab
# _create_ui
# _get_available_cores
# _load_config_for_game
# _on_game_selected
# _save_current_config
# _test_launch

##class GameConfig -
# __init__
# get_config
# save_config

##class GameManagerDialog -

class GameConfig: #vers 1
    """Handles loading and saving game configurations"""
    
    def __init__(self, config_dir: Path): #vers 1
        """Initialize game config manager
        
        Args:
            config_dir: Directory to store game configs
        """
        self.config_dir = Path(config_dir) / "game_configs"
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def get_config(self, platform: str, game_name: str) -> Dict: #vers 1
        """Get configuration for a specific game
        
        Args:
            platform: Platform name
            game_name: Game name
            
        Returns:
            Configuration dict or empty dict if not found
        """
        config_file = self.config_dir / platform / f"{game_name}.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config for {game_name}: {e}")
                return {}
        
        return {}
    
    def save_config(self, platform: str, game_name: str, config: Dict) -> bool: #vers 1
        """Save configuration for a specific game
        
        Args:
            platform: Platform name
            game_name: Game name
            config: Configuration dict
            
        Returns:
            True if saved successfully
        """
        platform_dir = self.config_dir / platform
        platform_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = platform_dir / f"{game_name}.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config for {game_name}: {e}")
            return False


class GameManagerDialog(QDialog): #vers 1
    """Dialog for managing game configurations"""
    
    config_saved = pyqtSignal(str, str)  # platform, game_name
    
    def __init__(self, platform: str, games: List[str], core_downloader, 
                 core_launcher, game_config: GameConfig, parent=None): #vers 1
        """Initialize game manager
        
        Args:
            platform: Current platform
            games: List of game names
            core_downloader: CoreDownloader instance
            core_launcher: CoreLauncher instance
            game_config: GameConfig instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.platform = platform
        self.games = games
        self.core_downloader = core_downloader
        self.core_launcher = core_launcher
        self.game_config = game_config
        
        self.current_game = None
        self.current_config = {}
        
        self.setWindowTitle(f"Game Manager - {platform}")
        self.resize(800, 600)
        
        self._create_ui()
        
        # Select first game if available
        if self.games:
            self.game_list.setCurrentRow(0)
    
    def _create_ui(self): #vers 1
        """Create dialog UI"""
        layout = QHBoxLayout(self)
        
        # Left panel - Game list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        list_label = QLabel(f"<b>{self.platform} Games ({len(self.games)})</b>")
        left_layout.addWidget(list_label)
        
        self.game_list = QListWidget()
        self.game_list.addItems(self.games)
        self.game_list.currentRowChanged.connect(self._on_game_selected)
        left_layout.addWidget(self.game_list)
        
        layout.addWidget(left_panel, stretch=1)
        
        # Right panel - Configuration
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.game_title = QLabel("<b>Select a game</b>")
        self.game_title.setFont(QFont("Sans", 12, QFont.Weight.Bold))
        right_layout.addWidget(self.game_title)
        
        # Tabs for different config sections
        self.tabs = QTabWidget()
        
        self.core_tab = self._create_core_tab()
        self.tabs.addTab(self.core_tab, "Core Settings")
        
        self.launch_tab = self._create_launch_tab()
        self.tabs.addTab(self.launch_tab, "Launch Options")
        
        right_layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save Configuration")
        self.save_btn.clicked.connect(self._save_current_config)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        
        self.test_btn = QPushButton("Test Launch")
        self.test_btn.clicked.connect(self._test_launch)
        self.test_btn.setEnabled(False)
        button_layout.addWidget(self.test_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        right_layout.addLayout(button_layout)
        
        layout.addWidget(right_panel, stretch=2)
    
    def _create_core_tab(self): #vers 1
        """Create core selection tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Core selection group
        core_group = QGroupBox("Emulator Core")
        core_layout = QFormLayout(core_group)
        
        # Core dropdown
        self.core_combo = QComboBox()
        self.core_combo.addItem("(Auto-detect)", None)
        core_layout.addRow("Core:", self.core_combo)
        
        # Browse Core button
        browse_core_layout = QHBoxLayout()
        self.core_path_edit = QLineEdit()
        self.core_path_edit.setReadOnly(True)
        self.core_path_edit.setPlaceholderText("Or browse for core file...")
        browse_core_layout.addWidget(self.core_path_edit)
        
        browse_core_btn = QPushButton("Browse Core...")
        browse_core_btn.clicked.connect(self._browse_core)
        browse_core_layout.addWidget(browse_core_btn)
        
        core_layout.addRow("Custom:", browse_core_layout)
        
        # Core info
        self.core_info = QTextEdit()
        self.core_info.setReadOnly(True)
        self.core_info.setMaximumHeight(80)
        core_layout.addRow("Info:", self.core_info)
        
        layout.addWidget(core_group)
        
        # BIOS group
        bios_group = QGroupBox("BIOS Settings")
        bios_layout = QFormLayout(bios_group)
        
        self.bios_required = QCheckBox("BIOS Required")
        self.bios_required.setEnabled(False)
        bios_layout.addRow("Status:", self.bios_required)
        
        self.bios_path = QLineEdit()
        self.bios_path.setReadOnly(True)
        bios_layout.addRow("Path:", self.bios_path)
        
        bios_browse_btn = QPushButton("Browse...")
        bios_browse_btn.clicked.connect(self._browse_bios)
        bios_layout.addRow("", bios_browse_btn)
        
        layout.addWidget(bios_group)
        
        layout.addStretch()
        
        return tab
    
    def _create_launch_tab(self): #vers 1
        """Create launch options tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Launch options group
        options_group = QGroupBox("Launch Options")
        options_layout = QFormLayout(options_group)
        
        # Custom arguments
        self.custom_args = QLineEdit()
        self.custom_args.setPlaceholderText("e.g., --fullscreen --filter bilinear")
        options_layout.addRow("Arguments:", self.custom_args)
        
        # Working directory
        self.working_dir = QLineEdit()
        options_layout.addRow("Working Dir:", self.working_dir)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_working_dir)
        options_layout.addRow("", browse_btn)
        
        layout.addWidget(options_group)
        
        # Behavior group
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QVBoxLayout(behavior_group)
        
        self.fullscreen_check = QCheckBox("Start in fullscreen")
        behavior_layout.addWidget(self.fullscreen_check)
        
        self.save_state_check = QCheckBox("Auto-load save state")
        behavior_layout.addWidget(self.save_state_check)
        
        self.aspect_ratio_check = QCheckBox("Maintain aspect ratio")
        self.aspect_ratio_check.setChecked(True)
        behavior_layout.addWidget(self.aspect_ratio_check)
        
        layout.addWidget(behavior_group)
        
        layout.addStretch()
        
        return tab
    
    def _on_game_selected(self, index): #vers 1
        """Handle game selection"""
        if index < 0:
            return
        
        self.current_game = self.games[index]
        self.game_title.setText(f"<b>{self.current_game}</b>")
        
        # Load config for this game
        self._load_config_for_game()
        
        # Enable buttons
        self.save_btn.setEnabled(True)
        self.test_btn.setEnabled(True)
    
    def _load_config_for_game(self): #vers 1
        """Load configuration for current game"""
        if not self.current_game:
            return
        
        # Get saved config
        self.current_config = self.game_config.get_config(self.platform, self.current_game)
        
        # Populate available cores
        self._populate_core_list()
        
        # Load core selection
        preferred_core = self.current_config.get("core")
        if preferred_core:
            index = self.core_combo.findData(preferred_core)
            if index >= 0:
                self.core_combo.setCurrentIndex(index)
        else:
            self.core_combo.setCurrentIndex(0)  # Auto-detect
        
        # Load launch options
        self.custom_args.setText(self.current_config.get("custom_args", ""))
        self.working_dir.setText(self.current_config.get("working_dir", ""))
        self.fullscreen_check.setChecked(self.current_config.get("fullscreen", False))
        self.save_state_check.setChecked(self.current_config.get("auto_load_save", False))
        self.aspect_ratio_check.setChecked(self.current_config.get("maintain_aspect", True))
        
        # Update BIOS info
        platform_info = self.core_downloader.get_core_info(self.platform)
        if platform_info:
            bios_required = platform_info.get("bios_required", False)
            self.bios_required.setChecked(bios_required)
            
            if bios_required:
                bios_path = self.core_launcher.bios_dir / self.platform
                self.bios_path.setText(str(bios_path))
    
    def _populate_core_list(self): #vers 1
        """Populate core dropdown with available cores"""
        self.core_combo.clear()
        self.core_combo.addItem("(Auto-detect)", None)
        
        # Get cores for this platform
        platform_info = self.core_downloader.get_core_info(self.platform)
        if not platform_info:
            return
        
        cores = platform_info.get("cores", [])
        installed_cores = self.core_downloader.get_installed_cores()
        
        for core_name in cores:
            # Check if core is installed
            is_installed = core_name in installed_cores
            display_name = core_name
            if is_installed:
                display_name += " âœ“"
            else:
                display_name += " (not installed)"
            
            self.core_combo.addItem(display_name, core_name)
    
    def _save_current_config(self): #vers 1
        """Save current configuration"""
        if not self.current_game:
            return
        
        # Build config dict
        config = {
            "platform": self.platform,
            "game": self.current_game,
            "core": self.core_combo.currentData(),
            "custom_args": self.custom_args.text(),
            "working_dir": self.working_dir.text(),
            "fullscreen": self.fullscreen_check.isChecked(),
            "auto_load_save": self.save_state_check.isChecked(),
            "maintain_aspect": self.aspect_ratio_check.isChecked()
        }
        
        # Save to file
        success = self.game_config.save_config(self.platform, self.current_game, config)
        
        if success:
            QMessageBox.information(
                self,
                "Configuration Saved",
                f"Configuration saved for:\n{self.current_game}"
            )
            self.config_saved.emit(self.platform, self.current_game)
        else:
            QMessageBox.warning(
                self,
                "Save Failed",
                f"Failed to save configuration for:\n{self.current_game}"
            )
    
    def _test_launch(self): #vers 1
        """Test launch with current configuration"""
        if not self.current_game:
            return
        
        # TODO: Implement test launch
        QMessageBox.information(
            self,
            "Test Launch",
            f"Would launch: {self.current_game}\n"
            f"Core: {self.core_combo.currentData() or 'Auto'}\n"
            f"Args: {self.custom_args.text()}"
        )
    
    def _browse_core(self): #vers 1
        """Browse for core file"""
        from PyQt6.QtWidgets import QFileDialog
        
        # Determine file filter based on OS
        import platform
        system = platform.system()
        
        if system == "Windows":
            filter_str = "Core Files (*.dll);;All Files (*)"
            extension = ".dll"
        elif system == "Darwin":  # macOS
            filter_str = "Core Files (*.dylib);;All Files (*)"
            extension = ".dylib"
        else:  # Linux
            filter_str = "Core Files (*.so);;All Files (*)"
            extension = ".so"
        
        # Start in cores directory
        start_dir = str(self.core_launcher.cores_dir)
        
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Core File",
            start_dir,
            filter_str
        )
        
        if not filename:
            return
        
        core_path = Path(filename)
        
        # Validate it's a core file
        if not core_path.exists():
            QMessageBox.warning(
                self,
                "Invalid File",
                "Selected file does not exist."
            )
            return
        
        if core_path.suffix not in ['.so', '.dll', '.dylib']:
            QMessageBox.warning(
                self,
                "Invalid Core",
                f"Selected file does not appear to be a core file.\n\n"
                f"Expected extension: {extension}\n"
                f"Got: {core_path.suffix}"
            )
            return
        
        # Extract core name from filename
        # e.g., "puae_libretro.so" -> "puae"
        core_filename = core_path.stem
        if "_libretro" in core_filename:
            core_name = core_filename.replace("_libretro", "")
        else:
            core_name = core_filename
        
        # Update UI
        self.core_path_edit.setText(str(core_path))
        
        # Update core info
        self.core_info.setHtml(
            f"<b>Custom Core Selected:</b><br>"
            f"Name: {core_name}<br>"
            f"Path: {core_path}<br>"
            f"Size: {core_path.stat().st_size / 1024:.1f} KB"
        )
        
        # Add to combo if not already there
        index = self.core_combo.findData(core_name)
        if index < 0:
            self.core_combo.addItem(f"{core_name} (custom)", core_name)
            index = self.core_combo.count() - 1
        
        self.core_combo.setCurrentIndex(index)
        
        QMessageBox.information(
            self,
            "Core Loaded",
            f"Loaded core: {core_name}\n\n"
            f"This core will be saved with the game configuration."
        )
    
    def _browse_bios(self): #vers 1
        """Browse for BIOS directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select BIOS Directory",
            str(self.core_launcher.bios_dir)
        )
        
        if directory:
            self.bios_path.setText(directory)
    
    def _browse_working_dir(self): #vers 1
        """Browse for working directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Working Directory",
            str(Path.cwd())
        )
        
        if directory:
            self.working_dir.setText(directory)


# Standalone testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Mock data
    games = ["Game 1", "Game 2", "Game 3"]
    config = GameConfig(Path.cwd() / "config")
    
    dialog = GameManagerDialog(
        "PlayStation 1",
        games,
        None,  # core_downloader
        None,  # core_launcher
        config
    )
    
    dialog.exec()
