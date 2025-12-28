# X-Seti - December27 2025 - Multi-Emulator Launcher - Settings Dialog
#this belongs in apps/gui/mel_settings_dialog.py - Version: 11
"""
MEL Settings Dialog
Provides UI for configuring Multi-Emulator Launcher settings
Includes paths, emulators, debug, display, and cap32-specific settings
"""

from PyQt6.QtWidgets import (QDialog, QTabWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLineEdit, QPushButton, QCheckBox,
                             QSpinBox, QComboBox, QGroupBox, QLabel, QFileDialog,
                             QDialogButtonBox, QWidget)
from PyQt6.QtCore import Qt
from pathlib import Path

##Methods list -
# __init__
# _create_buttons
# _create_debug_tab
# _create_display_tab
# _create_emulators_tab
# _create_paths_tab
# _get_settings
# _save_settings
# _setup_debug_tab
# _setup_display_tab
# _setup_emulators_tab
# _setup_paths_tab

class MELSettingsDialog(QDialog): #vers 11
    """Settings dialog for Multi-Emulator Launcher"""
    
    def __init__(self, mel_settings, parent=None): #vers 3
        """Initialize settings dialog
        
        Args:
            mel_settings: MELSettingsManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.mel_settings = mel_settings
        self.setWindowTitle("MEL Settings")
        self.setMinimumSize(700, 600)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self._create_paths_tab()
        self._create_emulators_tab()
        self._create_debug_tab()
        self._create_display_tab()
        
        layout.addWidget(self.tabs)
        
        # Buttons
        buttons = self._create_buttons()
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def _create_paths_tab(self): #vers 1
        """Create paths configuration tab"""
        tab = QWidget()
        self._setup_paths_tab(tab)
        self.tabs.addTab(tab, "Paths")
    
    def _create_emulators_tab(self): #vers 1
        """Create emulators configuration tab"""
        tab = QWidget()
        self._setup_emulators_tab(tab)
        self.tabs.addTab(tab, "Emulators")
    
    def _create_debug_tab(self): #vers 1
        """Create debug settings tab"""
        tab = QWidget()
        self._setup_debug_tab(tab)
        self.tabs.addTab(tab, "Debug")
    
    def _create_display_tab(self): #vers 1
        """Create display settings tab"""
        tab = QWidget()
        self._setup_display_tab(tab)
        self.tabs.addTab(tab, "Display")
    
    def _setup_paths_tab(self, tab): #vers 1
        """Setup paths tab widgets
        
        Args:
            tab: QWidget to setup
        """
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # ROM paths
        rom_group = QGroupBox("ROM Paths")
        rom_layout = QVBoxLayout()
        
        # Primary ROM path
        rom_path_layout = QHBoxLayout()
        self.rom_path_edit = QLineEdit(str(self.mel_settings.get_rom_path()))
        rom_path_btn = QPushButton("Browse...")
        rom_path_btn.clicked.connect(lambda: self._browse_folder(self.rom_path_edit))
        rom_path_layout.addWidget(self.rom_path_edit)
        rom_path_layout.addWidget(rom_path_btn)
        rom_layout.addLayout(rom_path_layout)
        
        rom_group.setLayout(rom_layout)
        layout.addWidget(rom_group)
        
        # BIOS path
        bios_group = QGroupBox("BIOS Path")
        bios_layout = QHBoxLayout()
        self.bios_path_edit = QLineEdit(str(self.mel_settings.get_bios_path()))
        bios_btn = QPushButton("Browse...")
        bios_btn.clicked.connect(lambda: self._browse_folder(self.bios_path_edit))
        bios_layout.addWidget(self.bios_path_edit)
        bios_layout.addWidget(bios_btn)
        bios_group.setLayout(bios_layout)
        layout.addWidget(bios_group)
        
        # Cores path
        cores_group = QGroupBox("Libretro Cores Path")
        cores_layout = QHBoxLayout()
        self.cores_path_edit = QLineEdit(str(self.mel_settings.get_core_path()))
        cores_btn = QPushButton("Browse...")
        cores_btn.clicked.connect(lambda: self._browse_folder(self.cores_path_edit))
        cores_layout.addWidget(self.cores_path_edit)
        cores_layout.addWidget(cores_btn)
        cores_group.setLayout(cores_layout)
        layout.addWidget(cores_group)
        
        # Saves path
        saves_group = QGroupBox("Save States Path")
        saves_layout = QHBoxLayout()
        self.saves_path_edit = QLineEdit(str(self.mel_settings.get_saves_path()))
        saves_btn = QPushButton("Browse...")
        saves_btn.clicked.connect(lambda: self._browse_folder(self.saves_path_edit))
        saves_layout.addWidget(self.saves_path_edit)
        saves_layout.addWidget(saves_btn)
        saves_group.setLayout(saves_layout)
        layout.addWidget(saves_group)
        
        layout.addStretch()
        tab.setLayout(layout)
    
    def _setup_emulators_tab(self, tab): #vers 2
        """Setup emulators tab widgets
        
        Args:
            tab: QWidget to setup
        """
        layout = QVBoxLayout()
        
        # Caprice32 Specific Settings
        cap32_group = QGroupBox("Caprice32 (Amstrad CPC) Settings")
        cap32_layout = QFormLayout()
        
        # Scale factor
        self.cap32_scale_combo = QComboBox()
        scale_options = [
            "1 - 384×270 (Tiny)",
            "2 - 768×540 (Default)",
            "3 - 1152×810 (Recommended)",
            "4 - 1536×1080 (Large)",
            "5 - 1920×1350 (XL)",
            "6 - 2304×1620 (XXL)",
            "7 - 2688×1890 (XXXL)",
            "8 - 3072×2160 (4K)"
        ]
        self.cap32_scale_combo.addItems(scale_options)
        scale = self.mel_settings.get_cap32_scale() if hasattr(self.mel_settings, 'get_cap32_scale') else 3
        self.cap32_scale_combo.setCurrentIndex(scale - 1)
        cap32_layout.addRow("Window Scale:", self.cap32_scale_combo)
        
        # Rendering style
        self.cap32_style_combo = QComboBox()
        style_options = [
            "0 - Half size with hardware flip",
            "1 - Double size with hardware flip",
            "2 - Half size",
            "3 - Double size",
            "4 - Super eagle",
            "5 - Scale2x",
            "6 - Advanced Scale2x",
            "7 - TV 2x",
            "8 - Software bilinear",
            "9 - Software bicubic",
            "10 - Dot matrix",
            "11 - OpenGL scaling (Recommended)"
        ]
        self.cap32_style_combo.addItems(style_options)
        style = self.mel_settings.get_cap32_style() if hasattr(self.mel_settings, 'get_cap32_style') else 11
        self.cap32_style_combo.setCurrentIndex(style)
        cap32_layout.addRow("Rendering Style:", self.cap32_style_combo)
        
        # Window mode
        self.cap32_window_check = QCheckBox("Windowed mode (unchecked = fullscreen)")
        window_mode = self.mel_settings.get_cap32_window_mode() if hasattr(self.mel_settings, 'get_cap32_window_mode') else 1
        self.cap32_window_check.setChecked(window_mode == 1)
        cap32_layout.addRow("", self.cap32_window_check)
        
        # Preserve aspect ratio
        self.cap32_aspect_check = QCheckBox("Preserve aspect ratio")
        aspect = self.mel_settings.get_cap32_preserve_aspect() if hasattr(self.mel_settings, 'get_cap32_preserve_aspect') else 1
        self.cap32_aspect_check.setChecked(aspect == 1)
        cap32_layout.addRow("", self.cap32_aspect_check)
        
        # OpenGL filter
        self.cap32_filter_check = QCheckBox("OpenGL filter (for style 11)")
        oglfilter = self.mel_settings.get_cap32_oglfilter() if hasattr(self.mel_settings, 'get_cap32_oglfilter') else 1
        self.cap32_filter_check.setChecked(oglfilter == 1)
        cap32_layout.addRow("", self.cap32_filter_check)
        
        # Info label
        cap32_info = QLabel("These settings control Caprice32 emulator video output.\n"
                           "Scale 3 + Style 11 (OpenGL) recommended for best quality.")
        cap32_info.setWordWrap(True)
        cap32_info.setStyleSheet("color: gray; font-size: 10px; margin-top: 10px;")
        cap32_layout.addRow(cap32_info)
        
        cap32_group.setLayout(cap32_layout)
        layout.addWidget(cap32_group)
        
        layout.addStretch()
        tab.setLayout(layout)
    
    def _setup_debug_tab(self, tab): #vers 1
        """Setup debug tab widgets
        
        Args:
            tab: QWidget to setup
        """
        layout = QVBoxLayout()
        
        # Debug settings group
        debug_group = QGroupBox("Debug Settings")
        debug_layout = QFormLayout()
        
        # Debug mode
        self.debug_mode_check = QCheckBox("Enable debug mode")
        debug_mode = self.mel_settings.get_debug_mode() if hasattr(self.mel_settings, 'get_debug_mode') else False
        self.debug_mode_check.setChecked(debug_mode)
        debug_layout.addRow("", self.debug_mode_check)
        
        # Verbose logging
        self.verbose_check = QCheckBox("Verbose logging")
        verbose = self.mel_settings.get_verbose_logging() if hasattr(self.mel_settings, 'get_verbose_logging') else False
        self.verbose_check.setChecked(verbose)
        debug_layout.addRow("", self.verbose_check)
        
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)
        
        layout.addStretch()
        tab.setLayout(layout)
    
    def _setup_display_tab(self, tab): #vers 2
        """Setup display tab widgets
        
        Args:
            tab: QWidget to setup
        """
        layout = QVBoxLayout()
        
        # Emulator Window Settings
        emu_window_group = QGroupBox("Emulator Window")
        emu_window_layout = QFormLayout()
        
        # Window width
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(320, 3840)
        self.window_width_spin.setSingleStep(100)
        width = self.mel_settings.get_emulator_window_width() if hasattr(self.mel_settings, 'get_emulator_window_width') else 800
        self.window_width_spin.setValue(width)
        emu_window_layout.addRow("Width:", self.window_width_spin)
        
        # Window height
        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(240, 2160)
        self.window_height_spin.setSingleStep(100)
        height = self.mel_settings.get_emulator_window_height() if hasattr(self.mel_settings, 'get_emulator_window_height') else 600
        self.window_height_spin.setValue(height)
        emu_window_layout.addRow("Height:", self.window_height_spin)
        
        # Info label
        window_info = QLabel("Window size is passed to emulators when launching.\n"
                            "Note: Some emulators ignore these settings.")
        window_info.setWordWrap(True)
        window_info.setStyleSheet("color: gray; font-size: 10px;")
        emu_window_layout.addRow(window_info)
        
        emu_window_group.setLayout(emu_window_layout)
        layout.addWidget(emu_window_group)
        
        layout.addStretch()
        tab.setLayout(layout)
    
    def _browse_folder(self, line_edit): #vers 1
        """Open folder browser and update line edit
        
        Args:
            line_edit: QLineEdit to update with selected folder
        """
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            line_edit.text() or str(Path.home())
        )
        
        if folder:
            line_edit.setText(folder)
    
    def _create_buttons(self): #vers 1
        """Create dialog buttons
        
        Returns:
            QDialogButtonBox with OK and Cancel buttons
        """
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        
        buttons.accepted.connect(self._save_settings)
        buttons.rejected.connect(self.reject)
        
        return buttons
    
    def _get_settings(self): #vers 2
        """Get settings from UI controls
        
        Returns:
            Dictionary of settings
        """
        settings = {}
        
        # Paths
        settings['rom_path'] = self.rom_path_edit.text()
        settings['bios_path'] = self.bios_path_edit.text()
        settings['cores_path'] = self.cores_path_edit.text()
        settings['saves_path'] = self.saves_path_edit.text()
        
        # Caprice32 settings
        settings['cap32_scale'] = self.cap32_scale_combo.currentIndex() + 1
        settings['cap32_style'] = self.cap32_style_combo.currentIndex()
        settings['cap32_window'] = 1 if self.cap32_window_check.isChecked() else 0
        settings['cap32_preserve_aspect'] = 1 if self.cap32_aspect_check.isChecked() else 0
        settings['cap32_oglfilter'] = 1 if self.cap32_filter_check.isChecked() else 0
        
        # Debug settings
        settings['debug_mode'] = self.debug_mode_check.isChecked()
        settings['verbose_logging'] = self.verbose_check.isChecked()
        
        # Display settings
        settings['emulator_window_width'] = self.window_width_spin.value()
        settings['emulator_window_height'] = self.window_height_spin.value()
        
        return settings
    
    def _save_settings(self): #vers 2
        """Save settings from UI to mel_settings"""
        settings = self._get_settings()
        
        # Save paths
        self.mel_settings.set_rom_path(Path(settings['rom_path']))
        self.mel_settings.set_bios_path(Path(settings['bios_path']))
        self.mel_settings.set_core_path(Path(settings['cores_path']))
        self.mel_settings.set_saves_path(Path(settings['saves_path']))
        
        # Save cap32 settings
        if hasattr(self.mel_settings, 'set_cap32_scale'):
            self.mel_settings.set_cap32_scale(settings['cap32_scale'])
            self.mel_settings.set_cap32_style(settings['cap32_style'])
            self.mel_settings.set_cap32_window_mode(settings['cap32_window'])
            self.mel_settings.set_cap32_preserve_aspect(settings['cap32_preserve_aspect'])
            self.mel_settings.set_cap32_oglfilter(settings['cap32_oglfilter'])
        
        # Save debug settings
        if hasattr(self.mel_settings, 'set_debug_mode'):
            self.mel_settings.set_debug_mode(settings['debug_mode'])
        if hasattr(self.mel_settings, 'set_verbose_logging'):
            self.mel_settings.set_verbose_logging(settings['verbose_logging'])
        
        # Save display settings
        if hasattr(self.mel_settings, 'set_emulator_window_width'):
            self.mel_settings.set_emulator_window_width(settings['emulator_window_width'])
            self.mel_settings.set_emulator_window_height(settings['emulator_window_height'])
        
        self.accept()
