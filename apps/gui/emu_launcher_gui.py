#!/usr/bin/env python3
#this belongs in apps/gui/emu_launcher_gui.py - Version: 1
# X-Seti - November19 2025 - Multi-Emulator Launcher - Main GUI

"""
Multi-Emulator Launcher GUI
Main window with 3-panel layout for emulator management
"""

import os
import sys
from pathlib import Path
from typing import Optional

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QListWidget, QListWidgetItem, QLabel, QPushButton, QFrame, 
    QTabWidget, QGroupBox, QFormLayout, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import QFont, QIcon, QColor, QCursor, QPainter, QPen

# Import AppSettings
try:
    from apps.utils.app_settings_system import AppSettings, SettingsDialog
    APPSETTINGS_AVAILABLE = True
except ImportError:
    APPSETTINGS_AVAILABLE = False
    print("Warning: AppSettings not available")

##Methods list -
# __init__
# mouseDoubleClickEvent
# mouseMoveEvent
# mousePressEvent
# mouseReleaseEvent
# paintEvent
# resizeEvent
# setup_ui
# _apply_theme
# _create_left_panel
# _create_middle_panel
# _create_right_panel
# _create_status_bar
# _create_titlebar
# _enable_move_mode
# _get_resize_corner
# _handle_corner_resize
# _initialize_features
# _is_on_draggable_area
# _on_game_selected
# _on_platform_selected
# _on_theme_changed
# _show_settings_context_menu
# _show_settings_dialog
# _show_shaders_dialog
# _show_window_context_menu
# _toggle_maximize
# _toggle_upscale_native
# _update_cursor

##SVG Icon Methods -
# _create_close_icon
# _create_controller_icon
# _create_file_icon
# _create_folder_icon
# _create_info_icon
# _create_launch_icon
# _create_maximize_icon
# _create_minimize_icon
# _create_record_icon
# _create_save_icon
# _create_screenshot_icon
# _create_settings_icon
# _create_stop_icon
# _create_volume_down_icon
# _create_volume_up_icon

# App name
App_name = "Multi-Emulator Launcher"
DEBUG_STANDALONE = True


class EmulatorListWidget(QListWidget): #vers 1
    """Panel 1: List of emulator platforms"""
    
    platform_selected = pyqtSignal(str)
    
    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.currentRowChanged.connect(self.on_selection_changed)
        
    def populate_platforms(self, platforms): #vers 1
        """Populate with platform names"""
        self.clear()
        for platform in platforms:
            item = QListWidgetItem(platform)
            self.addItem(item)
            
    def on_selection_changed(self, row): #vers 1
        """Handle platform selection"""
        if row >= 0:
            platform = self.item(row).text()
            self.platform_selected.emit(platform)


class GameListWidget(QListWidget): #vers 1
    """Panel 2: List of games for selected platform"""
    
    game_selected = pyqtSignal(str)
    
    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.currentRowChanged.connect(self.on_selection_changed)
        
    def populate_games(self, games): #vers 1
        """Populate with game names"""
        self.clear()
        for game in games:
            item = QListWidgetItem(game)
            self.addItem(item)
            
    def on_selection_changed(self, row): #vers 1
        """Handle game selection"""
        if row >= 0:
            game = self.item(row).text()
            self.game_selected.emit(game)


class EmulatorDisplayWidget(QWidget): #vers 2
    """Panel 3: Emulator display with vertical icon controls and bottom buttons"""
    
    def __init__(self, parent=None): #vers 2
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self): #vers 2
        """Setup display panel with horizontal layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # Top: Display area + icon controls (horizontal)
        top_layout = QHBoxLayout()
        
        # Display area (center - takes most space)
        self.display_area = QFrame()
        self.display_area.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        self.display_area.setMinimumHeight(400)
        self.display_area.setStyleSheet("background-color: #1a1a1a;")
        
        display_layout = QVBoxLayout(self.display_area)
        placeholder = QLabel("Emulator Display")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #666; font-size: 18px;")
        display_layout.addWidget(placeholder)
        
        top_layout.addWidget(self.display_area, stretch=1)
        
        # Icon controls (right side - vertical)
        icon_controls = self._create_icon_controls()
        top_layout.addWidget(icon_controls, stretch=0)
        
        main_layout.addLayout(top_layout)
        
        # Bottom: Control buttons
        controls = self._create_control_buttons()
        main_layout.addWidget(controls)
        
    def _create_icon_controls(self): #vers 2
        """Create vertical icon control buttons on right side"""
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        controls_frame.setMaximumWidth(50)
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(5, 5, 5, 5)
        controls_layout.setSpacing(5)
        
        # Volume Up
        vol_up_btn = QPushButton()
        vol_up_btn.setIcon(self._create_volume_up_icon())
        vol_up_btn.setIconSize(QSize(20, 20))
        vol_up_btn.setFixedSize(40, 40)
        vol_up_btn.setToolTip("Volume Up")
        controls_layout.addWidget(vol_up_btn)
        
        # Volume Down
        vol_down_btn = QPushButton()
        vol_down_btn.setIcon(self._create_volume_down_icon())
        vol_down_btn.setIconSize(QSize(20, 20))
        vol_down_btn.setFixedSize(40, 40)
        vol_down_btn.setToolTip("Volume Down")
        controls_layout.addWidget(vol_down_btn)
        
        controls_layout.addSpacing(10)
        
        # Screenshot
        screenshot_btn = QPushButton()
        screenshot_btn.setIcon(self._create_screenshot_icon())
        screenshot_btn.setIconSize(QSize(20, 20))
        screenshot_btn.setFixedSize(40, 40)
        screenshot_btn.setToolTip("Screenshot")
        controls_layout.addWidget(screenshot_btn)
        
        # Record
        record_btn = QPushButton()
        record_btn.setIcon(self._create_record_icon())
        record_btn.setIconSize(QSize(20, 20))
        record_btn.setFixedSize(40, 40)
        record_btn.setToolTip("Record")
        controls_layout.addWidget(record_btn)
        
        controls_layout.addStretch()
        
        return controls_frame
        
    def _create_control_buttons(self): #vers 1
        """Create control buttons at bottom"""
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(5, 5, 5, 5)
        
        self.launch_btn = QPushButton("Launch Game")
        self.launch_btn.setEnabled(False)
        controls_layout.addWidget(self.launch_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setEnabled(False)
        controls_layout.addWidget(self.pause_btn)
        
        controls_layout.addStretch()
        
        self.fullscreen_btn = QPushButton("Fullscreen")
        self.fullscreen_btn.setEnabled(False)
        controls_layout.addWidget(self.fullscreen_btn)
        
        self.windowed_btn = QPushButton("Windowed")
        self.windowed_btn.setEnabled(False)
        controls_layout.addWidget(self.windowed_btn)
        
        return controls_frame
        
    def _create_volume_up_icon(self): #vers 1
        """Create volume up icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter
        
        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <path d="M 2 6 L 5 6 L 8 3 L 8 13 L 5 10 L 2 10 Z" fill="#ffffff"/>
            <path d="M 10 5 Q 12 8 10 11" stroke="#ffffff" stroke-width="1.5" fill="none"/>
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
            <path d="M 10 8 L 12 8" stroke="#ffffff" stroke-width="1.5"/>
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
            <rect x="2" y="5" width="12" height="9" rx="1" fill="none" stroke="#ffffff" stroke-width="1.5"/>
            <circle cx="8" cy="9" r="2" fill="none" stroke="#ffffff" stroke-width="1.5"/>
            <path d="M 5 5 L 6 3 L 10 3 L 11 5" fill="none" stroke="#ffffff" stroke-width="1.5"/>
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


class EmuLauncherGUI(QWidget): #vers 1
    """Main GUI window - Multi-Emulator Launcher"""
    
    window_closed = pyqtSignal()
    
    def __init__(self, parent=None, main_window=None, core_downloader=None, gamepad_config=None): #vers 3
        """Initialize GUI with AppSettings integration and core systems"""
        if DEBUG_STANDALONE:
            print(f"{App_name} Initializing...")
            
        super().__init__(parent)
        
        self.main_window = main_window
        self.standalone_mode = (main_window is None)
        
        # Store core systems
        self.core_downloader = core_downloader
        self.gamepad_config = gamepad_config
        
        # Initialize AppSettings
        if APPSETTINGS_AVAILABLE:
            self.app_settings = AppSettings()
        else:
            self.app_settings = None
        
        # Set default fonts
        default_font = QFont("Fira Sans Condensed", 14)
        self.setFont(default_font)
        self.title_font = QFont("Arial", 14)
        self.panel_font = QFont("Arial", 10)
        self.button_font = QFont("Arial", 10)
        
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
        
    def _create_titlebar(self): #vers 3
        """Create combined titlebar with all controls in one line"""
        titlebar = QFrame()
        titlebar.setFrameStyle(QFrame.Shape.StyledPanel)
        titlebar.setFixedHeight(45)
        titlebar.setStyleSheet("background-color: #2d2d2d;")
        titlebar.setObjectName("titlebar")  # For drag detection
        
        layout = QHBoxLayout(titlebar)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Settings button with icon
        self.settings_btn = QPushButton()
        self.settings_btn.setFont(self.button_font)
        self.settings_btn.setIcon(self._create_settings_icon())
        self.settings_btn.setText("Settings")
        self.settings_btn.setIconSize(QSize(20, 20))
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.clicked.connect(self._show_settings_dialog)
        self.settings_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.settings_btn.customContextMenuRequested.connect(self._show_settings_context_menu)
        layout.addWidget(self.settings_btn)
        
        layout.addStretch()
        
        # App title in center
        title_label = QLabel(App_name)
        title_label.setFont(self.title_font)
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Scan ROMs button
        self.scan_btn = QPushButton()
        self.scan_btn.setFont(self.button_font)
        self.scan_btn.setIcon(self._create_folder_icon())
        self.scan_btn.setText("Scan ROMs")
        self.scan_btn.setIconSize(QSize(20, 20))
        self.scan_btn.setToolTip("Scan for ROM files")
        self.scan_btn.clicked.connect(self._scan_roms)
        layout.addWidget(self.scan_btn)
        
        # Save config button
        save_btn = QPushButton()
        save_btn.setFont(self.button_font)
        save_btn.setIcon(self._create_save_icon())
        save_btn.setText("Save Config")
        save_btn.setIconSize(QSize(20, 20))
        save_btn.setToolTip("Save configuration")
        layout.addWidget(save_btn)
        
        # Controller setup button
        self.controller_btn = QPushButton()
        self.controller_btn.setFont(self.button_font)
        self.controller_btn.setIcon(self._create_controller_icon())
        self.controller_btn.setText("Setup Controller")
        self.controller_btn.setIconSize(QSize(20, 20))
        self.controller_btn.setToolTip("Configure controller")
        self.controller_btn.clicked.connect(self._setup_controller)
        layout.addWidget(self.controller_btn)
        
        layout.addSpacing(10)
        
        # Info button
        info_btn = QPushButton()
        info_btn.setIcon(self._create_info_icon())
        info_btn.setFixedSize(35, 35)
        info_btn.setIconSize(QSize(20, 20))
        info_btn.setToolTip("Information")
        layout.addWidget(info_btn)
        
        layout.addSpacing(10)
        
        # Minimize button
        self.minimize_btn = QPushButton()
        self.minimize_btn.setIcon(self._create_minimize_icon())
        self.minimize_btn.setFixedSize(35, 35)
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.minimize_btn.setToolTip("Minimize")
        layout.addWidget(self.minimize_btn)
        
        # Maximize button
        self.maximize_btn = QPushButton()
        self.maximize_btn.setIcon(self._create_maximize_icon())
        self.maximize_btn.setFixedSize(35, 35)
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        self.maximize_btn.setToolTip("Maximize")
        layout.addWidget(self.maximize_btn)
        
        # Close button
        self.close_btn = QPushButton()
        self.close_btn.setIcon(self._create_close_icon())
        self.close_btn.setFixedSize(35, 35)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setToolTip("Close")
        layout.addWidget(self.close_btn)
        
        self.titlebar = titlebar
        return titlebar
        
    def _create_left_panel(self): #vers 1
        """Create Panel 1: Emulator platforms list"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header = QLabel("Emulator Platforms")
        header.setFont(self.panel_font)
        header.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        # Platform list
        self.platform_list = EmulatorListWidget()
        self.platform_list.platform_selected.connect(self._on_platform_selected)
        layout.addWidget(self.platform_list)
        
        # Populate with example platforms
        platforms = ["PlayStation 2", "PlayStation 3", "Nintendo Switch", "Xbox 360"]
        self.platform_list.populate_platforms(platforms)
        
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
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
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
        
    def _on_platform_selected(self, platform): #vers 1
        """Handle platform selection"""
        self.platform_status.setText(f"Platform: {platform}")
        # Populate games for this platform (placeholder)
        example_games = [f"{platform} Game 1", f"{platform} Game 2", f"{platform} Game 3"]
        self.game_list.populate_games(example_games)
        
    def _on_game_selected(self, game): #vers 1
        """Handle game selection"""
        self.game_status.setText(f"Game: {game}")

    def _apply_table_theme_styling(self): #vers 5
        """Apply theme styling to the table widget"""
        theme_colors = self._get_theme_colors("default")

        # Use standard theme variables from app_settings_system.py
        panel_bg = theme_colors.get('panel_bg', '#ffffff')
        bg_secondary = theme_colors.get('bg_secondary', '#f8f9fa')
        bg_tertiary = theme_colors.get('bg_tertiary', '#e9ecef')
        border = theme_colors.get('border', '#dee2e6')
        text_primary = theme_colors.get('text_primary', '#000000')
        text_secondary = theme_colors.get('text_secondary', '#495057')
        accent_primary = theme_colors.get('accent_primary', '#1976d2')

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {bg_secondary};
                alternate-background-color: {bg_tertiary};
                border: 1px solid {border};
                border-radius: 3px;
                gridline-color: {border};
                color: {text_primary};
                font-size: 9pt;
            }}
            QTableWidget::item {{
                padding: 5px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {accent_primary};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {panel_bg};
                color: {text_secondary};
                padding: 5px;
                border: 1px solid {border};
                font-weight: bold;
                font-size: 9pt;
            }}
        """)


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
                    print(f"✅ Using app_settings theme colors: {len(colors)} colors loaded")
                    return colors

            # Method 2: Try direct theme access
            if hasattr(self.main_window, 'app_settings') and hasattr(self.main_window.app_settings, 'themes'):
                current_theme = self.main_window.app_settings.current_settings.get("theme", "IMG_Factory")
                theme_data = self.main_window.app_settings.themes.get(current_theme, {})
                colors = theme_data.get('colors', {})
                if colors:
                    print(f"✅ Using direct theme access: {current_theme}")
                    return colors

        except Exception as e:
            print(f"❌ Theme color lookup error: {e}")

        # Fallback with proper theme variables
        print("⚠️ Using fallback theme colors")
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


    def _apply_theme(self): #vers 1
        """Apply theme styling to all windows"""
        if self.app_settings and APPSETTINGS_AVAILABLE:
            stylesheet = self.app_settings.get_stylesheet()
            self.setStyleSheet(stylesheet)
        else:
            self._apply_table_theme_styling()
            self._apply_log_theme_styling()
            self._apply_vertical_splitter_theme()
            self._apply_main_splitter_theme()
            self._apply_status_window_theme_styling()
            self._apply_file_list_window_theme_styling()

    def _apply_theme_bugged(self): #vers 2 #All window objects should themable, TODO
        """Apply theme styling using AppSettings if available"""
        if self.app_settings and APPSETTINGS_AVAILABLE:
            stylesheet = self.app_settings.get_stylesheet()
            self.setStyleSheet(stylesheet)
        else:
            # Fallback to hardcoded theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                }
                QFrame {
                    border: 1px solid #3d3d3d;
                }
                QPushButton {
                    background-color: #3d3d3d;
                    border: 1px solid #4d4d4d;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                }
                QPushButton:pressed {
                    background-color: #1d1d1d;
                }
                QPushButton:disabled {
                    background-color: #2d2d2d;
                    color: #666;
                }
                QListWidget {
                    background-color: #1a1a1a;
                    border: 1px solid #3d3d3d;
                }
                QListWidget::item:selected {
                    background-color: #0078d4;
                }
                QGroupBox {
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                }
            """)
        
    def _show_settings_dialog(self): #vers 1
        """Show settings dialog with theme and preferences"""
        if not APPSETTINGS_AVAILABLE:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Settings", "AppSettings system not available")
            return
            
        dialog = SettingsDialog(self.app_settings, self)
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
        
        menu = QMenu(self)
        
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
        
    def _scan_roms(self): #vers 1
        """Scan for ROM files in roms directory"""
        from PyQt6.QtWidgets import QMessageBox, QProgressDialog
        from PyQt6.QtCore import Qt
        
        if not self.core_downloader:
            QMessageBox.warning(self, "Scan ROMs", "Core downloader not initialized")
            return
            
        # Get available cores
        available_cores = self.core_downloader.get_available_cores()
        
        # Show progress dialog
        progress = QProgressDialog("Scanning ROM directories...", "Cancel", 0, len(available_cores), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setWindowTitle("Scanning ROMs")
        
        roms_dir = Path.cwd() / "roms"
        found_roms = {}
        
        for idx, (platform, cores) in enumerate(available_cores.items()):
            if progress.wasCanceled():
                break
                
            progress.setValue(idx)
            progress.setLabelText(f"Scanning {platform}...")
            
            platform_dir = roms_dir / platform
            if platform_dir.exists():
                # Get platform info for file extensions
                platform_info = self.core_downloader.get_core_info(platform)
                if platform_info:
                    extensions = platform_info.get("extensions", [])
                    roms = []
                    
                    for ext in extensions:
                        roms.extend(list(platform_dir.glob(f"*{ext}")))
                        
                    if roms:
                        found_roms[platform] = roms
                        
        progress.setValue(len(available_cores))
        
        # Show results
        if found_roms:
            total = sum(len(roms) for roms in found_roms.values())
            result = f"Found {total} ROM(s) across {len(found_roms)} platform(s):\n\n"
            for platform, roms in found_roms.items():
                result += f"{platform}: {len(roms)} ROM(s)\n"
            QMessageBox.information(self, "Scan Complete", result)
            
            # Populate platform list with found systems
            platforms_with_roms = list(found_roms.keys())
            self.platform_list.populate_platforms(platforms_with_roms)
        else:
            QMessageBox.information(self, "Scan Complete", 
                "No ROMs found.\n\nPlace ROM files in:\nroms/[System Name]/")
                
    def _setup_controller(self): #vers 1
        """Setup and configure game controller"""
        from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget
        
        if not self.gamepad_config:
            QMessageBox.warning(self, "Controller Setup", "Gamepad config not initialized")
            return
            
        # Detect controllers
        controllers = self.gamepad_config.detect_controllers()
        
        if not controllers:
            QMessageBox.information(self, "No Controllers", 
                "No controllers detected.\n\nPlease connect a controller and try again.")
            return
            
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
            
    def _on_theme_changed(self, theme_name): #vers 1
        """Handle theme change from settings dialog"""
        self._apply_theme()
        
    def _initialize_features(self): #vers 1
        """Initialize features after UI setup"""
        pass
        
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
                
    def _update_cursor(self, corner): #vers 1
        """Update cursor based on resize corner"""
        if corner == "top-left" or corner == "bottom-right":
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif corner == "top-right" or corner == "bottom-left":
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
    def _toggle_maximize(self): #vers 1
        """Toggle window maximize state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
            
    def mousePressEvent(self, event): #vers 3
        """Handle mouse press for dragging and resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.resize_corner = self._get_resize_corner(event.pos())
            
            if self.resize_corner:
                self.resizing = True
                self.drag_position = event.globalPosition().toPoint()
                self.initial_geometry = self.geometry()
                event.accept()
            elif self._is_on_draggable_area(event.pos()):
                # Use system move for better compatibility
                if hasattr(self.windowHandle(), 'startSystemMove'):
                    self.windowHandle().startSystemMove()
                    event.accept()
                else:
                    # Fallback to manual drag
                    self.dragging = True
                    self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    event.accept()
            else:
                # Let event propagate to child widgets (buttons)
                event.ignore()
        elif event.button() == Qt.MouseButton.RightButton:
            # Right-click on titlebar - show window menu
            if self._is_on_draggable_area(event.pos()):
                self._show_window_context_menu(event.pos())
                event.accept()
            else:
                event.ignore()
            
    def mouseMoveEvent(self, event): #vers 1
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
                self.update()
            self._update_cursor(corner)
            
    def mouseReleaseEvent(self, event): #vers 1
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            self.resize_corner = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            
    def mouseDoubleClickEvent(self, event): #vers 1
        """Handle double-click on titlebar to maximize/restore"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self._is_on_draggable_area(event.pos()):
                self._toggle_maximize()
                event.accept()
            else:
                super().mouseDoubleClickEvent(event)
                
    def resizeEvent(self, event): #vers 1
        """Handle resize event"""
        super().resizeEvent(event)
        
    def paintEvent(self, event): #vers 1
        """Paint corner resize indicators"""
        super().paintEvent(event)
        
        if not self.hover_corner:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw corner indicator
        size = self.corner_size
        w = self.width()
        h = self.height()
        
        painter.setPen(QPen(QColor(0, 120, 212), 2))
        
        if self.hover_corner == "top-left":
            points = [(0, size), (0, 0), (size, 0)]
        elif self.hover_corner == "top-right":
            points = [(w-size, 0), (w, 0), (w, size)]
        elif self.hover_corner == "bottom-left":
            points = [(0, h-size), (0, h), (size, h)]
        elif self.hover_corner == "bottom-right":
            points = [(w-size, h), (w, h), (w, h-size)]
        else:
            points = []
            
        if points:
            from PyQt6.QtGui import QPainterPath
            path = QPainterPath()
            path.moveTo(points[0][0], points[0][1])
            path.lineTo(points[1][0], points[1][1])
            path.lineTo(points[2][0], points[2][1])
            path.closeSubpath()
            painter.drawPath(path)
            
        painter.end()
        
    # SVG Icon creation methods
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
        
    def _create_settings_icon(self): #vers 1
        """Create settings (gear) icon"""
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QPixmap, QPainter
        
        svg_data = '''<svg width="16" height="16" viewBox="0 0 16 16">
            <circle cx="8" cy="8" r="3" fill="none" stroke="#ffffff" stroke-width="1.5"/>
            <circle cx="8" cy="2" r="1" fill="#ffffff"/>
            <circle cx="8" cy="14" r="1" fill="#ffffff"/>
            <circle cx="2" cy="8" r="1" fill="#ffffff"/>
            <circle cx="14" cy="8" r="1" fill="#ffffff"/>
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
        """Create controller (gamepad) icon for titlebar"""
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


# Standalone execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmuLauncherGUI()
    window.show()
    sys.exit(app.exec())
