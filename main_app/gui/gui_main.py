# X-Seti - October16 2025 - Multi-Emulator Launcher - Main GUI
# This belongs in main_app/gui/gui_main.py - Version: 2
"""
Main GUI - PyQt6-based frameless interface with custom window controls and PS4 controller support.
"""

##Methods list -
# clear_cache
# create_settings_tab
# init_controller
# init_ui
# launch_selected_game
# load_platforms
# mouseMoveEvent
# mousePressEvent
# mouseReleaseEvent
# navigate_list
# next_tab
# on_tab_changed
# poll_controller
# previous_tab
# refresh_games
# resizeEvent
# run
# setup_shortcuts
# show_settings
# wait_button_release
# wait_hat_release

##class SVGIcons -
# __init__
# _create_add_icon
# _create_check_icon
# _create_close_icon
# _create_create_icon
# _create_delete_icon
# _create_document_icon
# _create_duplicate_icon
# _create_export_icon
# _create_eye_icon
# _create_file_icon
# _create_filter_icon
# _create_folder_icon
# _create_import_icon
# _create_info_icon
# _create_list_icon
# _create_maximize_icon
# _create_minimize_icon
# _create_package_icon
# _create_pencil_icon
# _create_plus_icon
# _create_properties_icon
# _create_save_icon
# _create_settings_icon
# _create_trash_icon
# _create_undo_icon
# _svg_to_icon

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QLabel, QPushButton, 
                             QMessageBox, QSizeGrip)
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, QSize
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QIcon, QPixmap, QPainter, QCursor
from PyQt6.QtSvgWidgets import QSvgWidget
import sys


class SVGIcons: #vers 1
    """SVG Icon Generator - Creates all application icons from SVG data"""
    
    def __init__(self): #vers 1
        """Initialize SVG icon cache"""
        self.icon_cache = {}
    
    def _svg_to_icon(self, svg_data, size=24): #vers 1
        """Convert SVG bytes to QIcon"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        svg_widget = QSvgWidget()
        svg_widget.load(svg_data)
        svg_widget.render(painter)
        painter.end()
        
        return QIcon(pixmap)
    
    def _create_minimize_icon(self): #vers 1
        """Minimize - Horizontal line icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <line x1="5" y1="12" x2="19" y2="12"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_maximize_icon(self): #vers 1
        """Maximize - Square icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <rect x="5" y="5" width="14" height="14"
                stroke="currentColor" stroke-width="2"
                fill="none" rx="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_close_icon(self): #vers 1
        """Close - X icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <line x1="6" y1="6" x2="18" y2="18"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
            <line x1="18" y1="6" x2="6" y2="18"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_settings_icon(self): #vers 1
        """Settings/gear icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="2"/>
            <path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.93 4.93l1.41 1.41M13.66 13.66l1.41 1.41M4.93 15.07l1.41-1.41M13.66 6.34l1.41-1.41" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_undo_icon(self): #vers 1
        """Undo - Curved arrow icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M3 7v6h6M3 13a9 9 0 1018 0 9 9 0 00-18 0z"
                stroke="currentColor" stroke-width="2" fill="none"
                stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_info_icon(self): #vers 1
        """Info - circle with 'i' icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
            <path d="M12 11v6M12 8v.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_folder_icon(self): #vers 1
        """Open IMG - Folder icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-7l-2-2H5a2 2 0 00-2 2z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_file_icon(self): #vers 1
        """Open TXD - File icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="2"/>
            <path d="M14 2v6h6" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_save_icon(self): #vers 1
        """Save TXD - Floppy disk icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" stroke="currentColor" stroke-width="2"/>
            <path d="M17 21v-8H7v8M7 3v5h8" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_import_icon(self): #vers 1
        """Import - Download/Import icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="7 10 12 15 17 10"
                    stroke="currentColor" stroke-width="2"
                    fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="15" x2="12" y2="3"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_export_icon(self): #vers 1
        """Export - Upload/Export icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="17 8 12 3 7 8"
                    stroke="currentColor" stroke-width="2"
                    fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="3" x2="12" y2="15"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_package_icon(self): #vers 1
        """Export All - Package/Box icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" stroke="currentColor" stroke-width="2"/>
            <path d="M3.27 6.96L12 12.01l8.73-5.05M12 22.08V12" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_properties_icon(self): #vers 1
        """Properties - Info/Details icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 16v-4M12 8h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_plus_icon(self): #vers 1
        """Create New Entry - Plus icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 8v8M8 12h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_document_icon(self): #vers 1
        """Create New TXD - Document icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="2"/>
            <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_filter_icon(self): #vers 1
        """Filter/sliders icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="6" cy="4" r="2" fill="currentColor"/>
            <rect x="5" y="8" width="2" height="8" fill="currentColor"/>
            <circle cx="14" cy="12" r="2" fill="currentColor"/>
            <rect x="13" y="4" width="2" height="6" fill="currentColor"/>
            <circle cx="10" cy="8" r="2" fill="currentColor"/>
            <rect x="9" y="12" width="2" height="4" fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_add_icon(self): #vers 1
        """Add/plus icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <line x1="12" y1="5" x2="12" y2="19"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
            <line x1="5" y1="12" x2="19" y2="12"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_trash_icon(self): #vers 1
        """Delete/trash icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <polyline points="3 6 5 6 21 6"
                    stroke="currentColor" stroke-width="2"
                    fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_delete_icon(self): #vers 1
        """Delete/trash icon (alias)"""
        return self._create_trash_icon()

    def _create_duplicate_icon(self): #vers 1
        """Duplicate/copy icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="6" y="6" width="10" height="10" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M4 4h8v2H6v8H4V4z" fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_create_icon(self): #vers 1
        """Create/new icon"""
        return self._create_add_icon()

    def _create_pencil_icon(self): #vers 1
        """Edit - Pencil icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M17 3a2.83 2.83 0 114 4L7.5 20.5 2 22l1.5-5.5L17 3z" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_check_icon(self): #vers 1
        """Create check/verify icon - document with checkmark"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"
                fill="none" stroke="currentColor" stroke-width="2"/>
            <path d="M14 2v6h6"
                stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M9 13l2 2 4-4"
                stroke="currentColor" stroke-width="2" fill="none"
                stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_eye_icon(self): #vers 1
        """View - Eye icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2"/>
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)

    def _create_list_icon(self): #vers 1
        """Properties List - List icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


class EmulatorGUI(QMainWindow): #vers 2
    def __init__(self, config, platform_manager, scanner, app_settings): #vers 2
        super().__init__()
        
        self.config = config
        self.platform_manager = platform_manager
        self.scanner = scanner
        self.app_settings = app_settings
        self.current_platform = None
        self.controller = None
        self.icons = SVGIcons()
        
        # Window dragging
        self.dragging = False
        self.drag_position = QPoint()
        
        # Window resizing
        self.resizing = False
        self.resize_edge = None
        self.resize_margin = 8
        
        # Remove window frame
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        self.init_ui()
        self.init_controller()
        self.load_platforms()
    
    def init_ui(self): #vers 2
        """Initialize the user interface with custom title bar"""
        self.setWindowTitle("Multi-Emulator Launcher")
        self.setGeometry(100, 100, 1280, 720)
        self.setMinimumSize(800, 600)
        
        # Main container
        main_container = QWidget()
        self.setCentralWidget(main_container)
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Custom title bar
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setObjectName("titleBar")
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(5, 0, 5, 0)
        title_bar_layout.setSpacing(5)
        
        # Settings button (left side)
        settings_btn = QPushButton()
        settings_btn.setIcon(self.icons._create_settings_icon())
        settings_btn.setFixedSize(40, 40)
        settings_btn.setObjectName("windowButton")
        settings_btn.setToolTip("Settings")
        settings_btn.clicked.connect(self.show_settings)
        title_bar_layout.addWidget(settings_btn)
        
        # Title (center-left)
        title_label = QLabel("Multi-Emulator Launcher")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_bar_layout.addWidget(title_label)
        
        title_bar_layout.addStretch()
        
        # Window control buttons (right side)
        self.minimize_btn = QPushButton()
        self.minimize_btn.setIcon(self.icons._create_minimize_icon())
        self.minimize_btn.setFixedSize(40, 40)
        self.minimize_btn.setObjectName("windowButton")
        self.minimize_btn.clicked.connect(self.showMinimized)
        
        self.maximize_btn = QPushButton()
        self.maximize_btn.setIcon(self.icons._create_maximize_icon())
        self.maximize_btn.setFixedSize(40, 40)
        self.maximize_btn.setObjectName("windowButton")
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        
        self.close_btn = QPushButton()
        self.close_btn.setIcon(self.icons._create_close_icon())
        self.close_btn.setFixedSize(40, 40)
        self.close_btn.setObjectName("closeButton")
        self.close_btn.clicked.connect(self.close)
        
        title_bar_layout.addWidget(self.minimize_btn)
        title_bar_layout.addWidget(self.maximize_btn)
        title_bar_layout.addWidget(self.close_btn)
        
        container_layout.addWidget(title_bar)
        
        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header with settings button
        header_layout = QHBoxLayout()
        header_title = QLabel("Game Library")
        header_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        # Tab widget for platforms
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        content_layout.addWidget(self.tab_widget)
        
        container_layout.addWidget(content_widget)
        
        # Apply theme stylesheet
        stylesheet = self.app_settings.get_stylesheet()
        custom_styles = """
            #titleBar {
                background-color: palette(window);
                border-bottom: 1px solid palette(mid);
            }
            #windowButton {
                background-color: transparent;
                border: none;
                border-radius: 0px;
            }
            #windowButton:hover {
                background-color: palette(light);
            }
            #closeButton {
                background-color: transparent;
                border: none;
                border-radius: 0px;
            }
            #closeButton:hover {
                background-color: #e81123;
                color: white;
            }
        """
        self.setStyleSheet(stylesheet + custom_styles)
        
        self.setup_shortcuts()
    
    def toggle_maximize(self): #vers 1
        """Toggle between maximized and normal window state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def mousePressEvent(self, event): #vers 1
        """Handle mouse press for dragging and resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on title bar for dragging
            if event.position().y() < 40:
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
                return
            
            # Check if clicking on resize area
            edge = self.get_resize_edge(event.position().toPoint())
            if edge:
                self.resizing = True
                self.resize_edge = edge
                self.drag_position = event.globalPosition().toPoint()
                event.accept()
                return
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event): #vers 1
        """Handle mouse move for dragging and resizing"""
        if self.dragging and not self.isMaximized():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
            return
        
        if self.resizing:
            self.handle_resize(event.globalPosition().toPoint())
            event.accept()
            return
        
        # Update cursor based on position
        edge = self.get_resize_edge(event.position().toPoint())
        if edge:
            self.update_cursor(edge)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event): #vers 1
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            self.resize_edge = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
        
        super().mouseReleaseEvent(event)
    
    def get_resize_edge(self, pos): #vers 1
        """Determine which edge/corner is being hovered"""
        rect = self.rect()
        margin = self.resize_margin
        
        left = pos.x() < margin
        right = pos.x() > rect.width() - margin
        top = pos.y() < margin
        bottom = pos.y() > rect.height() - margin
        
        if top and left:
            return 'top-left'
        elif top and right:
            return 'top-right'
        elif bottom and left:
            return 'bottom-left'
        elif bottom and right:
            return 'bottom-right'
        elif top:
            return 'top'
        elif bottom:
            return 'bottom'
        elif left:
            return 'left'
        elif right:
            return 'right'
        
        return None
    
    def update_cursor(self, edge): #vers 1
        """Update cursor shape based on resize edge"""
        cursor_map = {
            'top': Qt.CursorShape.SizeVerCursor,
            'bottom': Qt.CursorShape.SizeVerCursor,
            'left': Qt.CursorShape.SizeHorCursor,
            'right': Qt.CursorShape.SizeHorCursor,
            'top-left': Qt.CursorShape.SizeFDiagCursor,
            'bottom-right': Qt.CursorShape.SizeFDiagCursor,
            'top-right': Qt.CursorShape.SizeBDiagCursor,
            'bottom-left': Qt.CursorShape.SizeBDiagCursor,
        }
        self.setCursor(cursor_map.get(edge, Qt.CursorShape.ArrowCursor))
    
    def handle_resize(self, global_pos): #vers 1
        """Handle window resizing"""
        delta = global_pos - self.drag_position
        self.drag_position = global_pos
        
        geo = self.geometry()
        min_size = self.minimumSize()
        
        if 'left' in self.resize_edge:
            new_width = geo.width() - delta.x()
            if new_width >= min_size.width():
                geo.setLeft(geo.left() + delta.x())
        
        if 'right' in self.resize_edge:
            new_width = geo.width() + delta.x()
            if new_width >= min_size.width():
                geo.setWidth(new_width)
        
        if 'top' in self.resize_edge:
            new_height = geo.height() - delta.y()
            if new_height >= min_size.height():
                geo.setTop(geo.top() + delta.y())
        
        if 'bottom' in self.resize_edge:
            new_height = geo.height() + delta.y()
            if new_height >= min_size.height():
                geo.setHeight(new_height)
        
        self.setGeometry(geo)
    
    def resizeEvent(self, event): #vers 1
        """Handle resize events"""
        super().resizeEvent(event)
    
    def clear_cache(self): #vers 1
        """Clear extraction cache"""
        from methods.rom_loader import RomLoader
        
        loader = RomLoader(self.config, self.platform_manager.platforms)
        
        reply = QMessageBox.question(
            self,
            "Clear Cache",
            "Are you sure you want to clear the extraction cache?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            cache_size = loader.get_cache_size()
            loader.clear_cache()
            
            size_mb = cache_size / (1024 * 1024)
            QMessageBox.information(
                self,
                "Cache Cleared",
                f"Cleared {size_mb:.2f} MB from cache"
            )
    
    def create_settings_tab(self): #vers 1
        """Create settings tab"""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox
        
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # Theme settings
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QVBoxLayout(theme_group)
        
        theme_btn = QPushButton("Open Theme Settings")
        theme_btn.clicked.connect(self.open_theme_settings)
        theme_layout.addWidget(theme_btn)
        
        layout.addWidget(theme_group)
        
        # Cache settings
        cache_group = QGroupBox("Cache Settings")
        cache_layout = QVBoxLayout(cache_group)
        
        cache_info = QLabel("ROM extraction cache location:\n" + str(self.config['cache_path']))
        cache_layout.addWidget(cache_info)
        
        clear_cache_btn = QPushButton("Clear Cache")
        clear_cache_btn.clicked.connect(self.clear_cache)
        cache_layout.addWidget(clear_cache_btn)
        
        layout.addWidget(cache_group)
        
        # Paths info
        paths_group = QGroupBox("Path Information")
        paths_layout = QVBoxLayout(paths_group)
        
        paths_info = QLabel(
            f"ROMs: {self.config['rom_path']}\n"
            f"Cores: {self.config['core_path']}\n"
            f"BIOS: {self.config['bios_path']}\n"
            f"Saves: {self.config['save_path']}"
        )
        paths_layout.addWidget(paths_info)
        
        layout.addWidget(paths_group)
        layout.addStretch()
        
        return settings_widget
    
    def open_theme_settings(self): #vers 1
        """Open full theme settings dialog"""
        from main_app.utils.app_settings_system import SettingsDialog
        
        dialog = SettingsDialog(self.app_settings, self)
        if dialog.exec():
            stylesheet = self.app_settings.get_stylesheet()
            self.setStyleSheet(stylesheet)
    
    def init_controller(self): #vers 1
        """Initialize PS4 controller support"""
        try:
            import pygame
            pygame.init()
            pygame.joystick.init()
            
            if pygame.joystick.get_count() > 0:
                self.controller = pygame.joystick.Joystick(self.config['input'].get('controller_index', 0))
                self.controller.init()
                print(f"Controller connected: {self.controller.get_name()}")
                
                self.controller_timer = QTimer()
                self.controller_timer.timeout.connect(self.poll_controller)
                self.controller_timer.start(50)
            else:
                print("No controller detected")
        
        except ImportError:
            print("pygame not available - controller support disabled")
    
    def launch_selected_game(self): #vers 1
        """Launch the currently selected game"""
        from main_app.components.game_list_widget import GameListWidget
        
        current_tab = self.tab_widget.currentWidget()
        
        if not isinstance(current_tab, GameListWidget):
            return
        
        selected_items = current_tab.table.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a game to launch.")
            return
        
        row = selected_items[0].row()
        game_data = current_tab.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        if not game_data:
            return
        
        from methods.rom_loader import RomLoader
        from core.core_launcher import CoreLauncher
        
        loader = RomLoader(self.config, self.platform_manager.platforms)
        launcher = CoreLauncher(self.config, self.platform_manager.platforms)
        
        rom_path = loader.load_rom(game_data['path'], game_data['platform'])
        
        if rom_path:
            launcher.launch_game(rom_path, game_data['platform'])
    
    def load_platforms(self): #vers 1
        """Load platform tabs"""
        from main_app.components.game_list_widget import GameListWidget
        
        available_platforms = self.scanner.discover_platforms()
        
        for platform in available_platforms:
            games = self.scanner.scan_platform(platform)
            
            if games:
                game_widget = GameListWidget(self, platform, games)
                self.tab_widget.addTab(game_widget, platform)
        
        settings_widget = self.create_settings_tab()
        self.tab_widget.addTab(settings_widget, "Settings")
    
    def navigate_list(self, direction): #vers 1
        """Navigate game list with controller or keyboard"""
        from main_app.components.game_list_widget import GameListWidget
        
        current_tab = self.tab_widget.currentWidget()
        
        if not isinstance(current_tab, GameListWidget):
            return
        
        table = current_tab.table
        current_row = table.currentRow()
        
        if direction == 'up' and current_row > 0:
            table.setCurrentCell(current_row - 1, 0)
        elif direction == 'down' and current_row < table.rowCount() - 1:
            table.setCurrentCell(current_row + 1, 0)
    
    def next_tab(self): #vers 1
        """Switch to next tab"""
        current = self.tab_widget.currentIndex()
        if current < self.tab_widget.count() - 1:
            self.tab_widget.setCurrentIndex(current + 1)
    
    def on_tab_changed(self, index): #vers 1
        """Handle tab change"""
        self.current_platform = self.tab_widget.tabText(index)
    
    def poll_controller(self): #vers 1
        """Poll PS4 controller for input"""
        if not self.controller:
            return
        
        import pygame
        pygame.event.pump()
        
        # D-pad navigation
        hat = self.controller.get_hat(0)
        if hat[1] == 1:
            self.navigate_list('up')
            self.wait_hat_release()
        elif hat[1] == -1:
            self.navigate_list('down')
            self.wait_hat_release()
        
        # Analog stick navigation
        left_y = self.controller.get_axis(1)
        deadzone = self.config['input'].get('deadzone', 0.15)
        
        if left_y < -deadzone:
            self.navigate_list('up')
            self.wait_hat_release()
        elif left_y > deadzone:
            self.navigate_list('down')
            self.wait_hat_release()
        
        # Button mapping
        if self.controller.get_button(0):
            self.launch_selected_game()
            self.wait_button_release(0)
        
        if self.controller.get_button(1):
            self.close()
        
        # L1/R1 for tab switching
        if self.controller.get_button(4):
            self.previous_tab()
            self.wait_button_release(4)
        
        if self.controller.get_button(5):
            self.next_tab()
            self.wait_button_release(5)
        
        # Options button for settings
        if self.controller.get_button(9):
            self.show_settings()
            self.wait_button_release(9)
    
    def previous_tab(self): #vers 1
        """Switch to previous tab"""
        current = self.tab_widget.currentIndex()
        if current > 0:
            self.tab_widget.setCurrentIndex(current - 1)
    
    def refresh_games(self): #vers 1
        """Refresh game list for current platform"""
        from main_app.components.game_list_widget import GameListWidget
        
        current_tab = self.tab_widget.currentWidget()
        
        if isinstance(current_tab, GameListWidget):
            platform = self.tab_widget.tabText(self.tab_widget.currentIndex())
            games = self.scanner.scan_platform(platform)
            current_tab.populate_table(games)
    
    def run(self): #vers 1
        """Start the GUI application"""
        self.show()
        return QApplication.instance().exec()
    
    def setup_shortcuts(self): #vers 1
        """Setup keyboard shortcuts"""
        launch_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        launch_shortcut.activated.connect(self.launch_selected_game)
        
        exit_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        exit_shortcut.activated.connect(self.close)
        
        prev_tab = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        prev_tab.activated.connect(self.previous_tab)
        
        next_tab = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        next_tab.activated.connect(self.next_tab)
    
    def show_settings(self): #vers 1
        """Show settings tab"""
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "Settings":
                self.tab_widget.setCurrentIndex(i)
                break
    
    def wait_button_release(self, button): #vers 1
        """Wait for button to be released"""
        import pygame
        import time
        
        while self.controller.get_button(button):
            pygame.event.pump()
            time.sleep(0.05)
    
    def wait_hat_release(self): #vers 1
        """Wait for D-pad to be released"""
        import pygame
        import time
        
        while self.controller.get_hat(0) != (0, 0):
            pygame.event.pump()
            time.sleep(0.05)


def main(): #vers 1
    app = QApplication(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
