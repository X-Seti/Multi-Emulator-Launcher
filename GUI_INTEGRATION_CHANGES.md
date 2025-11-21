# CoreLauncher GUI Integration Changes
# X-Seti - November20 2025 - Multi-Emulator Launcher

## Files Updated:
1. emu_launcher_main.py - Version 2 (COMPLETE - already in /outputs)
2. emu_launcher_gui.py - Version 2 (CHANGES BELOW)
3. core_launcher.py - Place in apps/core/ (already uploaded)

## Key Changes to emu_launcher_gui.py:

### 1. Add CoreLauncher Import (Line ~22)
```python
# Import core systems
from apps.core.core_launcher import CoreLauncher
```

### 2. Update EmuLauncherGUI.__init__ (vers 4)
```python
def __init__(self, parent=None, main_window=None, core_downloader=None, 
             core_launcher=None, gamepad_config=None): #vers 4
    """Initialize GUI with core systems"""
    if DEBUG_STANDALONE:
        print(f"{App_name} Initializing...")
        
    super().__init__(parent)
    
    self.main_window = main_window
    self.standalone_mode = (main_window is None)
    
    # Store core systems
    self.core_downloader = core_downloader
    self.core_launcher = core_launcher  # NEW
    self.gamepad_config = gamepad_config
    
    # State tracking for selected platform/game
    self.current_platform = None  # NEW
    self.current_rom_path = None  # NEW
    self.available_roms = {}       # NEW: {platform: [rom_paths]}
    
    # ... rest of init
```

### 3. Update _on_platform_selected (vers 2)
```python
def _on_platform_selected(self, platform): #vers 2
    """Handle platform selection - scan for actual ROMs"""
    self.current_platform = platform
    self.current_rom_path = None
    self.platform_status.setText(f"Platform: {platform}")
    
    # Scan for ROMs in roms/[platform]/ directory
    roms_dir = Path.cwd() / "roms" / platform
    
    if not roms_dir.exists():
        self.game_list.populate_games([])
        self.status_label.setText(f"No ROM directory: roms/{platform}/")
        return
        
    # Get platform info for valid extensions
    if self.core_downloader:
        platform_info = self.core_downloader.get_core_info(platform)
        if platform_info:
            extensions = platform_info.get("extensions", [])
            
            # Find all ROM files
            rom_files = []
            for ext in extensions:
                rom_files.extend(list(roms_dir.glob(f"*{ext}")))
                
            # Store ROM paths
            self.available_roms[platform] = rom_files
            
            # Populate game list with filenames
            game_names = [rom.stem for rom in rom_files]
            self.game_list.populate_games(game_names)
            
            self.status_label.setText(f"Found {len(rom_files)} ROM(s) for {platform}")
        else:
            self.game_list.populate_games([])
            self.status_label.setText(f"Unknown platform: {platform}")
    else:
        # No core_downloader, show placeholder
        self.game_list.populate_games([f"{platform} Game 1", f"{platform} Game 2"])
```

### 4. Update _on_game_selected (vers 2)
```python
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
                
                # Enable launch buttons in display widget
                if hasattr(self.display_widget, 'enable_launch_buttons'):
                    self.display_widget.enable_launch_buttons(True)
                break
```

### 5. Update EmulatorDisplayWidget.__init__ (vers 3)
```python
def __init__(self, parent=None, main_window=None): #vers 3
    """Initialize display widget with reference to main window"""
    super().__init__(parent)
    self.main_window = main_window  # Reference to EmuLauncherGUI
    self.setup_ui()
```

### 6. Update _create_left_panel to pass self reference (vers 2)
```python
def _create_right_panel(self): #vers 2
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
    
    # Display widget with reference to main window
    self.display_widget = EmulatorDisplayWidget(main_window=self)  # CHANGED
    layout.addWidget(self.display_widget)
    
    return panel
```

### 7. Add launch button handlers to EmulatorDisplayWidget (NEW METHODS)
```python
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
        
    # Get current platform and ROM from main window
    platform = self.main_window.current_platform
    rom_path = self.main_window.current_rom_path
    core_launcher = self.main_window.core_launcher
    
    if not all([platform, rom_path, core_launcher]):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Launch Error", 
            "Please select a platform and game first")
        return
        
    # Update status
    self.main_window.status_label.setText(f"Launching {rom_path.name}...")
    
    # Launch game
    success = core_launcher.launch_game(platform, rom_path)
    
    if success:
        self.main_window.status_label.setText(f"Running: {rom_path.name}")
    else:
        self.main_window.status_label.setText(f"Launch failed: {rom_path.name}")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Launch Failed",
            f"Could not launch {rom_path.name}\n\n"
            f"Check that you have the required emulator installed.\n"
            f"See terminal output for details.")
```

### 8. Wire launch buttons in _create_control_buttons (vers 2)
```python
def _create_control_buttons(self): #vers 2
    """Create bottom control buttons"""
    controls_frame = QFrame()
    controls_frame.setFrameStyle(QFrame.Shape.StyledPanel)
    
    layout = QHBoxLayout(controls_frame)
    layout.setContentsMargins(10, 5, 10, 5)
    layout.setSpacing(10)
    
    # Launch button
    self.launch_btn = QPushButton("Launch Game")
    self.launch_btn.setIcon(self._create_launch_icon())
    self.launch_btn.clicked.connect(self._on_launch_clicked)  # CONNECTED
    self.launch_btn.setEnabled(False)  # Disabled until game selected
    layout.addWidget(self.launch_btn)
    
    # Quick Launch button
    self.quick_launch_btn = QPushButton("Quick Launch")
    self.quick_launch_btn.clicked.connect(self._on_launch_clicked)  # CONNECTED
    self.quick_launch_btn.setEnabled(False)  # Disabled until game selected
    layout.addWidget(self.quick_launch_btn)
    
    layout.addStretch()
    
    # Stop button
    stop_btn = QPushButton("Stop")
    stop_btn.setIcon(self._create_stop_icon())
    stop_btn.clicked.connect(self._on_stop_clicked)  # NEW HANDLER NEEDED
    layout.addWidget(stop_btn)
    
    return controls_frame
```

### 9. Add stop emulation handler (NEW METHOD)
```python
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
```

## Summary of Flow:
1. User selects platform → _on_platform_selected() scans ROMs directory
2. User selects game → _on_game_selected() stores ROM path, enables launch buttons  
3. User clicks Launch → _on_launch_clicked() calls CoreLauncher.launch_game()
4. CoreLauncher finds appropriate emulator and launches
5. User clicks Stop → _on_stop_clicked() calls CoreLauncher.stop_emulation()

## Testing Checklist:
- [ ] Platform selection scans correct ROM directory
- [ ] Game selection enables launch buttons
- [ ] Launch button calls CoreLauncher
- [ ] Status updates show launch progress
- [ ] Stop button terminates emulation
- [ ] Error handling for missing emulators
- [ ] Error handling for missing ROMs

## Next Steps:
1. Apply these changes to full emu_launcher_gui.py file
2. Move uploaded core_launcher.py to apps/core/
3. Test with actual ROMs and installed emulators
