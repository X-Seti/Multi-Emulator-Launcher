"""
Main GUI Application
PyQt6-based interface with PS4 controller support
"""

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QListWidget, QListWidgetItem,
                             QLabel, QPushButton, QMessageBox, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
import sys


class GameListWidget(QListWidget):
    """Custom list widget for displaying games"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 16px;
                border: none;
                padding: 10px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                border-left: 5px solid #00ff00;
            }
            QListWidget::item:hover {
                background-color: #2d2d2d;
            }
        """)
    
    def populate_games(self, games):
        """Populate the list with games"""
        self.clear()
        
        for game in games:
            # Create display text
            display_text = game['display_name']
            
            # Add disk count if multi-disk
            if game.get('disk_count', 0) > 1:
                display_text += f" ({game['disk_count']} disks)"
            
            # Add type indicator
            type_indicator = ""
            if game['type'] == 'zip':
                type_indicator = " 📦"
            elif game['type'] == 'folder':
                type_indicator = " 📁"
            elif game['type'] == 'multidisk':
                type_indicator = " 💾"
            
            display_text += type_indicator
            
            # Create list item
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, game)
            self.addItem(item)


class EmulatorGUI(QMainWindow):
    """Main GUI window"""
    
    def __init__(self, config, platform_manager, scanner):
        super().__init__()
        
        self.config = config
        self.platform_manager = platform_manager
        self.scanner = scanner
        self.current_platform = None
        self.controller = None
        
        self.init_ui()
        self.init_controller()
        self.load_platforms()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Multi-Emulator Launcher")
        self.setGeometry(100, 100, 1280, 720)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QTabBar::tab:hover {
                background-color: #3d3d3d;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("🎮 Multi-Emulator Launcher")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Settings button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(settings_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tab widget for platforms
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tab_widget)
        
        # Bottom info bar
        self.info_bar = QLabel("Select a game and press Enter or X (Cross) to launch")
        self.info_bar.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                padding: 10px;
                border-top: 1px solid #444;
            }
        """)
        main_layout.addWidget(self.info_bar)
        
        # Controller guide
        guide_layout = QHBoxLayout()
        guide_text = [
            "🎮 D-Pad/Stick: Navigate",
            "✖ (Cross): Launch",
            "○ (Circle): Back",
            "L1/R1: Switch Tabs",
            "Options: Settings"
        ]
        for text in guide_text:
            label = QLabel(text)
            label.setStyleSheet("font-size: 12px; color: #888;")
            guide_layout.addWidget(label)
        
        guide_widget = QWidget()
        guide_widget.setLayout(guide_layout)
        main_layout.addWidget(guide_widget)
        
        # Keyboard shortcuts
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Enter to launch
        launch_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        launch_shortcut.activated.connect(self.launch_selected_game)
        
        # Escape to exit
        exit_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        exit_shortcut.activated.connect(self.close)
        
        # Left/Right arrows for tab switching
        prev_tab = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        prev_tab.activated.connect(self.previous_tab)
        
        next_tab = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        next_tab.activated.connect(self.next_tab)
    
    def init_controller(self):
        """Initialize PS4 controller support"""
        try:
            import pygame
            pygame.init()
            pygame.joystick.init()
            
            if pygame.joystick.get_count() > 0:
                self.controller = pygame.joystick.Joystick(0)
                self.controller.init()
                
                # Start controller polling timer
                self.controller_timer = QTimer()
                self.controller_timer.timeout.connect(self.poll_controller)
                self.controller_timer.start(50)  # Poll every 50ms
                
                self.info_bar.setText(f"🎮 Controller connected: {self.controller.get_name()}")
            else:
                self.info_bar.setText("⚠️ No controller detected - using keyboard")
        
        except ImportError:
            self.info_bar.setText("⚠️ pygame not installed - controller support disabled")
            self.controller = None
    
    def poll_controller(self):
        """Poll controller for input"""
        if not self.controller:
            return
        
        try:
            import pygame
            pygame.event.pump()
            
            # Button mapping for PS4 controller
            # Button 0 = Cross (X)
            # Button 1 = Circle (O)
            # Button 2 = Square
            # Button 3 = Triangle
            # Button 4 = Share
            # Button 6 = Options
            # Button 9 = L1
            # Button 10 = R1
            
            # Cross button - Launch game
            if self.controller.get_button(0):
                self.launch_selected_game()
                self.wait_button_release(0)
            
            # Circle button - Back/Exit
            if self.controller.get_button(1):
                self.close()
            
            # L1 - Previous tab
            if self.controller.get_button(9):
                self.previous_tab()
                self.wait_button_release(9)
            
            # R1 - Next tab
            if self.controller.get_button(10):
                self.next_tab()
                self.wait_button_release(10)
            
            # Options button - Settings
            if self.controller.get_button(6):
                self.show_settings()
                self.wait_button_release(6)
            
            # D-Pad navigation
            hat = self.controller.get_hat(0)
            if hat[1] == 1:  # Up
                self.navigate_list(-1)
                self.wait_hat_release()
            elif hat[1] == -1:  # Down
                self.navigate_list(1)
                self.wait_hat_release()
            
            # Left stick navigation
            axis_y = self.controller.get_axis(1)
            deadzone = self.config['input'].get('deadzone', 0.15)
            
            if abs(axis_y) > deadzone:
                if axis_y < -deadzone:  # Up
                    self.navigate_list(-1)
                    import time
                    time.sleep(0.2)
                elif axis_y > deadzone:  # Down
                    self.navigate_list(1)
                    import time
                    time.sleep(0.2)
        
        except Exception as e:
            print(f"Controller error: {e}")
    
    def wait_button_release(self, button):
        """Wait for button to be released (prevent double-press)"""
        import pygame
        import time
        
        while self.controller.get_button(button):
            pygame.event.pump()
            time.sleep(0.05)
    
    def wait_hat_release(self):
        """Wait for D-pad to be released"""
        import pygame
        import time
        
        while self.controller.get_hat(0) != (0, 0):
            pygame.event.pump()
            time.sleep(0.05)
    
    def load_platforms(self):
        """Load all available platforms into tabs"""
        platforms = self.scanner.discover_platforms()
        
        for platform_name in platforms:
            # Create tab for platform
            game_list = GameListWidget()
            game_list.itemDoubleClicked.connect(self.launch_selected_game)
            
            # Load games for this platform
            games = self.scanner.scan_platform(platform_name)
            game_list.populate_games(games)
            
            # Add tab
            self.tab_widget.addTab(game_list, platform_name)
        
        # Add settings tab
        settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(settings_tab, "⚙️ Settings")
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # Title
        title = QLabel("Settings")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Info section
        info_layout = QGridLayout()
        
        info_layout.addWidget(QLabel("ROM Path:"), 0, 0)
        info_layout.addWidget(QLabel(self.config['rom_path']), 0, 1)
        
        info_layout.addWidget(QLabel("Core Path:"), 1, 0)
        info_layout.addWidget(QLabel(self.config['core_path']), 1, 1)
        
        info_layout.addWidget(QLabel("BIOS Path:"), 2, 0)
        info_layout.addWidget(QLabel(self.config['bios_path']), 2, 1)
        
        info_layout.addWidget(QLabel("Save Path:"), 3, 0)
        info_layout.addWidget(QLabel(self.config['save_path']), 3, 1)
        
        layout.addLayout(info_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh Game List")
        refresh_btn.clicked.connect(self.refresh_games)
        button_layout.addWidget(refresh_btn)
        
        cache_btn = QPushButton("🗑️ Clear Cache")
        cache_btn.clicked.connect(self.clear_cache)
        button_layout.addWidget(cache_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return settings_widget
    
    def on_tab_changed(self, index):
        """Handle tab change"""
        tab_name = self.tab_widget.tabText(index)
        if tab_name != "⚙️ Settings":
            self.current_platform = tab_name
    
    def navigate_list(self, direction):
        """Navigate game list (direction: -1 for up, 1 for down)"""
        current_widget = self.tab_widget.currentWidget()
        
        if isinstance(current_widget, GameListWidget):
            current_row = current_widget.currentRow()
            new_row = current_row + direction
            
            # Wrap around
            if new_row < 0:
                new_row = current_widget.count() - 1
            elif new_row >= current_widget.count():
                new_row = 0
            
            current_widget.setCurrentRow(new_row)
    
    def previous_tab(self):
        """Switch to previous tab"""
        current_index = self.tab_widget.currentIndex()
        new_index = current_index - 1
        
        if new_index < 0:
            new_index = self.tab_widget.count() - 1
        
        self.tab_widget.setCurrentIndex(new_index)
    
    def next_tab(self):
        """Switch to next tab"""
        current_index = self.tab_widget.currentIndex()
        new_index = (current_index + 1) % self.tab_widget.count()
        
        self.tab_widget.setCurrentIndex(new_index)
    
    def launch_selected_game(self):
        """Launch the currently selected game"""
        current_widget = self.tab_widget.currentWidget()
        
        if not isinstance(current_widget, GameListWidget):
            return
        
        current_item = current_widget.currentItem()
        if not current_item:
            return
        
        game_data = current_item.data(Qt.ItemDataRole.UserRole)
        
        # Check BIOS before launching
        platform = game_data['platform']
        bios_ok, bios_msg = self.platform_manager.verify_bios(
            platform, 
            self.config['bios_path']
        )
        
        if not bios_ok:
            QMessageBox.warning(
                self,
                "BIOS Missing",
                f"Cannot launch {game_data['display_name']}\n\n{bios_msg}"
            )
            return
        
        # Launch game
        self.info_bar.setText(f"🚀 Launching: {game_data['display_name']}...")
        
        # Import and launch
        from src.core_launcher import CoreLauncher
        
        try:
            launcher = CoreLauncher(self.config, self.platform_manager)
            launcher.launch_game(game_data)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Launch Error",
                f"Failed to launch game:\n\n{str(e)}"
            )
            self.info_bar.setText(f"❌ Failed to launch: {game_data['display_name']}")
    
    def show_settings(self):
        """Show settings tab"""
        # Find settings tab
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "⚙️ Settings":
                self.tab_widget.setCurrentIndex(i)
                break
    
    def refresh_games(self):
        """Refresh game lists"""
        self.info_bar.setText("🔄 Refreshing game lists...")
        
        # Clear existing tabs (except settings)
        while self.tab_widget.count() > 1:
            self.tab_widget.removeTab(0)
        
        # Reload platforms
        self.load_platforms()
        
        self.info_bar.setText("✅ Game lists refreshed!")
    
    def clear_cache(self):
        """Clear extraction cache"""
        from src.rom_loader import RomLoader
        
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
    
    def run(self):
        """Start the GUI application"""
        self.show()
        return QApplication.instance().exec()


def main():
    app = QApplication(sys.argv)
    # GUI will be created by EmulatorLauncher
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
