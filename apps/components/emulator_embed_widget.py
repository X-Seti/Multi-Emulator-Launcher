#!/usr/bin/env python3
#this belongs in apps/components/emulator_embed_widget.py - Version: 2
# X-Seti - December01 2025 - Multi-Emulator Launcher - Embedded Emulator Display

"""
Embedded Emulator Display Widget
Embeds external emulator windows into the display panel
Provides pop-out, fullscreen, and window controls
NOW WITH EMBEDDING FALLBACK
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFrame, QDialog)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QWindow
import subprocess
from pathlib import Path

##Methods list -
# __init__
# clear_artwork
# clear_welcome_message
# close_embedded_window
# embed_window
# enable_launch_button
# set_fullscreen
# set_popout
# set_window_mode
# show_title_artwork
# _attempt_embed
# _create_bottom_buttons
# _create_controls
# _create_embed_icon
# _create_fullscreen_icon
# _create_placeholder
# _create_popout_icon
# _find_emulator_window

class EmulatorEmbedWidget(QWidget): #vers 2
    """Widget that embeds external emulator windows"""

    window_embedded = pyqtSignal(bool)  # Emits when window embed status changes

    def __init__(self, parent=None, main_window=None, include_controls=True): #vers 3
        super().__init__(parent)
        self.main_window = main_window
        self.embedded_window = None
        self.emulator_process = None
        self.popout_dialog = None
        self.fullscreen_widget = None
        self.current_mode = 'embedded'  # 'embedded', 'popout', 'fullscreen'
        self.current_pixmap = None  # Store current artwork
        self.include_controls = include_controls  # Whether to show display mode controls
        self.embed_attempts = 0  # Track embed attempts
        self.max_embed_attempts = 3  # Maximum attempts before fallback

        self._setup_ui()

    def _setup_ui(self): #vers 2
        """Setup the embed widget UI"""
        # Main horizontal layout: display area + optional right controls
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Left side: Display area (embed frame + buttons)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)

        # Embed container frame
        self.embed_frame = QFrame()
        self.embed_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        self.embed_frame.setMinimumSize(640, 480)

        embed_layout = QVBoxLayout(self.embed_frame)
        embed_layout.setContentsMargins(0, 0, 0, 0)

        # Title artwork label (shows when not running emulator)
        self.title_artwork_label = QLabel()
        self.title_artwork_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_artwork_label.setScaledContents(False)
        self.title_artwork_label.setMinimumHeight(300)

        # Placeholder widget
        self.placeholder = self._create_placeholder()
        embed_layout.addWidget(self.placeholder)
        embed_layout.addWidget(self.title_artwork_label)
        self.title_artwork_label.hide()  # Hidden until artwork is set

        left_layout.addWidget(self.embed_frame)

        # Bottom buttons
        bottom_buttons = self._create_bottom_buttons()
        left_layout.addWidget(bottom_buttons)

        main_layout.addWidget(left_container, stretch=1)

        # Right side: Window control buttons (vertical) - OPTIONAL
        if self.include_controls:
            right_controls = self._create_controls()
            main_layout.addWidget(right_controls, stretch=0)

    def _create_controls(self): #vers 2
        """Create window control buttons - VERTICAL sidebar"""
        controls = QFrame()
        controls.setMaximumWidth(50)

        layout = QVBoxLayout(controls)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Get icon color from main window
        icon_color = '#ffffff'
        if self.main_window and hasattr(self.main_window, '_get_icon_color'):
            icon_color = self.main_window._get_icon_color()

        # Embedded mode button
        self.embed_btn = QPushButton()
        self.embed_btn.setToolTip("Embedded mode (default)")
        self.embed_btn.setIcon(self._create_embed_icon(icon_color))
        self.embed_btn.setIconSize(QSize(32, 32))
        self.embed_btn.setFixedSize(40, 40)
        self.embed_btn.clicked.connect(lambda: self.set_window_mode('embedded'))

        # Pop-out button
        self.popout_btn = QPushButton()
        self.popout_btn.setToolTip("Pop-out to resizable window")
        self.popout_btn.setIcon(self._create_popout_icon(icon_color))
        self.popout_btn.setIconSize(QSize(32, 32))
        self.popout_btn.setFixedSize(40, 40)
        self.popout_btn.clicked.connect(self.set_popout)

        # Fullscreen button
        self.fullscreen_btn = QPushButton()
        self.fullscreen_btn.setToolTip("Fullscreen mode")
        self.fullscreen_btn.setIcon(self._create_fullscreen_icon(icon_color))
        self.fullscreen_btn.setIconSize(QSize(32, 32))
        self.fullscreen_btn.setFixedSize(40, 40)
        self.fullscreen_btn.clicked.connect(self.set_fullscreen)

        layout.addWidget(self.embed_btn)
        layout.addWidget(self.popout_btn)
        layout.addWidget(self.fullscreen_btn)
        layout.addStretch()

        return controls

    def enable_launch_button(self, enabled=True): #vers 1
        """Enable or disable the launch button"""
        if hasattr(self, 'launch_btn'):
            self.launch_btn.setEnabled(enabled)

    def _create_placeholder(self): #vers 2
        """Create placeholder widget when no emulator running"""
        placeholder = QLabel("No emulator running\n\nLaunch a game to see it here\n\n(Embedding will be attempted)")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("font-size: 14pt; color: #888888; padding: 50px;")
        return placeholder


    def _create_bottom_buttons(self): #vers 3
        """Create bottom control buttons"""
        from apps.methods.svg_icon_factory import SVGIconFactory

        button_bar = QWidget()
        button_layout = QHBoxLayout(button_bar)
        button_layout.setContentsMargins(5, 5, 5, 5)

        # Get icon color
        icon_color = '#ffffff'
        if self.main_window and hasattr(self.main_window, '_get_icon_color'):
            icon_color = self.main_window._get_icon_color()

        # Launch button
        self.launch_btn = QPushButton("Launch")
        self.launch_btn.setIcon(SVGIconFactory.launch_icon(20, icon_color))  # CHANGED: play_icon -> launch_icon
        self.launch_btn.setIconSize(QSize(20, 20))
        self.launch_btn.setMinimumHeight(30)
        self.launch_btn.setEnabled(False)
        self.launch_btn.setToolTip("Launch selected game")
        if self.main_window and hasattr(self.main_window, '_on_launch_game'):
            self.launch_btn.clicked.connect(self.main_window._on_launch_game)
        button_layout.addWidget(self.launch_btn)

        # Game Artwork button
        self.gameart_btn = QPushButton("Game Artwork")
        self.gameart_btn.setIcon(SVGIconFactory.paint_icon(20, icon_color))  # CHANGED: image_icon -> paint_icon
        self.gameart_btn.setIconSize(QSize(20, 20))
        self.gameart_btn.setMinimumHeight(30)
        self.gameart_btn.setToolTip("View game artwork")
        if self.main_window and hasattr(self.main_window, '_show_game_artwork'):
            self.gameart_btn.clicked.connect(self.main_window._show_game_artwork)
        button_layout.addWidget(self.gameart_btn)

        button_layout.addStretch()

        # Game Manager button
        self.manage_btn = QPushButton("Game Manager")
        self.manage_btn.setIcon(SVGIconFactory.manage_icon(20, icon_color))
        self.manage_btn.setIconSize(QSize(20, 20))
        self.manage_btn.setMinimumHeight(30)
        self.manage_btn.setToolTip("Configure game settings")
        if self.main_window and hasattr(self.main_window, '_show_game_manager'):
            self.manage_btn.clicked.connect(self.main_window._show_game_manager)
        button_layout.addWidget(self.manage_btn)

        # Game Ports button
        self.ports_btn = QPushButton("Game Ports")
        self.ports_btn.setIcon(SVGIconFactory.package_icon(20, icon_color))
        self.ports_btn.setIconSize(QSize(20, 20))
        self.ports_btn.setMinimumHeight(30)
        self.ports_btn.setToolTip("View game ports across systems")
        if self.main_window and hasattr(self.main_window, '_show_ports_manager'):
            self.ports_btn.clicked.connect(self.main_window._show_ports_manager)
        button_layout.addWidget(self.ports_btn)

        # Stop button
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setIcon(SVGIconFactory.stop_icon(20, icon_color))
        self.stop_btn.setIconSize(QSize(20, 20))
        self.stop_btn.setMinimumHeight(30)
        self.stop_btn.setToolTip("Stop emulation")
        if self.main_window and hasattr(self.main_window, '_on_stop_emulation'):
            self.stop_btn.clicked.connect(self.main_window._on_stop_emulation)
        button_layout.addWidget(self.stop_btn)

        return button_bar

    def embed_window(self, process, skip_embed=False): #vers 2
        """Embed an external emulator window

        Args:
            process: subprocess.Popen instance of the emulator
            skip_embed: If True, skip embedding and let run standalone
        """
        self.emulator_process = process
        self.embed_attempts = 0

        if skip_embed:
            print("⚠ Embedding skipped - emulator running standalone")
            self.placeholder.setText("Emulator running in standalone window\n\n(Check your taskbar)")
            return

        # Wait a moment for window to appear
        QTimer.singleShot(1000, self._attempt_embed)  # Increased from 500ms to 1000ms

    def _attempt_embed(self): #vers 2
        """Attempt to find and embed the emulator window"""
        if not self.emulator_process:
            return

        self.embed_attempts += 1

        # Get the window ID
        window_id = self._find_emulator_window()

        if window_id:
            try:
                # Hide artwork/placeholder when embedding
                self.placeholder.hide()
                self.title_artwork_label.hide()

                # Create container for embedded window
                window = QWindow.fromWinId(window_id)
                if window:
                    container = self.createWindowContainer(window, self.embed_frame)
                    container.setMinimumSize(640, 480)

                    # Add embedded window to layout
                    layout = self.embed_frame.layout()
                    layout.addWidget(container)

                    self.embedded_window = container
                    self.window_embedded.emit(True)
                    print(f"✓ Embedded window ID: {window_id}")
                else:
                    print(f"Failed to create QWindow from ID: {window_id}")
            except Exception as e:
                print(f"Error embedding window: {e}")
        else:
            # Check if we should keep trying or give up
            if self.embed_attempts < self.max_embed_attempts:
                print(f"Could not find emulator window (attempt {self.embed_attempts}/{self.max_embed_attempts})")
                # Try again after longer delay
                QTimer.singleShot(2000, self._attempt_embed)  # Increased to 2 seconds
            else:
                # Give up embedding, let it run standalone
                print(f"⚠ Embedding failed after {self.max_embed_attempts} attempts - letting emulator run standalone")
                self.placeholder.setText("Emulator running in standalone window\n\n(Check your taskbar)")
                self.placeholder.show()

    def _find_emulator_window(self): #vers 2
        """Find the emulator window ID using xdotool

        Returns:
            Window ID as integer or None
        """
        if not self.emulator_process:
            return None

        try:
            # Get PID
            pid = self.emulator_process.pid

            # Use xdotool to find window by PID
            result = subprocess.run(
                ['xdotool', 'search', '--pid', str(pid)],
                capture_output=True,
                text=True,
                timeout=10  # Increased from 2 to 10 seconds
            )

            if result.returncode == 0 and result.stdout.strip():
                window_ids = result.stdout.strip().split('\n')
                # Return first window ID
                return int(window_ids[0])
        except subprocess.TimeoutExpired:
            print(f"xdotool search timed out for PID {pid}")
        except Exception as e:
            print(f"Error finding window: {e}")

        return None

    def set_window_mode(self, mode): #vers 1
        """Set the display mode"""
        self.current_mode = mode

        if mode == 'embedded':
            # Close popout/fullscreen and re-embed
            if self.popout_dialog:
                self.popout_dialog.close()
                self.popout_dialog = None
            if self.fullscreen_widget:
                self.fullscreen_widget.close()
                self.fullscreen_widget = None

            # Re-embed if process exists
            if self.emulator_process:
                self._attempt_embed()

    def set_popout(self): #vers 1
        """Pop out to separate resizable window"""
        if not self.emulator_process:
            return

        # Create dialog
        self.popout_dialog = QDialog(self.main_window)
        self.popout_dialog.setWindowTitle("Emulator Display")
        self.popout_dialog.resize(800, 600)

        layout = QVBoxLayout(self.popout_dialog)
        layout.setContentsMargins(0, 0, 0, 0)

        # Move embedded window to dialog
        if self.embedded_window:
            self.embed_frame.layout().removeWidget(self.embedded_window)
            layout.addWidget(self.embedded_window)

        self.popout_dialog.show()
        self.current_mode = 'popout'

    def set_fullscreen(self): #vers 1
        """Set fullscreen mode"""
        if not self.emulator_process:
            return

        # Create fullscreen widget
        self.fullscreen_widget = QWidget()
        self.fullscreen_widget.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)

        layout = QVBoxLayout(self.fullscreen_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Move embedded window to fullscreen
        if self.embedded_window:
            self.embed_frame.layout().removeWidget(self.embedded_window)
            layout.addWidget(self.embedded_window)

        self.fullscreen_widget.showFullScreen()
        self.current_mode = 'fullscreen'

        # ESC to exit fullscreen
        self.fullscreen_widget.keyPressEvent = lambda e: (
            self.set_window_mode('embedded') if e.key() == Qt.Key.Key_Escape else None
        )

    def close_embedded_window(self): #vers 1
        """Close and cleanup embedded window"""
        if self.embedded_window:
            self.embedded_window.hide()
            self.embedded_window.deleteLater()
            self.embedded_window = None

        if self.popout_dialog:
            self.popout_dialog.close()
            self.popout_dialog = None

        if self.fullscreen_widget:
            self.fullscreen_widget.close()
            self.fullscreen_widget = None

        # Show placeholder again, hide artwork
        self.title_artwork_label.hide()
        self.placeholder.setText("No emulator running\n\nLaunch a game to see it here\n\n(Embedding will be attempted)")
        self.placeholder.show()

        self.window_embedded.emit(False)

    def show_title_artwork(self, pixmap): #vers 1
        """Show game title artwork"""
        if pixmap and not pixmap.isNull():
            self.current_pixmap = pixmap
            self.title_artwork_label.setPixmap(
                pixmap.scaled(
                    self.title_artwork_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
            self.placeholder.hide()
            self.title_artwork_label.show()

    def clear_artwork(self): #vers 1
        """Clear artwork and show placeholder"""
        self.current_pixmap = None
        self.title_artwork_label.clear()
        self.title_artwork_label.hide()
        self.placeholder.show()

    def clear_welcome_message(self): #vers 1
        """Clear welcome message if showing"""
        if self.placeholder.text().startswith("Welcome"):
            self.placeholder.setText("No emulator running\n\nLaunch a game to see it here\n\n(Embedding will be attempted)")

    def _create_embed_icon(self, color): #vers 1
        """Create embedded window icon"""
        from PyQt6.QtGui import QPixmap, QPainter
        from PyQt6.QtSvg import QSvgRenderer

        svg = f'''<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="20" height="20" fill="none" stroke="{color}" stroke-width="2"/>
            <rect x="5" y="5" width="14" height="14" fill="none" stroke="{color}" stroke-width="1.5"/>
        </svg>'''

        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)

        renderer = QSvgRenderer(svg.encode())
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_popout_icon(self, color): #vers 1
        """Create pop-out window icon"""
        from PyQt6.QtGui import QPixmap, QPainter
        from PyQt6.QtSvg import QSvgRenderer

        svg = f'''<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="6" width="14" height="14" fill="none" stroke="{color}" stroke-width="2"/>
            <polyline points="18,2 22,2 22,6" fill="none" stroke="{color}" stroke-width="2"/>
            <line x1="22" y1="2" x2="14" y2="10" stroke="{color}" stroke-width="2"/>
        </svg>'''

        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)

        renderer = QSvgRenderer(svg.encode())
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_fullscreen_icon(self, color): #vers 1
        """Create fullscreen icon"""
        from PyQt6.QtGui import QPixmap, QPainter
        from PyQt6.QtSvg import QSvgRenderer

        svg = f'''<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <polyline points="4,10 4,4 10,4" fill="none" stroke="{color}" stroke-width="2"/>
            <polyline points="20,14 20,20 14,20" fill="none" stroke="{color}" stroke-width="2"/>
            <polyline points="14,4 20,4 20,10" fill="none" stroke="{color}" stroke-width="2"/>
            <polyline points="10,20 4,20 4,14" fill="none" stroke="{color}" stroke-width="2"/>
        </svg>'''

        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)

        renderer = QSvgRenderer(svg.encode())
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)
