# X-Seti - October15 2025 - Multi-Emulator Launcher - Main GUI
# This belongs in gui/gui_main.py - Version: 1
"""
Main GUI - PyQt6-based interface with PS4 controller support and theme integration.
"""

##Methods list -
# clear_cache
# create_settings_tab
# init_controller
# init_ui
# launch_selected_game
# load_platforms
# navigate_list
# next_tab
# on_tab_changed
# poll_controller
# previous_tab
# refresh_games
# run
# setup_shortcuts
# show_settings
# wait_button_release
# wait_hat_release

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QLabel, QPushButton, 
                             QMessageBox, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
import sys


class EmulatorGUI(QMainWindow): #vers 1
    def __init__(self, config, platform_manager, scanner, app_settings): #vers 1
        super().__init__()
        
        self.config = config
        self.platform_manager = platform_manager
        self.scanner = scanner
        self.app_settings = app_settings
        self.current_platform = None
        self.controller = None
        
        self.init_ui()
        self.init_controller()
        self.load_platforms()
    
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
        from components.settings_dialog import create_settings_widget
        return create_settings_widget(self)
    
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
    
    def init_ui(self): #vers 1
        """Initialize the user interface"""
        self.setWindowTitle("Multi-Emulator Launcher")
        self.setGeometry(100, 100, 1280, 720)
        
        stylesheet = self.app_settings.get_stylesheet()
        self.setStyleSheet(stylesheet)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        header_layout = QHBoxLayout()
        title = QLabel("🎮 Multi-Emulator Launcher")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(settings_btn)
        
        main_layout.addLayout(header_layout)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tab_widget)
        
        self.info_bar = QLabel("Select a game and press Enter or X (Cross) to launch")
        main_layout.addWidget(self.info_bar)
        
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
            guide_layout.addWidget(label)
        
        guide_widget = QWidget()
        guide_widget.setLayout(guide_layout)
        main_layout.addWidget(guide_widget)
        
        self.setup_shortcuts()
    
    def launch_selected_game(self): #vers 1
        """Launch the currently selected game"""
        from components.game_list_widget import GameListWidget
        current_widget = self.tab_widget.currentWidget()
        
        if not isinstance(current_widget, GameListWidget):
            return
        
        current_item = current_widget.currentItem()
        if not current_item:
            return
        
        game_data = current_item.data(Qt.ItemDataRole.UserRole)
        
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
        
        self.info_bar.setText(f"🚀 Launching: {game_data['display_name']}...")
        
        from core.core_launcher import CoreLauncher
        
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
    
    def load_platforms(self): #vers 1
        """Load all available platforms into tabs"""
        from components.game_list_widget import GameListWidget
        
        platforms = self.scanner.discover_platforms()
        
        for platform_name in platforms:
            game_list = GameListWidget()
            game_list.itemDoubleClicked.connect(self.launch_selected_game)
            
            games = self.scanner.scan_platform(platform_name)
            game_list.populate_games(games)
            
            self.tab_widget.addTab(game_list, platform_name)
        
        settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(settings_tab, "⚙️ Settings")
    
    def navigate_list(self, direction): #vers 1
        """Navigate game list"""
        from components.game_list_widget import GameListWidget
        current_widget = self.tab_widget.currentWidget()
        
        if isinstance(current_widget, GameListWidget):
            current_row = current_widget.currentRow()
            new_row = current_row + direction
            
            if new_row < 0:
                new_row = current_widget.count() - 1
            elif new_row >= current_widget.count():
                new_row = 0
            
            current_widget.setCurrentRow(new_row)
    
    def next_tab(self): #vers 1
        """Switch to next tab"""
        current_index = self.tab_widget.currentIndex()
        new_index = (current_index + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(new_index)
    
    def on_tab_changed(self, index): #vers 1
        """Handle tab change"""
        tab_name = self.tab_widget.tabText(index)
        if tab_name != "⚙️ Settings":
            self.current_platform = tab_name
    
    def poll_controller(self): #vers 1
        """Poll controller for input"""
        import pygame
        
        try:
            pygame.event.pump()
            
            if self.controller.get_button(0):
                self.launch_selected_game()
                self.wait_button_release(0)
            
            if self.controller.get_button(1):
                self.close()
            
            if self.controller.get_button(4):
                self.previous_tab()
                self.wait_button_release(4)
            
            if self.controller.get_button(5):
                self.next_tab()
                self.wait_button_release(5)
            
            if self.controller.get_button(9):
                self.show_settings()
                self.wait_button_release(9)
            
            hat = self.controller.get_hat(0)
            if hat[1] == 1:
                self.navigate_list(-1)
                self.wait_hat_release()
            elif hat[1] == -1:
                self.navigate_list(1)
                self.wait_hat_release()
            
            axis_y = self.controller.get_axis(1)
            deadzone = self.config['input'].get('deadzone', 0.15)
            
            if abs(axis_y) > deadzone:
                if axis_y < -deadzone:
                    self.navigate_list(-1)
                    import time
                    time.sleep(0.2)
                elif axis_y > deadzone:
                    self.navigate_list(1)
                    import time
                    time.sleep(0.2)
        
        except Exception as e:
            print(f"Controller error: {e}")
    
    def previous_tab(self): #vers 1
        """Switch to previous tab"""
        current_index = self.tab_widget.currentIndex()
        new_index = current_index - 1
        
        if new_index < 0:
            new_index = self.tab_widget.count() - 1
        
        self.tab_widget.setCurrentIndex(new_index)
    
    def refresh_games(self): #vers 1
        """Refresh game lists"""
        self.info_bar.setText("🔄 Refreshing game lists...")
        
        while self.tab_widget.count() > 1:
            self.tab_widget.removeTab(0)
        
        self.load_platforms()
        
        self.info_bar.setText("✅ Game lists refreshed!")
    
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
            if self.tab_widget.tabText(i) == "⚙️ Settings":
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
