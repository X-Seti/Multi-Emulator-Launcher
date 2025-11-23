#!/usr/bin/env python3
#this belongs in apps/gui/emu_launcher_gui.py - Version: 12
# X-Seti - November22 2025 - Multi-Emulator Launcher - Main GUI

"""
Multi-Emulator Launcher GUI
Main window with 3-panel layout for emulator management
Clean version: No hardcoded colors, uses AppSettings theme system
"""

#TODO - def _create_icon_controls(self): #vers 2 exists but the icons are missing from the _create_right_panel.


#Changelog

#November22 v12 - Fixed themed titlebar setting to actually work
#- Updated _apply_titlebar_colors (vers 4) to check use_themed_titlebar setting
#- Updated _open_mel_settings (vers 2) to reapply titlebar colors after saving settings
#- Unchecked: White text on dark blue background (always visible)
#- Checked: Uses theme colors from AppSettings
#- Setting now properly toggles between hardcoded and themed titlebar

#November22 v11 - Fixed titlebar button visibility and updated icons to 64x64
#- Fixed _apply_titlebar_colors (vers 3) - buttons now use accent color backgrounds for visibility
#- Updated EmulatorListWidget icon size from 32x32 to 64x64
#- Created mel_settings_dialog.py v4 with themed titlebar checkbox
#- Titlebar buttons now visible in both light and dark themes
#- Better contrast with colored button backgrounds and borders

#November22 v10 - CRITICAL FIX: Theme system now works properly
#- Fixed _apply_titlebar_colors (vers 2) - removed duplicate stylesheet code that was overriding AppSettings
#- Fixed _show_settings_dialog (vers 2) - connects to _on_theme_changed not _apply_theme
#- Theme switching now applies correctly on startup and when changed
#- Removed conflicting stylesheet code that prevented AppSettings themes from loading

#November22 v9 - Added artwork system
#- Created artwork_loader.py (vers 1) for game thumbnails and title images
#- Updated GameListWidget (vers 2) to display 64x64 thumbnails in game list
#- Updated EmulatorDisplayWidget (vers 3) to show title artwork
#- Added show_title_artwork method to display panel
#- Updated _on_platform_selected (vers 4) to pass artwork_loader to game list
#- Updated _on_game_selected (vers 3) to load title artwork on selection
#- Fixed AppSettings signal: uses themeChanged not theme_changed
#- Artwork structure: /artwork/[platform]/thumbnails/ and /artwork/[platform]/titles/

#November22 v8 - Fixed theme switching
#- Connected app_settings.theme_changed signal in __init__
#- Added _on_theme_changed method (vers 1) to handle theme changes
#- Theme switching now works properly instead of staying in fallback

#November22 v7 - Fixed theme integration issues
#- Removed obsolete _apply_table_theme_styling method (no self.table widget)
#- Updated _apply_theme (vers 2) to call _apply_titlebar_colors
#- Added _apply_titlebar_colors (vers 1) for titlebar text/button visibility in dark themes
#- Fixed AttributeError on startup

#November20 - Added - PlatformScanner for dynamic platform discovery
#- 1. Add PlatformScanner import at top
#- 2. Initialize platform_scanner in __init__ (vers 5)
#- 3. Update _create_left_panel to use scanner (vers 2)
#- 4. Add _refresh_platforms method (vers 1)
#- 5. Update _on_platform_selected to use platform info (vers 3)

import os
import tempfile
import subprocess
import shutil
import struct
import sys
import io
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from PyQt6.QtSvg import QSvgRenderer

# PyQt6 imports
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QListWidgetItem, QLabel, QPushButton, QFrame, QTabWidget, QGroupBox, QFormLayout, QDialog, QMessageBox, QTextBrowser)
from PyQt6.QtWidgets import (QApplication, QSlider, QCheckBox,
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QDialog, QFormLayout, QSpinBox,  QListWidgetItem, QLabel, QPushButton, QFrame, QFileDialog, QLineEdit, QTextEdit, QMessageBox, QScrollArea, QGroupBox, QTableWidget, QTableWidgetItem, QColorDialog, QHeaderView, QAbstractItemView, QMenu, QComboBox, QInputDialog, QTabWidget, QDoubleSpinBox, QRadioButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint, QRect, QByteArray
from PyQt6.QtGui import QFont, QIcon, QPixmap, QImage, QPainter, QPen, QBrush,  QColor, QCursor
from PyQt6.QtSvg import QSvgRenderer

# Import SVG icon factory
from apps.methods.svg_icon_factory import SVGIconFactory
from apps.methods.platform_scanner import PlatformScanner
from apps.methods.platform_icons import PlatformIcons
from apps.methods.artwork_loader import ArtworkLoader
from apps.gui.mel_settings_dialog import MELSettingsDialog
from apps.utils.mel_settings_manager import MELSettingsManager

# Import AppSettings
try:
    from apps.utils.app_settings_system import AppSettings, SettingsDialog
    APPSETTINGS_AVAILABLE = True
except ImportError:
    APPSETTINGS_AVAILABLE = False
    print("Warning: AppSettings not available")

##METHODS LIST ORDER (ALPHABETICAL):
# __init__
# closeEvent
# mouseDoubleClickEvent
# mouseMoveEvent
# mousePressEvent
# mouseReleaseEvent
# paintEvent
# resizeEvent
# setup_ui
# _apply_fallback_theme          # NEW - after _apply_table_theme_styling
# _apply_theme                    # UPDATED vers 2
# _apply_titlebar_colors          # NEW vers 1 - applies theme colors to titlebar
# _browse_and_scan                # NEW - after _apply_theme, before _create_*
# _create_close_icon              # NEW
# _create_left_panel
# _create_maximize_icon           # NEW
# _create_middle_panel
# _create_minimize_icon           # NEW
# _create_right_panel
# _create_status_bar
# _create_titlebar                # UPDATED
# _enable_move_mode
# _get_resize_corner
# _get_theme_colors
# _handle_corner_resize
# _is_on_draggable_area
# _load_fonts_from_settings
# _on_game_selected               # UPDATED
# _on_launch_game                 # NEW - after _on_game_selected
# _on_platform_selected
# _on_stop_emulation              # NEW - after _on_platform_selected
# _on_theme_changed               # UPDATED
# _open_mel_settings              # UPDATED - after _on_theme_changed
# _open_rom_folder                # NEW - after _open_mel_settings
# _refresh_platforms              # UPDATED
# _save_config                    # NEW - after _refresh_platforms
# _scan_roms                      # UPDATED
# _setup_controller               # UPDATED
# _show_about_dialog              # NEW - after _setup_controller
# _show_scan_roms_context_menu    # NEW - after _show_about_dialog
# _show_settings_context_menu
# _show_settings_dialog
# _show_shaders_dialog
# _show_window_context_menu
# _toggle_maximize
# _toggle_upscale_native
# _update_cursor


# App configuration
App_name = "Multi-Emulator Launcher"
DEBUG_STANDALONE = True

class EmulatorListWidget(QListWidget): #vers 2
    """Panel 1: List of emulator platforms with icon support"""

    platform_selected = pyqtSignal(str)

    def __init__(self, parent=None, display_mode="icons_and_text"): #vers 4
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.currentRowChanged.connect(self.on_selection_changed)
        self.display_mode = display_mode
        self.setIconSize(QSize(64, 64))  # Increased from 32x32 to 64x64

        # Enable context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Hidden platforms storage
        self.hidden_platforms = set()

    def on_selection_changed(self, row): #vers 2
        """Handle platform selection"""
        if row >= 0:
            item = self.item(row)
            platform = item.data(Qt.ItemDataRole.UserRole)
            if not platform:
                platform = item.text()
            self.platform_selected.emit(platform)


    def populate_platforms(self, platforms, icon_factory=None): #vers 2
        """Populate with platform names and optional icons

        Args:
            platforms: List of platform names
            icon_factory: PlatformIcons instance for generating icons
        """
        self.clear()
        for platform in platforms:
            item = QListWidgetItem()

            # Set icon if available and mode allows
            if icon_factory and self.display_mode != "text_only":
                icon = icon_factory.get_platform_icon(platform, size=32)
                item.setIcon(icon)

            # Set text based on display mode
            if self.display_mode == "icons_only":
                item.setText("")
                item.setToolTip(platform)  # Show name on hover
            else:
                item.setText(platform)

            # Store platform name in data
            item.setData(Qt.ItemDataRole.UserRole, platform)
            self.addItem(item)


    def set_display_mode(self, mode): #vers 1
        """Change display mode and refresh

        Args:
            mode: "icons_only", "text_only", or "icons_and_text"
        """
        self.display_mode = mode

        # Update existing items
        for i in range(self.count()):
            item = self.item(i)
            platform = item.data(Qt.ItemDataRole.UserRole)

            if mode == "icons_only":
                item.setText("")
                item.setToolTip(platform)
            elif mode == "text_only":
                item.setText(platform)
                item.setIcon(QIcon())  # Remove icon
            else:  # icons_and_text
                item.setText(platform)


    def _show_context_menu(self, position): #vers 3
        """Show right-click context menu"""
        item = self.itemAt(position)

        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)

        # If clicked on an item, show platform options
        if item:
            platform = item.data(Qt.ItemDataRole.UserRole)
            if not platform:
                platform = item.text()

            # Configure controller for this platform
            config_action = menu.addAction(f"Configure Controller for {platform}")
            config_action.triggered.connect(lambda: self._configure_platform_controller(platform))

            menu.addSeparator()

            hide_action = menu.addAction(f"Hide {platform}")
            hide_action.triggered.connect(lambda: self._hide_platform(platform))

            menu.addSeparator()

        # Show hidden platforms submenu (always available)
        if self.hidden_platforms:
            hidden_menu = menu.addMenu("Show Hidden Platform")
            for hidden_platform in sorted(self.hidden_platforms):
                show_action = hidden_menu.addAction(hidden_platform)
                show_action.triggered.connect(lambda checked, p=hidden_platform: self._show_platform(p))

            menu.addSeparator()
            show_all_action = menu.addAction(f"Show All Hidden ({len(self.hidden_platforms)})")
            show_all_action.triggered.connect(self._show_all_platforms)

        menu.exec(self.mapToGlobal(position))


    def _configure_platform_controller(self, platform): #vers 1
        """Open controller config for specific platform"""
        # Find parent EmuLauncherGUI
        parent_widget = self.parent()
        while parent_widget and not hasattr(parent_widget, '_setup_controller'):
            parent_widget = parent_widget.parent()

        if parent_widget and hasattr(parent_widget, '_setup_controller'):
            # Open controller dialog with platform pre-selected
            from apps.gui.controller_config_dialog import ControllerConfigDialog
            dialog = ControllerConfigDialog(parent_widget.gamepad_config, parent_widget)
            # TODO: Select platform tab and highlight platform
            dialog.exec()


    def _show_all_platforms(self): #vers 1
        """Show all hidden platforms at once"""
        self.hidden_platforms.clear()

        # Trigger parent refresh to reload all platforms
        if self.parent():
            parent_widget = self.parent()
            while parent_widget and not hasattr(parent_widget, '_refresh_platforms'):
                parent_widget = parent_widget.parent()
            if parent_widget and hasattr(parent_widget, '_refresh_platforms'):
                parent_widget._refresh_platforms()


    def _hide_platform(self, platform): #vers 1
        """Hide a platform from the list"""
        self.hidden_platforms.add(platform)

        # Remove from list
        for i in range(self.count()):
            item = self.item(i)
            item_platform = item.data(Qt.ItemDataRole.UserRole)
            if not item_platform:
                item_platform = item.text()
            if item_platform == platform:
                self.takeItem(i)
                break


    def _show_platform(self, platform): #vers 1
        """Show a hidden platform"""
        self.hidden_platforms.discard(platform)

        # Would need to re-scan to add it back
        # Trigger parent refresh
        if self.parent():
            parent_widget = self.parent()
            while parent_widget and not hasattr(parent_widget, '_refresh_platforms'):
                parent_widget = parent_widget.parent()
            if parent_widget and hasattr(parent_widget, '_refresh_platforms'):
                parent_widget._refresh_platforms()


    def on_selection_changed(self, row): #vers 2
        """Handle platform selection"""
        if row >= 0:
            item = self.item(row)
            platform = item.data(Qt.ItemDataRole.UserRole)
            if not platform:
                platform = item.text()
            self.platform_selected.emit(platform)


    def populate_platforms(self, platforms, icon_factory=None): #vers 3
        """Populate with platform names and optional icons"""
        self.clear()
        for platform in platforms:
            # Skip hidden platforms
            if platform in self.hidden_platforms:
                continue

            item = QListWidgetItem()

            # Set icon if available and mode allows
            if icon_factory and self.display_mode != "text_only":
                icon = icon_factory.get_platform_icon(platform, size=32)
                item.setIcon(icon)

            # Set text based on display mode
            if self.display_mode == "icons_only":
                item.setText("")
                item.setToolTip(platform)
            else:
                item.setText(platform)

            # Store platform name in data
            item.setData(Qt.ItemDataRole.UserRole, platform)
            self.addItem(item)


    def set_display_mode(self, mode): #vers 1
        """Change display mode and refresh"""
        self.display_mode = mode

        # Update existing items
        for i in range(self.count()):
            item = self.item(i)
            platform = item.data(Qt.ItemDataRole.UserRole)

            if mode == "icons_only":
                item.setText("")
                item.setToolTip(platform)
            elif mode == "text_only":
                item.setText(platform)
                item.setIcon(QIcon())
            else:  # icons_and_text
                item.setText(platform)


class GameListWidget(QListWidget): #vers 2
    """Panel 2: List of games for selected platform with artwork support"""
    
    game_selected = pyqtSignal(str)
    
    def __init__(self, parent=None): #vers 2
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.currentRowChanged.connect(self.on_selection_changed)
        self.setIconSize(QSize(64, 64))  # Set icon size for artwork
        self.artwork_loader = None
        self.current_platform = None
        

    def populate_games(self, games, artwork_loader=None, platform=None): #vers 2
        """Populate with game names and artwork thumbnails
        
        Args:
            games: List of game names
            artwork_loader: ArtworkLoader instance for thumbnails
            platform: Platform name for artwork lookup
        """
        self.clear()
        self.artwork_loader = artwork_loader
        self.current_platform = platform
        
        for game in games:
            item = QListWidgetItem()
            item.setText(game)
            
            # Add artwork thumbnail if available
            if artwork_loader and platform:
                icon = artwork_loader.get_game_icon(game, platform, size=64)
                item.setIcon(icon)
            
            self.addItem(item)
            

    def on_selection_changed(self, row): #vers 1
        """Handle game selection"""
        if row >= 0:
            game = self.item(row).text()
            self.game_selected.emit(game)


class EmulatorDisplayWidget(QWidget): #vers 3
    """Panel 3: Emulator display with controls and title artwork"""
    
    def __init__(self, parent=None, main_window=None): #vers 3
        super().__init__(parent)
        self.main_window = main_window
        self.title_artwork_label = None
        self.setup_ui()
        

    def setup_ui(self): #vers 4
        """Setup display panel with title artwork support"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Title artwork display (replaces generic label)
        self.title_artwork_label = QLabel()
        self.title_artwork_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_artwork_label.setScaledContents(True)
        self.title_artwork_label.setMinimumHeight(200)
        self.title_artwork_label.setText("Select a game")
        self.title_artwork_label.setStyleSheet("font-size: 14pt; padding: 50px;")
        main_layout.addWidget(self.title_artwork_label)

        main_layout.addStretch()

        # Control buttons at bottom
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(10, 5, 10, 5)

        # Launch button
        self.launch_btn = QPushButton("Launch Game")
        self.launch_btn.setMinimumHeight(30)
        if self.main_window:
            self.launch_btn.clicked.connect(self.main_window._on_launch_game)
        button_layout.addWidget(self.launch_btn)

        # Stop button
        self.gameart_btn = QPushButton("Game Art")
        self.gameart_btn.setMinimumHeight(30)
        button_layout.addWidget(self.gameart_btn)

        button_layout.addStretch()

        # Stop button
        self.manage_btn = QPushButton("Manage")
        self.manage_btn.setMinimumHeight(30)
        button_layout.addWidget(self.manage_btn)


        # Stop button
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setMinimumHeight(30)
        if self.main_window:
            self.stop_btn.clicked.connect(self.main_window._on_stop_emulation)
        button_layout.addWidget(self.stop_btn)

        main_layout.addWidget(button_frame)
    
    
    def show_title_artwork(self, pixmap): #vers 1
        """Display title artwork
        
        Args:
            pixmap: QPixmap with title artwork or None to clear
        """
        if pixmap and not pixmap.isNull():
            # Scale pixmap to fit while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.title_artwork_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.title_artwork_label.setPixmap(scaled_pixmap)
            self.title_artwork_label.setText("")
        else:
            # Clear artwork and show text
            self.title_artwork_label.clear()
            self.title_artwork_label.setText("No title artwork")
            self.title_artwork_label.setStyleSheet("font-size: 14pt; padding: 50px;")
        

    def _create_icon_controls(self): #vers 2
        """Create vertical icon control buttons"""
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        controls_frame.setMaximumWidth(50)
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(5, 5, 5, 5)
        controls_layout.setSpacing(5)
        
        # Volume Up
        vol_up_btn = QPushButton()
        vol_up_btn.setIcon(SVGIconFactory.volume_up_icon(20))
        vol_up_btn.setIconSize(QSize(20, 20))
        vol_up_btn.setFixedSize(40, 40)
        vol_up_btn.setToolTip("Volume Up")
        controls_layout.addWidget(vol_up_btn)
        
        # Volume Down
        vol_down_btn = QPushButton()
        vol_down_btn.setIcon(SVGIconFactory.volume_down_icon(20))
        vol_down_btn.setIconSize(QSize(20, 20))
        vol_down_btn.setFixedSize(40, 40)
        vol_down_btn.setToolTip("Volume Down")
        controls_layout.addWidget(vol_down_btn)
        
        controls_layout.addSpacing(10)
        
        # Screenshot
        screenshot_btn = QPushButton()
        screenshot_btn.setIcon(SVGIconFactory.screenshot_icon(20))
        screenshot_btn.setIconSize(QSize(20, 20))
        screenshot_btn.setFixedSize(40, 40)
        screenshot_btn.setToolTip("Screenshot")
        controls_layout.addWidget(screenshot_btn)
        
        # Record
        record_btn = QPushButton()
        record_btn.setIcon(SVGIconFactory.record_icon(20))
        record_btn.setIconSize(QSize(20, 20))
        record_btn.setFixedSize(40, 40)
        record_btn.setToolTip("Record")
        controls_layout.addWidget(record_btn)
        
        controls_layout.addStretch()
        
        return controls_frame
        
    def _create_control_buttons(self): #vers 2
        """Create bottom control buttons"""
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QHBoxLayout(controls_frame)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # Launch button
        self.launch_btn = QPushButton("Launch Game")
        # Connect to main window's launch method
        if self.main_window:
            self.launch_btn.clicked.connect(self.main_window._on_launch_game)
        layout.addWidget(self.launch_btn)

        layout.addStretch()

        # Stop button
        stop_btn = QPushButton("Stop")
        # Connect to main window's stop method
        if self.main_window:
            stop_btn.clicked.connect(self.main_window._on_stop_emulation)
        layout.addWidget(stop_btn)

        return controls_frame

        def enable_launch_buttons(self, enabled=True): #vers 1
            """Enable/disable launch buttons"""
            if hasattr(self, 'launch_btn'):
                self.launch_btn.setEnabled(enabled)
            if hasattr(self, 'quick_launch_btn'):
                self.quick_launch_btn.setEnabled(enabled)
    

    def _on_launch_clicked(self): #vers 1
        """Handle launch button click"""
        if not self.main_window:
            return
            
        platform = self.main_window.current_platform
        rom_path = self.main_window.current_rom_path
        core_launcher = self.main_window.core_launcher
        
        if not all([platform, rom_path, core_launcher]):
            QMessageBox.warning(self, "Launch Error", 
                "Please select a platform and game first")
            return
            
        self.main_window.status_label.setText(f"Launching {rom_path.name}...")
        
        success = core_launcher.launch_game(platform, rom_path)
        
        if success:
            self.main_window.status_label.setText(f"Running: {rom_path.name}")
        else:
            self.main_window.status_label.setText(f"Launch failed: {rom_path.name}")
            QMessageBox.warning(self, "Launch Failed",
                f"Could not launch {rom_path.name}\n\n"
                f"Check that you have the required emulator installed.\n"
                f"See terminal output for details.")
    

    def _on_stop_clicked(self): #vers 1
        """Handle stop button click"""
        if not self.main_window or not self.main_window.core_launcher:
            return
            
        core_launcher = self.main_window.core_launcher
        
        if core_launcher.is_running():
            success = core_launcher.stop_emulation()
            if success:
                self.main_window.status_label.setText("Emulation stopped")
            else:
                self.main_window.status_label.setText("Failed to stop emulation")
        else:
            self.main_window.status_label.setText("No emulation running")


class EmuLauncherGUI(QWidget): #vers 1
    """Main GUI window - Multi-Emulator Launcher"""

    window_closed = pyqtSignal()

    def __init__(self, parent=None, main_window=None, core_downloader=None,
             core_launcher=None, gamepad_config=None): #vers 5
        """Initialize GUI with AppSettings integration and core systems"""
        if DEBUG_STANDALONE:
            print(f"{App_name} Initializing...")

        super().__init__(parent)

        self.main_window = main_window
        self.button_display_mode = 'both'
        self.last_save_directory = None
        self.standalone_mode = (main_window is None)

        # Set default fonts
        from PyQt6.QtGui import QFont
        default_font = QFont("Fira Sans Condensed", 14)
        self.setFont(default_font)
        self.title_font = QFont("Arial", 14)
        self.panel_font = QFont("Arial", 10)
        self.button_font = QFont("Arial", 10)
        self.infobar_font = QFont("Courier New", 9)

        # Initialize MEL Settings Manager FIRST
        self.mel_settings = MELSettingsManager()

        # Initialize PlatformScanner with MEL settings path
        roms_dir = self.mel_settings.get_rom_path()
        self.platform_scanner = PlatformScanner(roms_dir)

        # Initialize core systems
        if not core_downloader:
            self.core_downloader = CoreDownloader(Path.cwd())
        else:
            self.core_downloader = core_downloader

        if not core_launcher:
            self.core_launcher = CoreLauncher(
                Path.cwd(),
                self.core_downloader.CORE_DATABASE
            )
        else:
            self.core_launcher = core_launcher

        # Load saved configuration
        if 'hidden_platforms' in self.mel_settings.settings:
            # Will be applied when platform_list is created
            self._saved_hidden_platforms = self.mel_settings.settings['hidden_platforms']

        if 'window_geometry' in self.mel_settings.settings:
            geom = self.mel_settings.settings['window_geometry']
            self.resize(geom.get('width', 1400), geom.get('height', 800))
            if 'x' in geom and 'y' in geom:
                self.move(geom['x'], geom['y'])

        self.gamepad_config = gamepad_config

        # Keyboard shortcut for display mode toggle
        # TODO - Create mel_shortcuts.py and add a tab section in settings to config the shortcuts
        from PyQt6.QtGui import QShortcut, QKeySequence
        self.display_toggle_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        self.display_toggle_shortcut.activated.connect(self._toggle_icon_display_mode)

        self.use_system_titlebar = False
        self.window_always_on_top = False

        # Window flags
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self._initialize_features()

        # Corner resize variables
        self.dragging = False
        self.drag_position = None
        self.resizing = False
        self.resize_corner = None
        self.corner_size = 20
        self.hover_corner = None

        # State tracking for launch functionality
        self.current_platform = None
        self.current_rom_path = None
        self.available_roms = {}

        # Initialize icon factory and display mode
        self.platform_icons = PlatformIcons()
        self.icon_display_mode = "icons_and_text"  # Default mode
        
        # Initialize artwork loader
        artwork_dir = Path.cwd() / "artwork"
        self.artwork_loader = ArtworkLoader(artwork_dir)

        # Initialize AppSettings
        if APPSETTINGS_AVAILABLE:
            self.app_settings = AppSettings()
            self._load_fonts_from_settings()
            # Connect theme change signal - SettingsDialog emits themeChanged
            # Note: We'll connect when SettingsDialog is created
        else:
            self.app_settings = None
            self.default_font = QFont("Segoe UI", 9)
            self.title_font = QFont("Adwaita Sans", 10)
            self.panel_font = QFont("Adwaita Sans", 9)
            self.button_font = QFont("Adwaita Sans", 9)

        # Window settings
        self.setWindowTitle(f"{App_name}: Ready")
        self.resize(1400, 800)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Corner resize variables
        self.dragging = False
        self.drag_position = None
        self.resizing = False
        self.resize_corner = None
        self.corner_size = 20
        self.hover_corner = None

        # Setup UI
        self.setup_ui()

        # Apply theme
        self._apply_theme()

        # Setup hotkeys
        #self._setup_hotkeys()

        # Enable mouse tracking
        self.setMouseTracking(True)

        if DEBUG_STANDALONE:
            print(f"{App_name} initialized")


    def setup_ui(self): #vers 2
        """Setup main UI layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Combined titlebar with all controls
        titlebar = self._create_titlebar()
        main_layout.addWidget(titlebar)

        # Content area with margin
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(5)

        # Main 3-panel splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel 1: Emulator platforms
        left_panel = self._create_left_panel()
        main_splitter.addWidget(left_panel)

        # Panel 2: Game list
        middle_panel = self._create_middle_panel()
        main_splitter.addWidget(middle_panel)

        # Panel 3: Display and controls
        right_panel = self._create_right_panel()
        main_splitter.addWidget(right_panel)

        # Set proportions (2:3:5)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 3)
        main_splitter.setStretchFactor(2, 5)

        content_layout.addWidget(main_splitter)

        # Status bar
        status_bar = self._create_status_bar()
        content_layout.addWidget(status_bar)

        main_layout.addWidget(content_widget)

    def _load_fonts_from_settings(self): #vers 1
        """Load font settings from AppSettings"""
        if not self.app_settings:
            return

        settings = self.app_settings

        self.default_font = QFont(
            settings.get('default_font_family', 'Segoe UI'),
            settings.get('default_font_size', 9)
        )

        self.title_font = QFont(
            settings.get('title_font_family', 'Adwaita Sans'),
            settings.get('title_font_size', 10)
        )

        self.panel_font = QFont(
            settings.get('panel_font_family', 'Adwaita Sans'),
            settings.get('panel_font_size', 9)
        )

        self.button_font = QFont(
            settings.get('button_font_family', 'Adwaita Sans'),
            settings.get('button_font_size', 9)
        )

        self.setFont(self.default_font)


    def _create_titlebar(self): #vers 5
        """Create combined titlebar with all controls in one line"""
        # Get accent color from theme if available

        self.titlebar = QFrame()
        self.titlebar.setFrameStyle(QFrame.Shape.StyledPanel)
        self.titlebar.setFixedHeight(45)
        #self.titlebar.setStyleSheet("background-color: bg_primary;")
        self.titlebar.setObjectName("titlebar")  # For drag detection

        self.layout = QHBoxLayout(self.titlebar)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # Settings button with icon
        self.properties_btn = QPushButton()
        self.properties_btn.setFont(self.button_font)
        # Bold font
        self.theme_font = QFont(self.button_font)
        self.theme_font.setBold(True)
        self.theme_font.setPointSize(14)
        self.properties_btn.setFont(self.theme_font)

        self.properties_btn.setFixedSize(40, 35)
        self.properties_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                color: color;
                border: 2px solid border;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: bg_primary;
                color: color;
            }
        """)

     # Settings button with icon
        self.settings_btn = QPushButton()
        self.settings_btn.setFont(self.button_font)
        self.settings_btn.setIcon(SVGIconFactory.settings_icon())
        self.settings_btn.setText("Settings")
        self.settings_btn.setIconSize(QSize(20, 20))
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.clicked.connect(self._open_mel_settings)
        self.settings_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.settings_btn.customContextMenuRequested.connect(self._show_settings_context_menu)
        self.layout.addWidget(self.settings_btn)

        self.layout.addStretch()

        # App title in center
        self.title_label = QLabel(App_name)
        self.title_label.setFont(self.title_font)
        #self.title_label.setStyleSheet("color: white;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.layout.addStretch()

        # Scan ROMs button with context menu
        self.scan_roms_btn = QPushButton()
        self.scan_roms_btn.setFont(self.button_font)
        self.scan_roms_btn.setIcon(SVGIconFactory.folder_icon())
        self.scan_roms_btn.setText("Scan ROMs")
        self.scan_roms_btn.setIconSize(QSize(20, 20))
        self.scan_roms_btn.setToolTip("Scan for ROM files")
        self.scan_roms_btn.clicked.connect(self._scan_roms)

        # Add context menu
        self.scan_roms_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.scan_roms_btn.customContextMenuRequested.connect(self._show_scan_roms_context_menu)
        self.layout.addWidget(self.scan_roms_btn)

        # Save config button
        self.save_btn = QPushButton()
        self.save_btn.setFont(self.button_font)
        self.save_btn.setIcon(SVGIconFactory.save_icon())
        self.save_btn.setText("Save Config")
        self.save_btn.setIconSize(QSize(20, 20))
        self.save_btn.setToolTip("Save Configuration")
        self.save_btn.clicked.connect(self._save_config)  # WIRE IT
        self.layout.addWidget(self.save_btn)

        # Controller button
        self.controller_btn = QPushButton()
        self.controller_btn.setFont(self.button_font)
        self.controller_btn.setIcon(SVGIconFactory.controller_icon())
        self.controller_btn.setText("Setup Controller")
        self.controller_btn.setIconSize(QSize(20, 20))
        self.controller_btn.setToolTip("Configure Controller")
        self.controller_btn.clicked.connect(self._setup_controller)  # WIRE IT
        self.layout.addWidget(self.controller_btn)

        self.layout.addSpacing(10)

        # Info button
        self.info_btn = QPushButton()
        self.info_btn.setFont(self.button_font)
        self.info_btn.setIcon(self._create_info_icon())
        self.info_btn.setFixedSize(35, 35)
        self.info_btn.setIconSize(QSize(20, 20))
        self.info_btn.setToolTip("Information")
        #self.info_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.info_btn.customContextMenuRequested.connect(self._show_about_dialog)
        self.layout.addWidget(self.info_btn)

        self.layout.addSpacing(10)

        self.properties_btn.setText("")
        self.properties_btn = QPushButton()
        self.properties_btn.setFont(self.button_font)
        #self.properties_btn.setIcon(self._create_info_icon())
        self.properties_btn.setIcon(self._create_properties_icon())
        self.properties_btn.setToolTip("Theme")
        self.properties_btn.setFixedSize(35, 35)
        self.properties_btn.clicked.connect(self._show_settings_dialog)
        self.properties_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.properties_btn.customContextMenuRequested.connect(self._show_settings_context_menu)
        self.layout.addWidget(self.properties_btn)

        # Minimize button
        self.minimize_btn = QPushButton()
        self.minimize_btn.setIcon(self._create_minimize_icon())
        self.minimize_btn.setFixedSize(35, 35)
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.minimize_btn.setToolTip("Minimize")
        self.layout.addWidget(self.minimize_btn)

        # Maximize button
        self.maximize_btn = QPushButton()
        self.maximize_btn.setIcon(self._create_maximize_icon())
        self.maximize_btn.setFixedSize(35, 35)
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        self.maximize_btn.setToolTip("Maximize")
        self.layout.addWidget(self.maximize_btn)

        # Close button
        self.close_btn = QPushButton()
        self.close_btn.setIcon(self._create_close_icon())
        self.close_btn.setFixedSize(35, 35)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setToolTip("Close")
        self.layout.addWidget(self.close_btn)

        titlebar = self.titlebar
        return titlebar


    def _create_left_panel(self): #vers 4
        """Create Panel 1: Emulator platforms list with icons"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header = QLabel("Emulator Platforms")
        header.setFont(self.panel_font)
        header.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(header)

        # Platform list with icon support
        # Check if icon_display_mode exists, use default if not
        display_mode = getattr(self, 'icon_display_mode', 'icons_and_text')
        self.platform_list = EmulatorListWidget(display_mode=display_mode)
        self.platform_list.platform_selected.connect(self._on_platform_selected)
        layout.addWidget(self.platform_list)

        # Scan for platforms dynamically
        discovered_platforms = self.platform_scanner.get_platforms()

        if discovered_platforms:
            # Pass icon_factory if available
            icon_factory = getattr(self, 'platform_icons', None)
            self.platform_list.populate_platforms(discovered_platforms, icon_factory)
            print(f"Loaded {len(discovered_platforms)} platform(s): {', '.join(discovered_platforms)}")
        else:
            # No platforms found - show helpful message
            self.platform_list.clear()
            placeholder = QListWidgetItem("No platforms found")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            self.platform_list.addItem(placeholder)

            info = QListWidgetItem("Place ROMs in /roms/[Platform]/")
            info.setFlags(Qt.ItemFlag.NoItemFlags)
            self.platform_list.addItem(info)

            print("No platforms found. Create directories in /roms/")

        # Add refresh button
        refresh_btn = QPushButton("Refresh Platforms")
        refresh_btn.clicked.connect(self._refresh_platforms)
        layout.addWidget(refresh_btn)

        if hasattr(self, '_saved_hidden_platforms'):
            self.platform_list.hidden_platforms = set(self._saved_hidden_platforms)

        return panel


    def _create_middle_panel(self): #vers 1
        """Create Panel 2: Game list for selected platform"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header = QLabel("Games")
        header.setFont(self.panel_font)
        header.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(header)

        # Game list
        self.game_list = GameListWidget()
        self.game_list.game_selected.connect(self._on_game_selected)
        layout.addWidget(self.game_list)

        return panel


    def _create_right_panel(self): #vers 1
        """Create Panel 3: Emulator display and controls"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(400)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        #layout = QHBoxLayout()

        # Header
        header = QLabel("Emulator Display")
        header.setFont(self.panel_font)
        header.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(header)

        # Display widget
        self.display_widget = EmulatorDisplayWidget()
        layout.addWidget(self.display_widget)

        return panel


    def _create_status_bar(self): #vers 1
        """Create bottom status bar"""
        status_bar = QFrame()
        status_bar.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        status_bar.setFixedHeight(22)

        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(15)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.platform_status = QLabel("Platform: None")
        layout.addWidget(self.platform_status)

        self.game_status = QLabel("Game: None")
        layout.addWidget(self.game_status)

        return status_bar


    def _refresh_platforms(self): #vers 3
        """Refresh platform list using current ROM path from settings"""
        # Get ROM path from MEL settings
        roms_dir = self.mel_settings.get_rom_path()

        # Update platform scanner with new path
        self.platform_scanner = PlatformScanner(roms_dir)

        # Scan for platforms - CORRECT METHOD NAME
        discovered_platforms = self.platform_scanner.scan_platforms()

        if discovered_platforms:
            platform_names = list(discovered_platforms.keys())
            # PASS icon_factory here
            self.platform_list.populate_platforms(platform_names, self.platform_icons)

            if hasattr(self, 'status_label'):
                self.status_label.setText(f"Found {len(platform_names)} platform(s)")
        else:
            self.platform_list.clear()
            placeholder = QListWidgetItem("No platforms found")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            self.platform_list.addItem(placeholder)

            if hasattr(self, 'status_label'):
                self.status_label.setText("No platforms found")


    def _set_icon_display_mode(self, mode): #vers 1
        """Set icon display mode for platform list

        Args:
            mode: "icons_only", "text_only", or "icons_and_text"
        """
        self.icon_display_mode = mode
        self.platform_list.set_display_mode(mode)

        if hasattr(self, 'status_label'):
            mode_names = {
                "icons_only": "Icons Only",
                "text_only": "Text Only",
                "icons_and_text": "Icons & Text"
            }
            self.status_label.setText(f"Display mode: {mode_names.get(mode, mode)}")


    def _toggle_icon_display_mode(self): #vers 1
        """Cycle through icon display modes"""
        modes = ["icons_and_text", "icons_only", "text_only"]
        current_index = modes.index(self.icon_display_mode)
        next_index = (current_index + 1) % len(modes)
        self._set_icon_display_mode(modes[next_index])


    def _on_game_selected(self, game): #vers 3
        """Handle game selection - find ROM path and show title artwork"""
        self.game_status.setText(f"Game: {game}")

        if not self.current_platform:
            return

        # Find ROM path for this game
        if self.current_platform in self.available_roms:
            roms = self.available_roms[self.current_platform]

            # Match game name to ROM file
            for rom_path in roms:
                if rom_path.stem == game:
                    self.current_rom_path = rom_path
                    if hasattr(self, 'status_label'):
                        self.status_label.setText(f"Ready to launch: {game}")
                    break
        
        # Load and display title artwork
        if hasattr(self, 'artwork_loader') and hasattr(self, 'display_widget'):
            title_artwork = self.artwork_loader.get_title_artwork(game, self.current_platform)
            self.display_widget.show_title_artwork(title_artwork)

    def _on_launch_game(self): #vers 1
        """Launch selected game with CoreLauncher"""
        if not self.current_platform or not self.current_rom_path:
            if hasattr(self, 'status_label'):
                self.status_label.setText("No game selected")
            return

        if not self.core_launcher:
            if hasattr(self, 'status_label'):
                self.status_label.setText("CoreLauncher not initialized")
            return

        # Update status
        game_name = self.current_rom_path.stem
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Launching {game_name}...")

        # Launch game
        success = self.core_launcher.launch_game(
            self.current_platform,
            self.current_rom_path
        )

        # Update status
        if hasattr(self, 'status_label'):
            if success:
                self.status_label.setText(f"Running: {game_name}")
            else:
                self.status_label.setText(f"Launch failed: {game_name}")


    def _on_stop_emulation(self): #vers 1
        """Stop current emulation"""
        if not self.core_launcher:
            return

        if self.core_launcher.is_running():
            success = self.core_launcher.stop_emulation()
            if hasattr(self, 'status_label'):
                if success:
                    self.status_label.setText("Emulation stopped")
                else:
                    self.status_label.setText("Failed to stop emulation")
        else:
            if hasattr(self, 'status_label'):
                self.status_label.setText("No emulation running")


    def _on_platform_selected(self, platform): #vers 4
        """Handle platform selection - scan for actual ROMs using discovered info"""
        self.current_platform = platform
        self.current_rom_path = None
        self.platform_status.setText(f"Platform: {platform}")

        # Get platform info from scanner
        platform_info = self.platform_scanner.get_platform_info(platform)

        if not platform_info:
            self.game_list.populate_games([], self.artwork_loader, platform)
            self.status_label.setText(f"Platform info not found: {platform}")
            return

        # Get ROM directory from discovered info
        roms_dir = Path(platform_info['path'])

        if not roms_dir.exists():
            self.game_list.populate_games([], self.artwork_loader, platform)
            self.status_label.setText(f"ROM directory not found: {roms_dir}")
            return

        # Get valid extensions from discovered info
        extensions = platform_info.get('extensions', [])

        # Find all ROM files
        rom_files = []
        for ext in extensions:
            rom_files.extend(list(roms_dir.glob(f"*{ext}")))

        # Store ROM paths
        self.available_roms[platform] = rom_files

        # Populate game list with filenames AND artwork
        game_names = [rom.stem for rom in rom_files]
        self.game_list.populate_games(game_names, self.artwork_loader, platform)

        rom_count = platform_info.get('rom_count', len(rom_files))
        self.status_label.setText(f"Found {rom_count} ROM(s) for {platform}")


    def _on_game_selected(self, game): #vers 2
        """Handle game selection - find ROM path and enable launch"""
        self.game_status.setText(f"Game: {game}")

        if not self.current_platform:
            return

        # Find ROM path for this game
        if self.current_platform in self.available_roms:
            roms = self.available_roms[self.current_platform]

            # Match game name to ROM file
            for rom_path in roms:
                if rom_path.stem == game:
                    self.current_rom_path = rom_path
                    self.status_label.setText(f"Ready to launch: {game}")
                    break


    def _on_launch_game(self): #vers 1
        """Launch selected game with CoreLauncher"""
        if not self.current_platform or not self.current_rom_path:
            if hasattr(self, 'status_label'):
                self.status_label.setText("No game selected")
            return

        if not self.core_launcher:
            if hasattr(self, 'status_label'):
                self.status_label.setText("CoreLauncher not initialized")
            return

        # Update status
        game_name = self.current_rom_path.stem
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Launching {game_name}...")

        # Launch game
        success = self.core_launcher.launch_game(
            self.current_platform,
            self.current_rom_path
        )

        # Update status
        if hasattr(self, 'status_label'):
            if success:
                self.status_label.setText(f"Running: {game_name}")
            else:
                self.status_label.setText(f"Launch failed: {game_name}")


    def _on_stop_emulation(self): #vers 1
        """Stop current emulation"""
        if not self.core_launcher:
            return

        if self.core_launcher.is_running():
            success = self.core_launcher.stop_emulation()
            if hasattr(self, 'status_label'):
                if success:
                    self.status_label.setText("Emulation stopped")
                else:
                    self.status_label.setText("Failed to stop emulation")
        else:
            if hasattr(self, 'status_label'):
                self.status_label.setText("No emulation running")

    def _apply_main_splitter_theme(self): #vers 6
        """Apply theme styling to main horizontal splitter"""
        theme_colors = self._get_theme_colors("default")

        # Extract variables FIRST
        bg_secondary = theme_colors.get('bg_secondary', '#f8f9fa')
        bg_primary = theme_colors.get('bg_primary', '#ffffff')
        bg_tertiary = theme_colors.get('bg_tertiary', '#e9ecef')

        self.main_splitter.setStyleSheet(f"""
            QSplitter::handle:horizontal {{
                background-color: {bg_secondary};
                border: 1px solid {bg_primary};
                border-left: 1px solid {bg_tertiary};
                width: 8px;
                margin: 2px 1px;
                border-radius: 3px;
            }}

            QSplitter::handle:horizontal:hover {{
                background-color: {bg_primary};
                border-color: {bg_tertiary};
            }}

            QSplitter::handle:horizontal:pressed {{
                background-color: {bg_tertiary};
            }}
        """)


    def _apply_vertical_splitter_theme(self): #vers 6
        """Apply theme styling to the vertical splitter"""
        theme_colors = self._get_theme_colors("default")

        # Extract variables FIRST
        bg_secondary = theme_colors.get('bg_secondary', '#f8f9fa')
        bg_tertiary = theme_colors.get('bg_tertiary', '#e9ecef')

        self.left_vertical_splitter.setStyleSheet(f"""
            QSplitter::handle:vertical {{
                background-color: {bg_secondary};
                border: 1px solid {bg_tertiary};
                height: 4px;
                margin: 1px 2px;
                border-radius: 2px;
            }}
            QSplitter::handle:vertical:hover {{
                background-color: {bg_tertiary};
            }}
        """)


    def _apply_log_theme_styling(self): #vers 7
        """Apply theme styling to the log widget"""
        theme_colors = self._get_theme_colors("default")

        # Extract variables FIRST
        panel_bg = theme_colors.get('panel_bg', '#f0f0f0')
        text_primary = theme_colors.get('text_primary', '#000000')
        border = theme_colors.get('border', '#dee2e6')

        self.log.setStyleSheet(f"""
            QTextEdit {{
                background-color: {panel_bg};
                color: {text_primary};
                border: 1px solid {border};
                border-radius: 3px;
                padding: 5px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
            }}
        """)


    def _apply_status_window_theme_styling(self): #vers 1
        """Apply theme styling to the status window"""
        theme_colors = self._get_theme_colors("default")
        if hasattr(self, 'status_window'):
             # Extract variables FIRST
            panel_bg = theme_colors.get('panel_bg', '#f0f0f0')
            text_primary = theme_colors.get('text_primary', '#000000')
            border = theme_colors.get('border', '#dee2e6')

            self.status_window.setStyleSheet(f"""
                QWidget {{
                    background-color: {panel_bg};
                    border: 1px solid {border};
                    border-radius: 3px;
                }}
                QLabel {{
                    color: #{text_primary};
                    font-weight: bold;
                }}
            """)


    def _apply_file_list_window_theme_styling(self): #vers 7
        """Apply theme styling to the file list window"""
        theme_colors = self._get_theme_colors("default")

        # Extract variables FIRST
        bg_secondary = theme_colors.get('bg_secondary', '#f8f9fa')
        border = theme_colors.get('border', '#dee2e6')
        button_normal = theme_colors.get('button_normal', '#e0e0e0')
        text_primary = theme_colors.get('text_primary', '#000000')
        bg_tertiary = theme_colors.get('bg_tertiary', '#e9ecef')

        if hasattr(self, 'tab_widget'):
            self.tab_widget.setStyleSheet(f"""
                QTabWidget::pane {{
                    background-color: {bg_secondary};
                    border: 1px solid {border};
                    border-radius: 3px;
                }}
                QTabBar::tab {{
                    background-color: {button_normal};
                    color: {text_primary};
                    padding: 5px 10px;
                    margin: 2px;
                    border-radius: 3px;
                }}
                QTabBar::tab:selected {{
                    background-color: {bg_tertiary};
                    border: 1px solid {border};
                }}
            """)


    def _get_theme_colors(self, theme_name): #vers 3
        """Get theme colors - properly connected to app_settings_system"""
        try:
            # Method 1: Use app_settings get_theme_colors() method
            if hasattr(self.main_window, 'app_settings') and hasattr(self.main_window.app_settings, 'get_theme_colors'):
                colors = self.main_window.app_settings.get_theme_colors()
                if colors:
                    print(f"Using app_settings theme colors: {len(colors)} colors loaded")
                    return colors

            # Method 2: Try direct theme access
            if hasattr(self.main_window, 'app_settings') and hasattr(self.main_window.app_settings, 'themes'):
                current_theme = self.main_window.app_settings.current_settings.get("theme", "IMG_Factory")
                theme_data = self.main_window.app_settings.themes.get(current_theme, {})
                colors = theme_data.get('colors', {})
                if colors:
                    print(f"Using direct theme access: {current_theme}")
                    return colors

        except Exception as e:
            print(f"Theme color lookup error: {e}")

        # Fallback with proper theme variables
        print("Using fallback theme colors")
        is_dark = self._is_dark_theme()
        if is_dark:
            return {
                'bg_primary': '#2b2b2b', 'bg_secondary': '#3c3c3c', 'bg_tertiary': '#4a4a4a',
                'panel_bg': '#333333', 'text_primary': '#ffffff', 'text_secondary': '#cccccc',
                'border': '#666666', 'accent_primary': '#FFECEE', 'button_normal': '#404040'
            }
        else:
            return {
                'bg_primary': '#ffffff', 'bg_secondary': '#f8f9fa', 'bg_tertiary': '#e9ecef',
                'panel_bg': '#f0f0f0', 'text_primary': '#000000', 'text_secondary': '#495057',
                'border': '#dee2e6', 'accent_primary': '#1976d2', 'button_normal': '#e0e0e0'
            }


    def _apply_file_list_window_theme_styling(self): #vers 7
        """Apply theme styling to the file list window"""
        theme_colors = self._get_theme_colors("default")

        # Extract variables FIRST
        bg_secondary = theme_colors.get('bg_secondary', '#f8f9fa')
        border = theme_colors.get('border', '#dee2e6')
        button_normal = theme_colors.get('button_normal', '#e0e0e0')
        text_primary = theme_colors.get('text_primary', '#000000')
        bg_tertiary = theme_colors.get('bg_tertiary', '#e9ecef')

        if hasattr(self, 'tab_widget'):
            self.tab_widget.setStyleSheet(f"""
                QTabWidget::pane {{
                    background-color: {bg_secondary};
                    border: 1px solid {border};
                    border-radius: 3px;
                }}
                QTabBar::tab {{
                    background-color: {button_normal};
                    color: {text_primary};
                    padding: 5px 10px;
                    margin: 2px;
                    border-radius: 3px;
                }}
                QTabBar::tab:selected {{
                    background-color: {bg_tertiary};
                    border: 1px solid {border};
                }}
            """)


    def apply_table_theme(self): #vers 1
        """Legacy method - Apply theme styling to table and related components"""
        # This method is called by main application for compatibility
        self.apply_all_window_themes()


    def _safe_log(self, message): #vers 1
        """Safe logging that won't cause circular dependency"""
        if hasattr(self.main_window, 'log_message') and hasattr(self.main_window, 'gui_layout'):
            self.main_window.log_message(message)
        else:
            print(f"GUI Layout: {message}")


    def log_message(self, message): #vers 1
        """Add message to activity log"""
        if self.log:
            from PyQt6.QtCore import QDateTime
            timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
            self.log.append(f"[{timestamp}] {message}")
            # Auto-scroll to bottom
            self.log.verticalScrollBar().setValue(
                self.log.verticalScrollBar().maximum()
            )


    def _is_dark_theme(self):
        """
        Returns True if the current theme name ends with _Dark.
        Works with hundreds of themes: Retro_Dark, Amiga_Dark, etc.
        Defaults to dark if theme settings are unavailable.
        """
        if APPSETTINGS_AVAILABLE and hasattr(self, "app_settings") and self.app_settings:
            theme_name = self.app_settings.current_settings.get("theme", "").lower()
            return theme_name.endswith("_dark")

        return True

    def _get_theme_colors(self, theme_name: str):
        """
        Returns a dictionary of theme colors and dynamic stylesheet sections
        for dark and light modes.
        """

        # Base colors from theme definitions (AppSettings)
        if APPSETTINGS_AVAILABLE and self.app_settings:
            theme_data = self.app_settings.themes.get(theme_name, {}).copy()
        else:
            theme_data = {}

        # Ensure missing keys have defaults
        theme_data.setdefault("bg_primary", "#1a1a1a")
        theme_data.setdefault("bg_secondary", "#2a2a2a")
        theme_data.setdefault("text_primary", "#ffffff")
        theme_data.setdefault("text_secondary", "#cccccc")
        theme_data.setdefault("accent", "#00d8ff")
        theme_data.setdefault("border", "#3a3a3a")
        theme_data.setdefault("panel_bg", "#2d2d2d")

        # Determine if this theme is dark or light
        is_dark = self._is_dark_theme()

        # Build tearoff button stylesheet
        if is_dark:
            button_style = f"""
                QPushButton {{
                    border: 1px solid {theme_data['border']};
                    border-radius: 1px;
                    background-color: {theme_data['bg_secondary']};
                    color: {theme_data['text_primary']};
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0px;
                    margin: 2px;
                }}
                QPushButton:hover {{
                    background-color: {theme_data['accent']};
                    border: 1px solid {theme_data['border']};
                    color: {theme_data['text_secondary']};
                }}
                QPushButton:pressed {{
                    background-color: {theme_data['bg_primary']};
                    border: 1px solid {theme_data['border']};
                    color: {theme_data['text_primary']};
                }}
            """
        else:
            button_style = f"""
                QPushButton {{
                    border: 1px solid {theme_data['border']};
                    border-radius: 1px;
                    background-color: {theme_data['bg_primary']};
                    color: {theme_data['text_primary']};
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0px;
                    margin: 2px;
                }}
                QPushButton:hover {{
                    background-color: {theme_data['accent']};
                    border: 1px solid {theme_data['border']};
                    color: {theme_data['text_secondary']};
                }}
                QPushButton:pressed {{
                    background-color: {theme_data['bg_secondary']};
                    border: 1px solid {theme_data['border']};
                    color: {theme_data['text_primary']};
                }}
            """

        # Inject button style into theme data
        theme_data["button_style"] = button_style

        return theme_data

    def _apply_theme(self): #vers 6
        """Apply theme to all GUI elements - extends AppSettings stylesheet"""

        if self.app_settings and APPSETTINGS_AVAILABLE:
            # Get base AppSettings stylesheet (already complete)
            base_stylesheet = self.app_settings.get_stylesheet()

            # Get theme colors for any additional MEL-specific overrides
            theme_colors = self._get_theme_colors("default")

            # Only add minimal overrides for widgets AppSettings might miss
            mel_overrides = f"""
                /* MEL-specific panel styling */
                QFrame[frameShape="4"] {{
                    background-color: {theme_colors.get('panel_bg', '#253447')};
                }}
            """

            # Apply: base stylesheet + minimal overrides
            self.setStyleSheet(base_stylesheet + mel_overrides)

            # Apply titlebar colors
            self._apply_titlebar_colors()
        #else:
            # Fallback theme when AppSettings not available
            #self._apply_log_theme_styling()
            #self._apply_vertical_splitter_theme()
            #self._apply_main_splitter_theme()
            #self._apply_status_window_theme_styling()
            #self._apply_file_list_window_theme_styling()


    def _apply_theme_not_found(self): #vers 5
        """Apply theme to all GUI elements - comprehensive styling"""
        # DEBUG - Check what's happening
        print(f"DEBUG: self.app_settings = {self.app_settings}")
        print(f"DEBUG: APPSETTINGS_AVAILABLE = {APPSETTINGS_AVAILABLE}")
        print(f"DEBUG: Condition result = {self.app_settings and APPSETTINGS_AVAILABLE}")

        if self.app_settings and APPSETTINGS_AVAILABLE:
            # Get base AppSettings stylesheet
            stylesheet = self.app_settings.get_stylesheet()

            # Get theme colors for MEL-specific widgets
            theme_colors = self._get_theme_colors("default")

            # Extract all colors from theme
            bg_primary = theme_colors.get('bg_primary', '#1f2f39')
            bg_secondary = theme_colors.get('bg_secondary', '#293f4d')
            bg_tertiary = theme_colors.get('bg_tertiary', '#18242d')
            panel_bg = theme_colors.get('panel_bg', '#253447')

            accent_primary = theme_colors.get('accent_primary', '#4f6f7A')
            accent_secondary = theme_colors.get('accent_secondary', '#657682')

            text_primary = theme_colors.get('text_primary', '#FFFFFF')
            text_secondary = theme_colors.get('text_secondary', '#E2FFE9')
            text_accent = theme_colors.get('text_accent', '#AFCFAF')

            button_normal = theme_colors.get('button_normal', '#2f3f49')
            button_hover = theme_colors.get('button_hover', '#0f0f09')
            button_pressed = theme_colors.get('button_pressed', '#5f6f79')
            button_text = theme_colors.get('button_text_color', '#FFFFFF')

            border = theme_colors.get('border', '#135379')

            splitter_bg = theme_colors.get('splitter_color_background', '#243845')
            splitter_shine = theme_colors.get('splitter_color_shine', '#3e525e')
            splitter_shadow = theme_colors.get('splitter_color_shadow', '#1f2f39')

            scrollbar_bg = theme_colors.get('scrollbar_background', '#1d2c36')
            scrollbar_handle = theme_colors.get('scrollbar_handle', '#114a6c')
            scrollbar_handle_hover = theme_colors.get('scrollbar_handle_hover', '#0f4260')
            scrollbar_handle_pressed = theme_colors.get('scrollbar_handle_pressed', '#0d3a54')
            scrollbar_border = theme_colors.get('scrollbar_border', '#135379')

            selection_bg = theme_colors.get('selection_background', '#4f6f7A')
            selection_text = theme_colors.get('selection_text', '#ffffff')

            # Comprehensive MEL stylesheet
            mel_stylesheet = f"""
                /* Main Window */
                QWidget {{
                    background-color: {bg_primary};
                    color: {text_primary};
                }}

                /* Frames and Panels */
                QFrame {{
                    background-color: {panel_bg};
                    border: 1px solid {border};
                    border-radius: 4px;
                }}

                QFrame[frameShape="4"] {{  /* StyledPanel */
                    background-color: {panel_bg};
                    border: 1px solid {border};
                }}

                /* Group Boxes */
                QGroupBox {{
                    background-color: {panel_bg};
                    border: 2px solid {border};
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 15px;
                    color: {text_primary};
                    font-weight: bold;
                }}

                QGroupBox::title {{
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 5px 10px;
                    color: {text_primary};
                    background-color: {bg_secondary};
                    border: 1px solid {border};
                    border-radius: 3px;
                }}

                /* Buttons */
                QPushButton {{
                    background-color: {button_normal};
                    border: 1px solid {border};
                    border-radius: 4px;
                    padding: 6px 12px;
                    color: {button_text};
                    min-height: 30px;
                }}

                QPushButton:hover {{
                    background-color: {button_hover};
                    border-color: {accent_primary};
                }}

                QPushButton:pressed {{
                    background-color: {button_pressed};
                    border-color: {accent_secondary};
                }}

                QPushButton:disabled {{
                    background-color: {bg_tertiary};
                    color: {text_secondary};
                    border-color: {border};
                }}

                /* Lists */
                QListWidget {{
                    background-color: {bg_primary};
                    alternate-background-color: {bg_secondary};
                    border: 1px solid {border};
                    border-radius: 4px;
                    color: {text_primary};
                    selection-background-color: {selection_bg};
                    selection-color: {selection_text};
                }}

                QListWidget::item {{
                    padding: 5px;
                    border-bottom: 1px solid {bg_tertiary};
                }}

                QListWidget::item:selected {{
                    background-color: {selection_bg};
                    color: {selection_text};
                }}

                QListWidget::item:hover {{
                    background-color: {accent_primary};
                }}

                /* Splitters */
                QSplitter::handle:horizontal {{
                    background-color: {splitter_bg};
                    border: 1px solid {splitter_shadow};
                    border-left: 1px solid {splitter_shine};
                    width: 8px;
                    margin: 2px;
                    border-radius: 3px;
                }}

                QSplitter::handle:horizontal:hover {{
                    background-color: {splitter_shine};
                }}

                QSplitter::handle:vertical {{
                    background-color: {splitter_bg};
                    border: 1px solid {splitter_shadow};
                    border-top: 1px solid {splitter_shine};
                    height: 8px;
                    margin: 2px;
                    border-radius: 3px;
                }}

                QSplitter::handle:vertical:hover {{
                    background-color: {splitter_shine};
                }}

                /* Scrollbars */
                QScrollBar:vertical {{
                    background-color: {scrollbar_bg};
                    width: 12px;
                    border: 1px solid {scrollbar_border};
                    border-radius: 3px;
                }}

                QScrollBar::handle:vertical {{
                    background-color: {scrollbar_handle};
                    min-height: 20px;
                    border-radius: 3px;
                    margin: 2px;
                }}

                QScrollBar::handle:vertical:hover {{
                    background-color: {scrollbar_handle_hover};
                }}

                QScrollBar::handle:vertical:pressed {{
                    background-color: {scrollbar_handle_pressed};
                }}

                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}

                QScrollBar:horizontal {{
                    background-color: {scrollbar_bg};
                    height: 12px;
                    border: 1px solid {scrollbar_border};
                    border-radius: 3px;
                }}

                QScrollBar::handle:horizontal {{
                    background-color: {scrollbar_handle};
                    min-width: 20px;
                    border-radius: 3px;
                    margin: 2px;
                }}

                QScrollBar::handle:horizontal:hover {{
                    background-color: {scrollbar_handle_hover};
                }}

                QScrollBar::handle:horizontal:pressed {{
                    background-color: {scrollbar_handle_pressed};
                }}

                QScrollBar::add-line:horizontal,
                QScrollBar::sub-line:horizontal {{
                    width: 0px;
                }}

                /* Labels */
                QLabel {{
                    color: {text_primary};
                    background-color: transparent;
                }}

                /* Line Edits */
                QLineEdit {{
                    background-color: {bg_secondary};
                    border: 1px solid {border};
                    border-radius: 3px;
                    padding: 5px;
                    color: {text_primary};
                    selection-background-color: {selection_bg};
                    selection-color: {selection_text};
                }}

                QLineEdit:focus {{
                    border: 2px solid {accent_primary};
                }}

                /* Checkboxes */
                QCheckBox {{
                    color: {text_primary};
                    spacing: 5px;
                }}

                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 1px solid {border};
                    border-radius: 3px;
                    background-color: {bg_secondary};
                }}

                QCheckBox::indicator:checked {{
                    background-color: {accent_primary};
                    border-color: {accent_secondary};
                }}

                QCheckBox::indicator:hover {{
                    border-color: {accent_primary};
                }}

                /* Radio Buttons */
                QRadioButton {{
                    color: {text_primary};
                    spacing: 5px;
                }}

                QRadioButton::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 1px solid {border};
                    border-radius: 9px;
                    background-color: {bg_secondary};
                }}

                QRadioButton::indicator:checked {{
                    background-color: {accent_primary};
                    border-color: {accent_secondary};
                }}

                QRadioButton::indicator:hover {{
                    border-color: {accent_primary};
                }}

                /* Status Bar */
                QStatusBar {{
                    background-color: {bg_tertiary};
                    color: {text_secondary};
                    border-top: 1px solid {border};
                }}

                /* Dialogs */
                QDialog {{
                    background-color: {bg_primary};
                    color: {text_primary};
                }}

                /* Tab Widget */
                QTabWidget::pane {{
                    background-color: {panel_bg};
                    border: 1px solid {border};
                    border-radius: 4px;
                }}

                QTabBar::tab {{
                    background-color: {button_normal};
                    color: {button_text};
                    padding: 8px 16px;
                    margin: 2px;
                    border: 1px solid {border};
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }}

                QTabBar::tab:selected {{
                    background-color: {panel_bg};
                    border-bottom: 2px solid {accent_primary};
                }}

                QTabBar::tab:hover {{
                    background-color: {button_hover};
                }}
            """

            # Apply combined stylesheet
            self.setStyleSheet(stylesheet + mel_stylesheet)

            # Apply titlebar colors
            self._apply_titlebar_colors()
        else:
            # Fallback theme when AppSettings not available
            self._apply_log_theme_styling()
            self._apply_vertical_splitter_theme()
            self._apply_main_splitter_theme()
            self._apply_status_window_theme_styling()
            self._apply_file_list_window_theme_styling()


    def _apply_titlebar_colors(self): #vers 4
        """Apply theme colors to titlebar elements - respects themed setting"""
        if not self.app_settings:
            return

        # Check if themed titlebar is enabled from MEL settings
        use_themed = self.mel_settings.settings.get('use_themed_titlebar', True)
        
        if not use_themed:
            # Hardcoded high-contrast colors for visibility
            text_color = '#FFFFFF'
            bg_color = '#2c3e50'
            accent_color = '#3498db'
        else:
            # Use theme colors
            theme_colors = self._get_theme_colors("default")
            text_color = theme_colors.get('text_primary', '#000000')
            bg_color = theme_colors.get('panel_bg', '#ffffff')
            accent_color = theme_colors.get('accent', '#1976d2')

        # Apply to title label
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    background-color: {bg_color};
                    font-weight: bold;
                    padding: 5px;
                }}
            """)

        # Apply to titlebar buttons - ensure BOTH icons and backgrounds are visible
        button_style = f"""
            QPushButton {{
                background-color: {accent_color};
                border: 1px solid {text_color};
                border-radius: 3px;
                color: {text_color};
                padding: 2px;
            }}
            QPushButton:hover {{
                background-color: {text_color};
                border-color: {accent_color};
            }}
        """

        if hasattr(self, 'minimize_btn'):
            self.minimize_btn.setStyleSheet(button_style)
        if hasattr(self, 'maximize_btn'):
            self.maximize_btn.setStyleSheet(button_style)
        if hasattr(self, 'close_btn'):
            self.close_btn.setStyleSheet(button_style)


    def _on_theme_changed(self, theme_name): #vers 1
        """Handle theme change from AppSettings
        
        Args:
            theme_name: Name of the newly selected theme
        """
        if DEBUG_STANDALONE:
            print(f"Theme changed to: {theme_name}")
        
        # Reapply theme to entire GUI
        self._apply_theme()
        
        # Update status
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Theme changed to: {theme_name}")


    def _open_mel_settings(self): #vers 2
        """Open MEL settings dialog for path configuration"""
        dialog = MELSettingsDialog(self.mel_settings, self)
        if dialog.exec():
            # Settings saved, refresh platforms with new ROM path
            self._refresh_platforms()
            
            # Reapply titlebar colors (in case themed setting changed)
            self._apply_titlebar_colors()

            # Update status
            if hasattr(self, 'status_label'):
                self.status_label.setText("Settings saved - platforms refreshed")

    def _open_settings_dialog(self): #vers 1
        """Open settings dialog and refresh on save"""
        dialog = SettingsDialog(self.mel_settings, self)
        if dialog.exec():
            # Refresh platform list with new ROM path
            self._scan_platforms()
            self.status_label.setText("Settings saved - platforms refreshed")


    def _setup_settings_button(self): #vers 1
        """Setup settings button in UI"""
        settings_btn = QPushButton("⚙ Settings")
        settings_btn.clicked.connect(self._open_settings_dialog)
        settings_btn.setMaximumWidth(120)
        return settings_btn


    def _show_settings_dialog(self): #vers 2
        """Show settings dialog with theme and preferences"""
        if not APPSETTINGS_AVAILABLE:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Settings", "AppSettings system not available")
            return

        dialog = SettingsDialog(self.app_settings, self)
        # Connect to _on_theme_changed to get theme name and status updates
        dialog.themeChanged.connect(self._on_theme_changed)

        if dialog.exec():
            # Settings were applied
            self.app_settings.save_settings()
            self._apply_theme()


    def _show_settings_context_menu(self, pos): #vers 1
        """Show context menu for Settings button"""
        from PyQt6.QtWidgets import QMenu

        menu = QMenu(self)

        # Move window action
        move_action = menu.addAction("Move Window")
        move_action.triggered.connect(self._enable_move_mode)

        # Maximize window action
        max_action = menu.addAction("Maximize Window")
        max_action.triggered.connect(self._toggle_maximize)

        # Minimize action
        min_action = menu.addAction("Minimize")
        min_action.triggered.connect(self.showMinimized)

        menu.addSeparator()

        # Upscale Native action
        upscale_action = menu.addAction("Upscale Native")
        upscale_action.setCheckable(True)
        upscale_action.setChecked(False)
        upscale_action.triggered.connect(self._toggle_upscale_native)

        # Shaders action
        shaders_action = menu.addAction("Shaders")
        shaders_action.triggered.connect(self._show_shaders_dialog)

        menu.addSeparator()

        # Icon display mode submenu # TODO icon only system is missing.
        display_menu = menu.addMenu("Platform Display")

        icons_text_action = display_menu.addAction("Icons & Text")
        icons_text_action.setCheckable(True)
        icons_text_action.setChecked(self.icon_display_mode == "icons_and_text")
        icons_text_action.triggered.connect(lambda: self._set_icon_display_mode("icons_and_text"))

        icons_only_action = display_menu.addAction("Icons Only")
        icons_only_action.setCheckable(True)
        icons_only_action.setChecked(self.icon_display_mode == "icons_only")
        icons_only_action.triggered.connect(lambda: self._set_icon_display_mode("icons_only"))

        text_only_action = display_menu.addAction("Text Only")
        text_only_action.setCheckable(True)
        text_only_action.setChecked(self.icon_display_mode == "text_only")
        text_only_action.triggered.connect(lambda: self._set_icon_display_mode("text_only"))

        # Show menu at button position
        menu.exec(self.settings_btn.mapToGlobal(pos))

    def _enable_move_mode(self): #vers 2
        """Enable move window mode using system move"""
        # Use Qt's system move which works on Windows, Linux, etc.
        if hasattr(self.windowHandle(), 'startSystemMove'):
            self.windowHandle().startSystemMove()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Move Window",
                "Drag the titlebar to move the window")

    def _toggle_upscale_native(self): #vers 1
        """Toggle upscale native resolution"""
        # Placeholder for upscale native functionality
        print("Upscale Native toggled")

    def _show_shaders_dialog(self): #vers 1
        """Show shaders configuration dialog"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Shaders",
            "Shader configuration coming soon!\n\nThis will allow you to:\n"
            "- Select shader presets\n"
            "- Configure CRT effects\n"
            "- Adjust visual filters")

    def _show_window_context_menu(self, pos): #vers 1
        """Show context menu for titlebar right-click"""
        from PyQt6.QtWidgets import QMenu


        # Move window action
        move_action = menu.addAction("Move Window")
        move_action.triggered.connect(self._enable_move_mode)

        # Maximize/Restore action
        if self.isMaximized():
            max_action = menu.addAction("Restore Window")
        else:
            max_action = menu.addAction("Maximize Window")
        max_action.triggered.connect(self._toggle_maximize)

        # Minimize action
        min_action = menu.addAction("Minimize")
        min_action.triggered.connect(self.showMinimized)

        menu.addSeparator()

        # Close action
        close_action = menu.addAction("Close")
        close_action.triggered.connect(self.close)

        # Show menu at global position
        menu.exec(self.mapToGlobal(pos))

    def _scan_roms(self): #vers 2
        """Scan for ROMs in configured directory with option to browse"""
        from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog
        from pathlib import Path

        # Get ROM path from MEL settings
        roms_dir = self.mel_settings.get_rom_path()

        # Check if path exists
        if not roms_dir.exists():
            response = QMessageBox.question(
                self,
                "ROM Directory Not Found",
                f"ROM directory not found:\n{roms_dir}\n\n"
                "Would you like to select a different directory?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if response == QMessageBox.StandardButton.Yes:
                # Let user browse for ROMs directory
                selected_dir = QFileDialog.getExistingDirectory(
                    self,
                    "Select ROM Directory",
                    str(Path.home()),
                    QFileDialog.Option.ShowDirsOnly
                )

                if selected_dir:
                    roms_dir = Path(selected_dir)
                    # Save this path to settings
                    self.mel_settings.set_rom_path(selected_dir)
                    self.status_label.setText(f"ROM path updated: {selected_dir}")
                else:
                    return
            else:
                return

        # Progress dialog
        progress = QProgressDialog("Scanning for ROMs...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setValue(10)

        # Update scanner with current path
        self.platform_scanner = PlatformScanner(roms_dir)
        progress.setValue(30)

        # Scan platforms
        discovered_platforms = self.platform_scanner.scan_platforms()
        progress.setValue(60)

        if discovered_platforms:
            # Count total ROMs
            total_roms = sum(info['rom_count'] for info in discovered_platforms.values())

            # Refresh platform list
            platform_names = list(discovered_platforms.keys())
            icon_factory = getattr(self, 'platform_icons', None)
            self.platform_list.populate_platforms(platform_names, icon_factory)

            progress.setValue(100)

            # Show results
            result = f"Found {total_roms} ROM(s) across {len(discovered_platforms)} platform(s):\n\n"
            for platform, info in sorted(discovered_platforms.items()):
                result += f"• {platform}: {info['rom_count']} ROM(s)\n"

            QMessageBox.information(self, "Scan Complete", result)
            self.status_label.setText(f"Found {len(discovered_platforms)} platform(s) with {total_roms} ROM(s)")
        else:
            progress.setValue(100)

            # Offer to browse for ROMs
            response = QMessageBox.question(
                self,
                "No ROMs Found",
                f"No ROM files found in:\n{roms_dir}\n\n"
                "Would you like to select a different directory?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if response == QMessageBox.StandardButton.Yes:
                # Recursively call to browse
                self._scan_roms()
            else:
                self.status_label.setText("No ROMs found")


    def _show_scan_roms_context_menu(self, position): #vers 1
        """Context menu for Scan ROMs button"""
        from PyQt6.QtWidgets import QMenu

        menu = QMenu(self)

        # Scan current path
        scan_action = menu.addAction("Scan Current ROM Path")
        scan_action.triggered.connect(self._scan_roms)

        # Browse and scan
        browse_action = menu.addAction("Browse for ROM Directory...")
        browse_action.triggered.connect(self._browse_and_scan)

        menu.addSeparator()

        # Open ROM folder
        open_action = menu.addAction("Open ROM Folder")
        open_action.triggered.connect(self._open_rom_folder)

        menu.exec(self.scan_roms_btn.mapToGlobal(position))


    def _browse_and_scan(self): #vers 1
        """Browse for ROM directory and scan"""
        from PyQt6.QtWidgets import QFileDialog
        from pathlib import Path

        selected_dir = QFileDialog.getExistingDirectory(
            self,
            "Select ROM Directory",
            str(self.mel_settings.get_rom_path()),
            QFileDialog.Option.ShowDirsOnly
        )

        if selected_dir:
            self.mel_settings.set_rom_path(selected_dir)
            self._scan_roms()


    def _open_rom_folder(self): #vers 1
        """Open ROM folder in file manager"""
        import subprocess
        import platform
        from pathlib import Path

        roms_dir = self.mel_settings.get_rom_path()

        if not roms_dir.exists():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Folder Not Found",
                f"ROM folder does not exist:\n{roms_dir}")
            return

        # Open in file manager
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.run(["explorer", str(roms_dir)])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(roms_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(roms_dir)])
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Could not open folder:\n{e}")


    def _save_config(self): #vers 1
        """Save current MEL configuration"""
        from PyQt6.QtWidgets import QMessageBox

        try:
            # Save MEL settings
            self.mel_settings.save_mel_settings()

            # Save hidden platforms list
            if hasattr(self.platform_list, 'hidden_platforms'):
                hidden_list = list(self.platform_list.hidden_platforms)
                self.mel_settings.settings['hidden_platforms'] = hidden_list
                self.mel_settings.save_mel_settings()

            # Save window geometry
            geometry = {
                'width': self.width(),
                'height': self.height(),
                'x': self.x(),
                'y': self.y()
            }
            self.mel_settings.settings['window_geometry'] = geometry
            self.mel_settings.save_mel_settings()

            QMessageBox.information(self, "Configuration Saved",
                "All settings have been saved successfully!")

            if hasattr(self, 'status_label'):
                self.status_label.setText("Configuration saved")

        except Exception as e:
            QMessageBox.critical(self, "Save Failed",
                f"Failed to save configuration:\n{e}")


    def _setup_controller(self): #vers 1
        """Setup and configure game controller"""
        from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget

        from apps.gui.controller_config_dialog import ControllerConfigDialog
        dialog = ControllerConfigDialog(self.gamepad_config, self)

        if not self.gamepad_config:
            QMessageBox.warning(self, "Controller Setup", "Gamepad config not initialized")
            return

        # Detect controllers
        controllers = self.gamepad_config.detect_controllers()

        if not controllers:
            QMessageBox.information(self, "No Controllers",
                "No controllers detected.\n\nPlease connect a controller and try again.")
            return

        if dialog.exec():
            if hasattr(self, 'status_label'):
                self.status_label.setText("Controller configuration updated")

        # Show controller selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Controller Setup")
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(300)

        layout = QVBoxLayout(dialog)

        info_label = QLabel(f"Detected {len(controllers)} controller(s):")
        layout.addWidget(info_label)

        # List controllers
        controller_list = QListWidget()
        for ctrl in controllers:
            item_text = f"{ctrl['name']} - {ctrl['buttons']} buttons, {ctrl['axes']} axes"
            controller_list.addItem(item_text)
        layout.addWidget(controller_list)

        # Test button
        test_btn = QPushButton("Test Selected Controller")
        test_btn.clicked.connect(lambda: self._test_selected_controller(controller_list.currentRow()))
        layout.addWidget(test_btn)

        # Save button
        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(lambda: self._save_controller_config(controller_list.currentRow()))
        layout.addWidget(save_btn)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()


    def _show_about_dialog(self): #vers 1
        """Show about/info dialog"""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QWidget, QGroupBox, QFormLayout, QSpinBox, QComboBox, QSlider, QLabel, QCheckBox, QFontComboBox)
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont

        dialog = QDialog(self)
        dialog.setWindowTitle("About Multi-Emulator Launcher")
        dialog.setMinimumSize(600, 500)

        layout = QVBoxLayout()

        # Title
        title = QLabel("Multi-Emulator Launcher 1.0")
        title_font = QFont(self.title_font)
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Author info
        author = QLabel("Created by X-Seti")
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author_font = QFont(self.panel_font)
        author_font.setPointSize(12)
        author.setFont(author_font)
        layout.addWidget(author)

        # Year
        year = QLabel("© 2025")
        year.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(year)

        layout.addSpacing(20)

        # Info browser
        info_browser = QTextBrowser()
        info_browser.setOpenExternalLinks(True)

        info_html = """
        <h3>About This Tool</h3>
        <p>Multi-Emulator Launcher (MEL) is a comprehensive emulation management system
        that provides a unified interface for launching games across multiple retro gaming platforms.</p>

        <h3>Key Features</h3>
        <ul>
            <li><b>Multi-Platform Support</b> - Support for 20+ gaming systems including:
                <ul>
                    <li>Commodore Amiga, Atari ST, Amstrad CPC</li>
                    <li>PlayStation 1/2/3, Nintendo 64, SNES, Genesis</li>
                    <li>Game Boy Advance, PSP, Dreamcast, and more</li>
                </ul>
            </li>
            <li><b>Dynamic Platform Discovery</b> - Automatically detects platforms from ROM directory structure</li>
            <li><b>Custom Emulator Launching</b> - Direct core launching without RetroArch dependency</li>
            <li><b>ROM Management</b> - Intelligent scanning, ZIP support, multi-disk game handling</li>
            <li><b>BIOS Management</b> - Organized BIOS file structure matching platforms</li>
            <li><b>Controller Support</b> - Full gamepad configuration with per-platform overrides</li>
            <li><b>Customizable Interface</b>
                <ul>
                    <li>Multiple display modes: Icons & Text, Icons Only, Text Only</li>
                    <li>Theme system with light/dark modes</li>
                    <li>SVG-based platform icons</li>
                    <li>Frameless window with custom controls</li>
                </ul>
            </li>
            <li><b>Platform Organization</b>
                <ul>
                    <li>Hide/show individual platforms</li>
                    <li>Right-click context menus</li>
                    <li>Platform-specific controller configuration</li>
                </ul>
            </li>
            <li><b>Configuration Management</b>
                <ul>
                    <li>Save/load complete settings</li>
                    <li>Persistent hidden platforms list</li>
                    <li>Window geometry memory</li>
                    <li>Icon display preferences</li>
                </ul>
            </li>
        </ul>

        <h3>Technical Details</h3>
        <ul>
            <li><b>Framework:</b> PyQt6</li>
            <li><b>Architecture:</b> Modular design with separated concerns</li>
            <li><b>Graphics:</b> SVG-based scalable icons</li>
            <li><b>Theme Engine:</b> App-System-Settings integration</li>
            <li><b>Platform:</b> Cross-platform (Linux, Windows, macOS)</li>
        </ul>

        <h3>Project Structure</h3>
        <ul>
            <li><b>core/</b> - Core functionality (launchers, downloaders, configs)</li>
            <li><b>gui/</b> - GUI components and dialogs</li>
            <li><b>methods/</b> - Shared utility methods</li>
            <li><b>components/</b> - Reusable UI components</li>
            <li><b>utils/</b> - Settings and theme management</li>
            <li><b>themes/</b> - Theme JSON files</li>
        </ul>

        <h3>GitHub Repository</h3>
        <p><a href="https://github.com/X-Seti/Multi-Emulator-Launcher">
        https://github.com/X-Seti/Multi-Emulator-Launcher</a></p>

        <h3>License</h3>
        <p>This project follows clean code conventions with strict organizational rules:</p>
        <ul>
            <li>File headers with "X-Seti - [Date] 2025" format</li>
            <li>Alphabetical method listings with version tracking</li>
            <li>No "Enhanced/Fixed/Improved" naming patterns</li>
            <li>Organized folder structure</li>
            <li>SVG icons only (no emojis)</li>
        </ul>

        <br>
        <p><i>Built with attention to detail and commitment to quality code.</i></p>
        """

        info_browser.setHtml(info_html)
        layout.addWidget(info_browser)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)

        # Apply theme to dialog
        if APPSETTINGS_AVAILABLE and self.app_settings:
            theme_name = self.app_settings.get_current_theme()
            if theme_name and theme_name in self.app_settings.themes:
                theme_data = self.app_settings.themes[theme_name]
                bg = theme_data.get('bg_secondary', '#2a2a2a')
                text = theme_data.get('text_primary', '#ffffff')
                accent = theme_data.get('accent', '#00d8ff')

                dialog.setStyleSheet(f"""
                    QDialog {{
                        background-color: {bg};
                        color: {text};
                    }}
                    QTextBrowser {{
                        background-color: {bg};
                        color: {text};
                        border: 1px solid {accent};
                    }}
                    a {{
                        color: {accent};
                    }}
                """)

        dialog.exec()


    def _test_selected_controller(self, controller_id): #vers 1
        """Test controller input"""
        from PyQt6.QtWidgets import QMessageBox

        if controller_id < 0:
            QMessageBox.warning(self, "Test Controller", "Please select a controller first")
            return

        QMessageBox.information(self, "Test Controller",
            f"Testing controller {controller_id}...\n\n"
            "Press buttons and move sticks.\n"
            "Check terminal for output.\n\n"
            "Test will run for 10 seconds...")

        if self.gamepad_config:
            inputs = self.gamepad_config.test_controller_input(controller_id, 10)

            if inputs:
                result = "Detected inputs:\n\n"
                for key, value in list(inputs.items())[:10]:  # Show first 10
                    result += f"{key}: {value}\n"
                QMessageBox.information(self, "Test Results", result)
            else:
                QMessageBox.information(self, "Test Results", "No inputs detected")


    def _save_controller_config(self, controller_id): #vers 1
        """Save controller configuration"""
        from PyQt6.QtWidgets import QMessageBox

        if controller_id < 0:
            QMessageBox.warning(self, "Save Config", "Please select a controller first")
            return

        # Get controller info
        ctrl_info = self.gamepad_config.get_controller_info(controller_id)

        if ctrl_info:
            # Save configuration
            success = self.gamepad_config.save_config(controller_id, ctrl_info)

            if success:
                QMessageBox.information(self, "Configuration Saved",
                    f"Controller {controller_id} configuration saved successfully!")
            else:
                QMessageBox.warning(self, "Save Failed", "Failed to save controller configuration")
        else:
            QMessageBox.warning(self, "Save Failed", "Controller information not available")

# - Settings Reusable
    def _show_workshop_settings(self): #vers 1 < moved from TXD workshop
        """Show complete workshop settings dialog"""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QWidget, QGroupBox, QFormLayout, QSpinBox, QComboBox, QSlider, QLabel, QCheckBox, QFontComboBox)
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont

        dialog = QDialog(self)
        dialog.setWindowTitle(App_name + " Settings")
        dialog.setMinimumWidth(650)
        dialog.setMinimumHeight(550)

        layout = QVBoxLayout(dialog)

        # Create tabs
        tabs = QTabWidget()

        # TAB 1: FONTS (FIRST TAB)

        fonts_tab = QWidget()
        fonts_layout = QVBoxLayout(fonts_tab)

        # Default Font
        default_font_group = QGroupBox("Default Font")
        default_font_layout = QHBoxLayout()

        default_font_combo = QFontComboBox()
        default_font_combo.setCurrentFont(self.font())
        default_font_layout.addWidget(default_font_combo)

        default_font_size = QSpinBox()
        default_font_size.setRange(8, 24)
        default_font_size.setValue(self.font().pointSize())
        default_font_size.setSuffix(" pt")
        default_font_size.setFixedWidth(80)
        default_font_layout.addWidget(default_font_size)

        default_font_group.setLayout(default_font_layout)
        fonts_layout.addWidget(default_font_group)

        # Title Font
        title_font_group = QGroupBox("Title Font")
        title_font_layout = QHBoxLayout()

        title_font_combo = QFontComboBox()
        if hasattr(self, 'title_font'):
            title_font_combo.setCurrentFont(self.title_font)
        else:
            title_font_combo.setCurrentFont(QFont("Arial", 14))
        title_font_layout.addWidget(title_font_combo)

        title_font_size = QSpinBox()
        title_font_size.setRange(10, 32)
        title_font_size.setValue(getattr(self, 'title_font', QFont("Arial", 14)).pointSize())
        title_font_size.setSuffix(" pt")
        title_font_size.setFixedWidth(80)
        title_font_layout.addWidget(title_font_size)

        title_font_group.setLayout(title_font_layout)
        fonts_layout.addWidget(title_font_group)

        # Panel Font
        panel_font_group = QGroupBox("Panel Headers Font")
        panel_font_layout = QHBoxLayout()

        panel_font_combo = QFontComboBox()
        if hasattr(self, 'panel_font'):
            panel_font_combo.setCurrentFont(self.panel_font)
        else:
            panel_font_combo.setCurrentFont(QFont("Arial", 10))
        panel_font_layout.addWidget(panel_font_combo)

        panel_font_size = QSpinBox()
        panel_font_size.setRange(8, 18)
        panel_font_size.setValue(getattr(self, 'panel_font', QFont("Arial", 10)).pointSize())
        panel_font_size.setSuffix(" pt")
        panel_font_size.setFixedWidth(80)
        panel_font_layout.addWidget(panel_font_size)

        panel_font_group.setLayout(panel_font_layout)
        fonts_layout.addWidget(panel_font_group)

        # Button Font
        button_font_group = QGroupBox("Button Font")
        button_font_layout = QHBoxLayout()

        button_font_combo = QFontComboBox()
        if hasattr(self, 'button_font'):
            button_font_combo.setCurrentFont(self.button_font)
        else:
            button_font_combo.setCurrentFont(QFont("Arial", 10))
        button_font_layout.addWidget(button_font_combo)

        button_font_size = QSpinBox()
        button_font_size.setRange(8, 16)
        button_font_size.setValue(getattr(self, 'button_font', QFont("Arial", 10)).pointSize())
        button_font_size.setSuffix(" pt")
        button_font_size.setFixedWidth(80)
        button_font_layout.addWidget(button_font_size)

        button_font_group.setLayout(button_font_layout)
        fonts_layout.addWidget(button_font_group)

        # Info Bar Font
        infobar_font_group = QGroupBox("Info Bar Font")
        infobar_font_layout = QHBoxLayout()

        infobar_font_combo = QFontComboBox()
        if hasattr(self, 'infobar_font'):
            infobar_font_combo.setCurrentFont(self.infobar_font)
        else:
            infobar_font_combo.setCurrentFont(QFont("Courier New", 9))
        infobar_font_layout.addWidget(infobar_font_combo)

        infobar_font_size = QSpinBox()
        infobar_font_size.setRange(7, 14)
        infobar_font_size.setValue(getattr(self, 'infobar_font', QFont("Courier New", 9)).pointSize())
        infobar_font_size.setSuffix(" pt")
        infobar_font_size.setFixedWidth(80)
        infobar_font_layout.addWidget(infobar_font_size)

        infobar_font_group.setLayout(infobar_font_layout)
        fonts_layout.addWidget(infobar_font_group)

        fonts_layout.addStretch()
        tabs.addTab(fonts_tab, "Fonts")

        # TAB 2: DISPLAY SETTINGS

        display_tab = QWidget()
        display_layout = QVBoxLayout(display_tab)

        # Button display mode
        button_group = QGroupBox("Button Display Mode")
        button_layout = QVBoxLayout()

        button_mode_combo = QComboBox()
        button_mode_combo.addItems(["Icons + Text", "Icons Only", "Text Only"])
        current_mode = getattr(self, 'button_display_mode', 'both')
        mode_map = {'both': 0, 'icons': 1, 'text': 2}
        button_mode_combo.setCurrentIndex(mode_map.get(current_mode, 0))
        button_layout.addWidget(button_mode_combo)

        button_hint = QLabel("Changes how toolbar buttons are displayed")
        button_hint.setStyleSheet("color: #888; font-style: italic;")
        button_layout.addWidget(button_hint)

        button_group.setLayout(button_layout)
        display_layout.addWidget(button_group)

        # Table display
        table_group = QGroupBox("Texture List Display")
        table_layout = QVBoxLayout()

        show_thumbnails = QCheckBox("Show texture thumbnails")
        show_thumbnails.setChecked(True)
        table_layout.addWidget(show_thumbnails)

        show_warnings = QCheckBox("Show warning icons for suspicious textures")
        show_warnings.setChecked(True)
        show_warnings.setToolTip("Shows icon if normal and alpha appear identical")
        table_layout.addWidget(show_warnings)

        table_group.setLayout(table_layout)
        display_layout.addWidget(table_group)

        display_layout.addStretch()
        tabs.addTab(display_tab, "Display")


        # TAB 3: placeholder
        # TAB 4: PERFORMANCE

        perf_tab = QWidget()
        perf_layout = QVBoxLayout(perf_tab)

        perf_group = QGroupBox("Performance Settings")
        perf_form = QFormLayout()

        preview_quality = QComboBox()
        preview_quality.addItems(["Low (Fast)", "Medium", "High (Slow)"])
        preview_quality.setCurrentIndex(1)
        perf_form.addRow("Preview Quality:", preview_quality)

        thumb_size = QSpinBox()
        thumb_size.setRange(32, 128)
        thumb_size.setValue(64)
        thumb_size.setSuffix(" px")
        perf_form.addRow("Thumbnail Size:", thumb_size)

        perf_group.setLayout(perf_form)
        perf_layout.addWidget(perf_group)

        # Caching
        cache_group = QGroupBox("Caching")
        cache_layout = QVBoxLayout()

        enable_cache = QCheckBox("Enable texture preview caching")
        enable_cache.setChecked(True)
        cache_layout.addWidget(enable_cache)

        cache_hint = QLabel("Caching improves performance but uses more memory")
        cache_hint.setStyleSheet("color: #888; font-style: italic;")
        cache_layout.addWidget(cache_hint)

        cache_group.setLayout(cache_layout)
        perf_layout.addWidget(cache_group)

        perf_layout.addStretch()
        tabs.addTab(perf_tab, "Performance")

        # TAB 5: PREVIEW SETTINGS (LAST TAB)

        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)

        # Zoom Settings
        zoom_group = QGroupBox("Zoom Settings")
        zoom_form = QFormLayout()

        zoom_spin = QSpinBox()
        zoom_spin.setRange(10, 500)
        zoom_spin.setValue(int(getattr(self, 'zoom_level', 1.0) * 100))
        zoom_spin.setSuffix("%")
        zoom_form.addRow("Default Zoom:", zoom_spin)

        zoom_group.setLayout(zoom_form)
        preview_layout.addWidget(zoom_group)

        # Background Settings
        bg_group = QGroupBox("Background Settings")
        bg_layout = QVBoxLayout()

        # Background mode
        bg_mode_layout = QFormLayout()
        bg_mode_combo = QComboBox()
        bg_mode_combo.addItems(["Solid Color", "Checkerboard", "Grid"])
        current_bg_mode = getattr(self, 'background_mode', 'solid')
        mode_idx = {"solid": 0, "checkerboard": 1, "checker": 1, "grid": 2}.get(current_bg_mode, 0)

        bg_mode_combo.setCurrentIndex(mode_idx)
        bg_mode_layout.addRow("Background Mode:", bg_mode_combo)
        bg_layout.addLayout(bg_mode_layout)

        bg_layout.addSpacing(10)

        # Checkerboard size
        cb_label = QLabel("Checkerboard Size:")
        bg_layout.addWidget(cb_label)

        cb_layout = QHBoxLayout()
        cb_slider = QSlider(Qt.Orientation.Horizontal)
        cb_slider.setMinimum(4)
        cb_slider.setMaximum(64)
        cb_slider.setValue(getattr(self, '_checkerboard_size', 16))
        cb_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        cb_slider.setTickInterval(8)
        cb_layout.addWidget(cb_slider)

        cb_spin = QSpinBox()
        cb_spin.setMinimum(4)
        cb_spin.setMaximum(64)
        cb_spin.setValue(getattr(self, '_checkerboard_size', 16))
        cb_spin.setSuffix(" px")
        cb_spin.setFixedWidth(80)
        cb_layout.addWidget(cb_spin)

        bg_layout.addLayout(cb_layout)

        # Connect checkerboard controls
        #cb_slider.valueChanged.connect(cb_spin.setValue)
        #cb_spin.valueChanged.connect(cb_slider.setValue)

        # Hint
        cb_hint = QLabel("Smaller = tighter pattern, larger = bigger squares")
        cb_hint.setStyleSheet("color: #888; font-style: italic; font-size: 10px;")
        bg_layout.addWidget(cb_hint)

        bg_group.setLayout(bg_layout)
        preview_layout.addWidget(bg_group)

        # Overlay Settings
        overlay_group = QGroupBox("Overlay View Settings")
        overlay_layout = QVBoxLayout()

        overlay_label = QLabel("Overlay Opacity (Normal over Alpha):")
        overlay_layout.addWidget(overlay_label)

        opacity_layout = QHBoxLayout()
        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setMinimum(0)
        opacity_slider.setMaximum(100)
        opacity_slider.setValue(getattr(self, '_overlay_opacity', 50))
        opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        opacity_slider.setTickInterval(10)
        opacity_layout.addWidget(opacity_slider)

        opacity_spin = QSpinBox()
        opacity_spin.setMinimum(0)
        opacity_spin.setMaximum(100)
        opacity_spin.setValue(getattr(self, '_overlay_opacity', 50))
        opacity_spin.setSuffix(" %")
        opacity_spin.setFixedWidth(80)
        opacity_layout.addWidget(opacity_spin)

        overlay_layout.addLayout(opacity_layout)

        # Connect opacity controls
        #opacity_slider.valueChanged.connect(opacity_spin.setValue)
        #opacity_spin.valueChanged.connect(opacity_slider.setValue)

        # Hint
        opacity_hint = QLabel("0")
        opacity_hint.setStyleSheet("color: #888; font-style: italic; font-size: 10px;")
        overlay_layout.addWidget(opacity_hint)

        overlay_group.setLayout(overlay_layout)
        preview_layout.addWidget(overlay_group)

        preview_layout.addStretch()
        tabs.addTab(preview_tab, "Preview")

        # Add tabs to dialog
        layout.addWidget(tabs)

        # BUTTONS

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        # Apply button
        apply_btn = QPushButton("Apply Settings")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #0078d4;
                color: white;
                padding: 10px 24px;
                font-weight: bold;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #1984d8;
            }
        """)

        def apply_settings():
            # FONTS
            self.setFont(QFont(default_font_combo.currentFont().family(),
                            default_font_size.value()))
            self.title_font = QFont(title_font_combo.currentFont().family(),
                                title_font_size.value())
            self.panel_font = QFont(panel_font_combo.currentFont().family(),
                                panel_font_size.value())
            self.button_font = QFont(button_font_combo.currentFont().family(),
                                    button_font_size.value())
            self.infobar_font = QFont(infobar_font_combo.currentFont().family(),
                                    infobar_font_size.value())

            # Apply fonts to UI
            self._apply_title_font()
            self._apply_panel_font()
            self._apply_button_font()
            self._apply_infobar_font()

            mode_map = {0: 'both', 1: 'icons', 2: 'text'}
            self.button_display_mode = mode_map[button_mode_combo.currentIndex()]

            # EXPORT
            self.default_export_format = format_combo.currentText()

            # PREVIEW
            self.zoom_level = zoom_spin.value() / 100.0

            bg_modes = ['solid', 'checkerboard', 'grid']
            self.background_mode = bg_modes[bg_mode_combo.currentIndex()]

            self._checkerboard_size = cb_spin.value()
            self._overlay_opacity = opacity_spin.value()

            # Update preview widget
            if hasattr(self, 'preview_widget'):
                if self.background_mode == 'checkerboard':
                    self.preview_widget.set_checkerboard_background()
                    self.preview_widget._checkerboard_size = self._checkerboard_size
                else:
                    self.preview_widget.set_background_color(self.preview_widget.bg_color)

            # Apply button display mode
            if hasattr(self, '_update_all_buttons'):
                self._update_all_buttons()

            # Refresh display

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Workshop settings updated successfully")

        apply_btn.clicked.connect(apply_settings)
        btn_layout.addWidget(apply_btn)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("padding: 10px 24px; font-size: 13px;")
        close_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        # Show dialog
        dialog.exec()


    def _apply_window_flags(self): #vers 1
        """Apply window flags based on settings"""
        # Save current geometry
        current_geometry = self.geometry()
        was_visible = self.isVisible()

        if self.use_system_titlebar:
            # Use system window with title bar
            self.setWindowFlags(
                Qt.WindowType.Window |
                Qt.WindowType.WindowMinimizeButtonHint |
                Qt.WindowType.WindowMaximizeButtonHint |
                Qt.WindowType.WindowCloseButtonHint
            )
        else:
            # Use custom frameless window
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Restore geometry and visibility
        self.setGeometry(current_geometry)

        if was_visible:
            self.show()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            mode = "System title bar" if self.use_system_titlebar else "Custom frameless"
            self.main_window.log_message(f"Window mode: {mode}")


    def _apply_always_on_top(self): #vers 1
        """Apply always on top window flag"""
        current_flags = self.windowFlags()

        if self.window_always_on_top:
            new_flags = current_flags | Qt.WindowType.WindowStaysOnTopHint
        else:
            new_flags = current_flags & ~Qt.WindowType.WindowStaysOnTopHint

        if new_flags != current_flags:
            # Save state
            current_geometry = self.geometry()
            was_visible = self.isVisible()

            self.setWindowFlags(new_flags)

            self.setGeometry(current_geometry)
            if was_visible:
                self.show()


    def _scan_available_locales(self): #vers 2
        """Scan locale folder and return list of available languages"""
        import os
        import configparser

        locales = []
        locale_path = os.path.join(os.path.dirname(__file__), 'locale')

        if not os.path.exists(locale_path):
            # Easter egg: Amiga Workbench 3.1 style error
            self._show_amiga_locale_error()
            # Return default English
            return [("English", "en", None)]

        try:
            for filename in os.listdir(locale_path):
                if filename.endswith('.lang'):
                    filepath = os.path.join(locale_path, filename)

                    try:
                        config = configparser.ConfigParser()
                        config.read(filepath, encoding='utf-8')

                        if 'Metadata' in config:
                            lang_name = config['Metadata'].get('LanguageName', 'Unknown')
                            lang_code = config['Metadata'].get('LanguageCode', 'unknown')
                            locales.append((lang_name, lang_code, filepath))

                    except Exception as e:
                        if self.main_window and hasattr(self.main_window, 'log_message'):
                            self.main_window.log_message(f"Failed to load locale {filename}: {e}")

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Locale scan error: {e}")

        locales.sort(key=lambda x: x[0])

        if not locales:
            locales = [("English", "en", None)]

        return locales


    def _show_amiga_locale_error(self): #vers 1
        """Show Amiga Workbench 3.1 style error dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont

        dialog = QDialog(self)
        dialog.setWindowTitle("Workbench Request")
        dialog.setFixedSize(450, 150)

        # Amiga Workbench styling
        dialog.setStyleSheet("""
            QDialog {
                background-color: #aaaaaa;
                border: 2px solid #ffffff;
            }
            QLabel {
                color: #000000;
                background-color: #aaaaaa;
            }
            QPushButton {
                background-color: #8899aa;
                color: #000000;
                border: 2px outset #ffffff;
                padding: 5px 15px;
                min-width: 80px;
            }
            QPushButton:pressed {
                border: 2px inset #555555;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Amiga Topaz font style
        amiga_font = QFont("Courier", 10, QFont.Weight.Normal)

        # Error message
        message = QLabel("Workbench 3.1 installer\n\nPlease insert Local disk in any drive")
        message.setFont(amiga_font)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)

        layout.addStretch()

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Retry and Cancel buttons (Amiga style)
        retry_btn = QPushButton("Retry")
        retry_btn.setFont(amiga_font)
        retry_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(retry_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(amiga_font)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        dialog.exec()


    def _update_dock_button_visibility(self): #vers 1
        """Show/hide dock and tearoff buttons based on docked state"""
        if hasattr(self, 'dock_btn'):
            # Hide D button when docked, show when standalone
            self.dock_btn.setVisible(not self.is_docked)

        if hasattr(self, 'tearoff_btn'):
            # T button only visible when docked and not in standalone mode
            self.tearoff_btn.setVisible(self.is_docked and not self.standalone_mode)


    def toggle_dock_mode(self): #vers 1
        """Toggle between docked and standalone mode"""
        if self.is_docked:
            self._undock_from_main()
        else:
            self._dock_to_main()

        self._update_dock_button_visibility()

    def _dock_to_main(self): #vers 7
        """Dock handled by overlay system in imgfactory"""
        if hasattr(self, 'is_overlay') and self.is_overlay:
            self.show()
            self.raise_()

    def _undock_from_main(self): #vers 3
        """Undock from overlay mode to standalone window"""
        if hasattr(self, 'is_overlay') and self.is_overlay:
            self.setWindowFlags(Qt.WindowType.Window)
            self.is_overlay = False
            self.overlay_table = None

        self.is_docked = False
        self._update_dock_button_visibility()

        self.show()

        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(App_name + " undocked to standalone")

    def _apply_button_mode(self, dialog): #vers 1
        """Apply button display mode"""
        mode_index = self.button_mode_combo.currentIndex()
        mode_map = {0: 'both', 1: 'icons', 2: 'text'}

        new_mode = mode_map[mode_index]

        if new_mode != self.button_display_mode:
            self.button_display_mode = new_mode
            self._update_all_buttons()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                mode_names = {0: 'Icons + Text', 1: 'Icons Only', 2: 'Text Only'}
                self.main_window.log_message(f"✨ Button style: {mode_names[mode_index]}")

        dialog.close()

# - Window functionality

    def _initialize_features(self): #vers 3
        """Initialize all features after UI setup"""
        try:
            self._apply_theme()
            self._update_status_indicators()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("All features initialized")

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Feature init error: {str(e)}")


    def _is_on_draggable_area(self, pos): #vers 2
        """Check if position is on draggable titlebar area - not on buttons"""
        if not hasattr(self, 'titlebar'):
            return False

        titlebar_rect = self.titlebar.geometry()
        if not titlebar_rect.contains(pos):
            return False

        # Convert position to titlebar coordinates
        titlebar_local_pos = self.titlebar.mapFrom(self, pos)

        # Check if clicking on any button - if so, not draggable
        for widget in self.titlebar.findChildren(QPushButton):
            if widget.geometry().contains(titlebar_local_pos):
                return False

        # Check title label - draggable
        for widget in self.titlebar.findChildren(QLabel):
            if widget.geometry().contains(titlebar_local_pos):
                return True

        return True  # On empty stretch area, draggable


    def _get_resize_corner(self, pos): #vers 1
        """Determine which corner is under mouse position"""
        size = self.corner_size
        w = self.width()
        h = self.height()

        if pos.x() < size and pos.y() < size:
            return "top-left"
        if pos.x() > w - size and pos.y() < size:
            return "top-right"
        if pos.x() < size and pos.y() > h - size:
            return "bottom-left"
        if pos.x() > w - size and pos.y() > h - size:
            return "bottom-right"

        return None


    def _handle_corner_resize(self, global_pos): #vers 1
        """Handle window resizing from corners"""
        if not self.resize_corner or not self.drag_position:
            return

        delta = global_pos - self.drag_position
        geometry = self.initial_geometry

        min_width = 800
        min_height = 600

        if self.resize_corner == "top-left":
            new_x = geometry.x() + delta.x()
            new_y = geometry.y() + delta.y()
            new_width = geometry.width() - delta.x()
            new_height = geometry.height() - delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(new_x, new_y, new_width, new_height)

        elif self.resize_corner == "top-right":
            new_y = geometry.y() + delta.y()
            new_width = geometry.width() + delta.x()
            new_height = geometry.height() - delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(geometry.x(), new_y, new_width, new_height)

        elif self.resize_corner == "bottom-left":
            new_x = geometry.x() + delta.x()
            new_width = geometry.width() - delta.x()
            new_height = geometry.height() + delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(new_x, geometry.y(), new_width, new_height)

        elif self.resize_corner == "bottom-right":
            new_width = geometry.width() + delta.x()
            new_height = geometry.height() + delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.resize(new_width, new_height)

    def _update_all_buttons(self): #vers 4
        """Update all buttons to match display mode"""
        buttons_to_update = [
            # Toolbar buttons
            ('open_btn', 'Open'),
            ('save_btn', 'Save'),
        ]

    def paintEvent(self, event): #vers 2
        """Paint corner resize triangles"""
        super().paintEvent(event)

        from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Colors
        normal_color = QColor(100, 100, 100, 150)
        hover_color = QColor(150, 150, 255, 200)

        w = self.width()
        h = self.height()
        size = self.corner_size

        # Define corner triangles
        corners = {
            'top-left': [(0, 0), (size, 0), (0, size)],
            'top-right': [(w, 0), (w-size, 0), (w, size)],
            'bottom-left': [(0, h), (size, h), (0, h-size)],
            'bottom-right': [(w, h), (w-size, h), (w, h-size)]
        }

        for corner_name, points in corners.items():
            # Choose color based on hover state
            if self.hover_corner == corner_name:
                painter.setBrush(QBrush(hover_color))
                painter.setPen(QPen(hover_color.darker(120), 1))
            else:
                painter.setBrush(QBrush(normal_color))
                painter.setPen(QPen(normal_color.darker(120), 1))

            # Draw triangle
            path = QPainterPath()
            path.moveTo(points[0][0], points[0][1])
            path.lineTo(points[1][0], points[1][1])
            path.lineTo(points[2][0], points[2][1])
            path.closeSubpath()

            painter.drawPath(path)

        painter.end()




    def _get_resize_corner(self, pos): #vers 2
        """Determine which corner is under mouse position"""
        size = self.corner_size
        w = self.width()
        h = self.height()

        if pos.x() < size and pos.y() < size:
            return "top-left"

        if pos.x() > w - size and pos.y() < size:
            return "top-right"

        if pos.x() < size and pos.y() > h - size:
            return "bottom-left"

        if pos.x() > w - size and pos.y() > h - size:
            return "bottom-right"

        return None


    def mousePressEvent(self, event): #vers 2
        """Handle mouse press for dragging and resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.resize_corner = self._get_resize_corner(event.pos())

            if self.resize_corner:
                self.resizing = True
                self.drag_position = event.globalPosition().toPoint()
                self.initial_geometry = self.geometry()
            else:
                # Check if clicking on toolbar for dragging
                if self._is_on_draggable_area(event.pos()):
                    self.dragging = True
                    self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

            event.accept()


    def mouseMoveEvent(self, event): #vers 2
        """Handle mouse move for dragging, resizing, and hover effects"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.resizing and self.resize_corner:
                self._handle_corner_resize(event.globalPosition().toPoint())
            elif self.dragging:
                self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            corner = self._get_resize_corner(event.pos())
            if corner != self.hover_corner:
                self.hover_corner = corner
                self.update()  # Trigger repaint for hover effect
            self._update_cursor(corner)


    def mouseReleaseEvent(self, event): #vers 2
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            self.resize_corner = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()


    def mouseDoubleClickEvent(self, event): #vers 1
        """Handle double-click on toolbar to maximize/restore"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self._is_on_draggable_area(event.pos()):
                self._toggle_maximize()
                event.accept()
            else:
                super().mouseDoubleClickEvent(event)


    def resizeEvent(self, event): #vers 1
        '''Keep resize grip in bottom-right corner'''
        super().resizeEvent(event)
        if hasattr(self, 'size_grip'):
            self.size_grip.move(self.width() - 16, self.height() - 16)


    def _handle_corner_resize(self, global_pos): #vers 2
        """Handle window resizing from corners"""
        if not self.resize_corner or not self.drag_position:
            return

        delta = global_pos - self.drag_position
        geometry = self.initial_geometry

        min_width = 800
        min_height = 600

        # Calculate new geometry based on corner
        if self.resize_corner == "top-left":
            new_x = geometry.x() + delta.x()
            new_y = geometry.y() + delta.y()
            new_width = geometry.width() - delta.x()
            new_height = geometry.height() - delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(new_x, new_y, new_width, new_height)

        elif self.resize_corner == "top-right":
            new_y = geometry.y() + delta.y()
            new_width = geometry.width() + delta.x()
            new_height = geometry.height() - delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(geometry.x(), new_y, new_width, new_height)

        elif self.resize_corner == "bottom-left":
            new_x = geometry.x() + delta.x()
            new_width = geometry.width() - delta.x()
            new_height = geometry.height() + delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(new_x, geometry.y(), new_width, new_height)

        elif self.resize_corner == "bottom-right":
            new_width = geometry.width() + delta.x()
            new_height = geometry.height() + delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.resize(new_width, new_height)


    def _get_resize_direction(self, pos): #vers 1
        """Determine resize direction based on mouse position"""
        rect = self.rect()
        margin = self.resize_margin

        left = pos.x() < margin
        right = pos.x() > rect.width() - margin
        top = pos.y() < margin
        bottom = pos.y() > rect.height() - margin

        if left and top:
            return "top-left"
        elif right and top:
            return "top-right"
        elif left and bottom:
            return "bottom-left"
        elif right and bottom:
            return "bottom-right"
        elif left:
            return "left"
        elif right:
            return "right"
        elif top:
            return "top"
        elif bottom:
            return "bottom"

        return None


    def _update_cursor(self, direction): #vers 1
        """Update cursor based on resize direction"""
        if direction == "top" or direction == "bottom":
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif direction == "left" or direction == "right":
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif direction == "top-left" or direction == "bottom-right":
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif direction == "top-right" or direction == "bottom-left":
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)


    def _handle_resize(self, global_pos): #vers 1
        """Handle window resizing"""
        if not self.resize_direction or not self.drag_position:
            return

        delta = global_pos - self.drag_position
        geometry = self.frameGeometry()

        min_width = 800
        min_height = 600

        # Handle horizontal resizing
        if "left" in self.resize_direction:
            new_width = geometry.width() - delta.x()
            if new_width >= min_width:
                geometry.setLeft(geometry.left() + delta.x())
        elif "right" in self.resize_direction:
            new_width = geometry.width() + delta.x()
            if new_width >= min_width:
                geometry.setRight(geometry.right() + delta.x())

        # Handle vertical resizing
        if "top" in self.resize_direction:
            new_height = geometry.height() - delta.y()
            if new_height >= min_height:
                geometry.setTop(geometry.top() + delta.y())
        elif "bottom" in self.resize_direction:
            new_height = geometry.height() + delta.y()
            if new_height >= min_height:
                geometry.setBottom(geometry.bottom() + delta.y())

        self.setGeometry(geometry)
        self.drag_position = global_pos


    def _toggle_maximize(self): #vers 1
        """Toggle window maximize state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _set_checkerboard_bg(self): #vers 1
        """Set checkerboard background"""
        # Create checkerboard pattern
        self.preview_widget.setStyleSheet("""
            border: 1px solid #3a3a3a;
            background-image:
                linear-gradient(45deg, #333 25%, transparent 25%),
                linear-gradient(-45deg, #333 25%, transparent 25%),
                linear-gradient(45deg, transparent 75%, #333 75%),
                linear-gradient(-45deg, transparent 75%, #333 75%);
            background-size: 20px 20px;
            background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
        """)

    def closeEvent(self, event): #vers 1
        """Handle close event"""
        self.window_closed.emit()
        event.accept()

# - Create

    def _create_properties_icon(self): #vers 1
        """Create settings (gear) icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = b'''<svg viewBox="0 0 24 24">
            <!-- Gear/cog icon for management -->
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''

        return self._svg_to_icon(svg_data, size=20)
        #return QIcon(pixmap)

    def _create_settings_icon(self): #vers 1
        """Create settings (gear) icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <circle cx="8" cy="8" r="3" fill="none" stroke="333333" stroke-width="1.5"/>
            <circle cx="8" cy="2" r="1" fill="#ffffff"/>
            <circle cx="8" cy="14" r="1" fill="#000000"/>
            <circle cx="2" cy="8" r="1" fill="#555555"/>
            <circle cx="14" cy="8" r="1" fill="#111111"/>
        </svg>'''

        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_launch_icon(self): #vers 1
        """Create launch (play) icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <path d="M 4 2 L 4 14 L 12 8 Z" fill="#ffffff"/>
        </svg>'''

        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_stop_icon(self): #vers 1
        """Create stop (square) icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <rect x="4" y="4" width="8" height="8" fill="#ffffff"/>
        </svg>'''

        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_controller_icon(self): #vers 1
        """Create controller (gamepad) icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <path d="M 3 6 Q 2 6 2 7 L 2 10 Q 2 11 3 11 L 5 11 Q 6 11 6 10 L 6 7 Q 6 6 5 6 Z" fill="none" stroke="#ffffff" stroke-width="1.5"/>
            <path d="M 11 6 Q 10 6 10 7 L 10 10 Q 10 11 11 11 L 13 11 Q 14 11 14 10 L 14 7 Q 14 6 13 6 Z" fill="none" stroke="#ffffff" stroke-width="1.5"/>
            <path d="M 6 8 L 10 8" stroke="#ffffff" stroke-width="1.5"/>
        </svg>'''

        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_close_icon(self): #vers 1
        """Create close (X) icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <path d="M 3 3 L 13 13 M 13 3 L 3 13" stroke="#ffffff" stroke-width="2"/>
        </svg>'''

        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_minimize_icon(self): #vers 1
        """Create minimize icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <path d="M 3 8 L 13 8" stroke="#ffffff" stroke-width="2"/>
        </svg>'''

        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_maximize_icon(self): #vers 1
        """Create maximize icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <rect x="3" y="3" width="10" height="10" fill="none" stroke="#ffffff" stroke-width="1.5"/>
        </svg>'''

        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_volume_up_icon(self): #vers 1
        """Create volume up icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <path d="M 2 6 L 5 6 L 8 3 L 8 13 L 5 10 L 2 10 Z" fill="#ffffff"/>
            <path d="M 10 5 Q 12 8 10 11" stroke="#ffffff" stroke-width="1.5" fill="none"/>
            <path d="M 12 4 Q 15 8 12 12" stroke="#ffffff" stroke-width="1.5" fill="none"/>
        </svg>'''

        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_volume_down_icon(self): #vers 1
        """Create volume down icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <path d="M 2 6 L 5 6 L 8 3 L 8 13 L 5 10 L 2 10 Z" fill="#ffffff"/>
            <path d="M 10 6 Q 12 8 10 10" stroke="#ffffff" stroke-width="1.5" fill="none"/>
        </svg>'''

        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_screenshot_icon(self): #vers 1
        """Create screenshot (camera) icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <rect x="2" y="4" width="12" height="9" rx="1" fill="none" stroke="#ffffff" stroke-width="1.5"/>
            <circle cx="8" cy="8" r="2" fill="none" stroke="#ffffff" stroke-width="1.5"/>
            <rect x="6" y="2" width="4" height="2" fill="#ffffff"/>
        </svg>'''

        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_record_icon(self): #vers 1
        """Create record (circle) icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <circle cx="8" cy="8" r="5" fill="#ff0000"/>
        </svg>'''

        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_save_icon(self): #vers 1
        """Create save (floppy disk) icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <rect x="2" y="2" width="12" height="12" fill="none" stroke="#ffffff" stroke-width="1.5"/>
            <rect x="4" y="2" width="8" height="4" fill="none" stroke="#ffffff" stroke-width="1.5"/>
            <rect x="5" y="8" width="6" height="6" fill="#ffffff"/>
        </svg>'''

        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_file_icon(self): #vers 1
        """Create file icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <path d="M 3 1 L 10 1 L 13 4 L 13 15 L 3 15 Z" fill="none" stroke="#ffffff" stroke-width="1.5"/>
            <path d="M 10 1 L 10 4 L 13 4" fill="none" stroke="#ffffff" stroke-width="1.5"/>
        </svg>'''

        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_folder_icon(self): #vers 1
        """Create folder icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <path d="M 2 3 L 7 3 L 8 5 L 14 5 L 14 13 L 2 13 Z" fill="none" stroke="#ffffff" stroke-width="1.5"/>
        </svg>'''

        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_info_icon(self): #vers 1
        """Create info (i) icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter

        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <circle cx="8" cy="8" r="6" fill="none" stroke="#ffffff" stroke-width="1.5"/>
            <circle cx="8" cy="5" r="0.5" fill="#ffffff"/>
            <path d="M 8 7 L 8 11" stroke="#ffffff" stroke-width="1.5"/>
        </svg>'''

        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _svg_to_icon(self, svg_data, size=24): #vers 2
        """Convert SVG data to QIcon with theme color support"""
        from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import QByteArray
        from PyQt6.QtGui import QPixmap, QPainter

        try:
            # Get current text color from palette
            text_color = self.palette().color(self.foregroundRole())

            # Replace currentColor with actual color
            svg_str = svg_data.decode('utf-8')
            svg_str = svg_str.replace('currentColor', text_color.name())
            svg_data = svg_str.encode('utf-8')

            renderer = QSvgRenderer(QByteArray(svg_data))
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            return QIcon(pixmap)
        except:
            # Fallback to no icon if SVG fails
            return QIcon()

# Standalone execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmuLauncherGUI()
    window.show()
    sys.exit(app.exec())
