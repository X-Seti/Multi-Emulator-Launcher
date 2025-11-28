#!/usr/bin/env python3
#this belongs in apps/gui/preview_window.py - Version: 1
# X-Seti - November28 2025 - Multi-Emulator Launcher - Preview Window

"""
Preview Window
Handles the preview window with record, screenshot, and shader effects functionality
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QPushButton, QSlider, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPen
import os
from pathlib import Path

##Methods list -
# __init__
# toggle_fullscreen
# take_screenshot
# start_recording
# stop_recording
# apply_shader
# set_volume
# update_preview

class PreviewWindow(QWidget): #vers 1
    """Preview window with record, screenshot, and shader effects"""
    
    # Signals for communication with main launcher
    fullscreen_requested = pyqtSignal()
    screenshot_taken = pyqtSignal(str)  # Path to screenshot
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    
    def __init__(self, parent=None): #vers 1
        """Initialize preview window"""
        super().__init__(parent)
        self.setWindowTitle("Game Preview")
        self.setGeometry(100, 100, 640, 480)
        
        # State variables
        self.is_fullscreen = False
        self.is_recording = False
        self.current_shader = "none"
        self.volume = 50  # 0-100
        
        self.setup_ui()
        
    def setup_ui(self): #vers 1
        """Set up the user interface"""
        layout = QVBoxLayout()
        
        # Main preview area
        self.preview_frame = QFrame()
        self.preview_frame.setFrameStyle(QFrame.Shape.Box)
        self.preview_frame.setLineWidth(2)
        self.preview_frame.setStyleSheet("background-color: black;")
        self.preview_frame.setMinimumHeight(400)
        
        # Control panel
        control_layout = QHBoxLayout()
        
        # Screenshot button
        self.screenshot_btn = QPushButton("📸 Screenshot")
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        control_layout.addWidget(self.screenshot_btn)
        
        # Record button
        self.record_btn = QPushButton("🔴 Record")
        self.record_btn.setCheckable(True)
        self.record_btn.clicked.connect(self.toggle_recording)
        control_layout.addWidget(self.record_btn)
        
        # Volume controls
        volume_label = QLabel("🔊 Volume:")
        control_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.volume)
        self.volume_slider.valueChanged.connect(self.set_volume)
        control_layout.addWidget(self.volume_slider)
        
        # Shader effects dropdown
        shader_label = QLabel("Shader:")
        control_layout.addWidget(shader_label)
        
        from PyQt6.QtWidgets import QComboBox
        self.shader_combo = QComboBox()
        self.shader_combo.addItems([
            "None", "CRT", "Green Screen", "RGB", "Composite", 
            "Scanlines", "Phosphor", "LCD", "Pixel Perfect"
        ])
        self.shader_combo.currentTextChanged.connect(self.apply_shader)
        control_layout.addWidget(self.shader_combo)
        
        # Fullscreen button
        self.fullscreen_btn = QPushButton("⛶ Fullscreen")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        control_layout.addWidget(self.fullscreen_btn)
        
        # Pop-out button
        self.popout_btn = QPushButton("⏏️ Pop-out")
        self.popout_btn.clicked.connect(self.toggle_popout)
        control_layout.addWidget(self.popout_btn)
        
        # Add to main layout
        layout.addWidget(self.preview_frame)
        layout.addLayout(control_layout)
        
        self.setLayout(layout)
        
    def toggle_fullscreen(self): #vers 1
        """Toggle fullscreen mode"""
        if not self.is_fullscreen:
            self.showFullScreen()
            self.is_fullscreen = True
            self.fullscreen_btn.setText("⛶ Exit Fullscreen")
        else:
            self.showNormal()
            self.is_fullscreen = False
            self.fullscreen_btn.setText("⛶ Fullscreen")
            
        self.fullscreen_requested.emit()
        
    def toggle_popout(self): #vers 1
        """Toggle pop-out window mode"""
        # This would toggle between being embedded and being a separate window
        if self.parent() is not None:
            # If embedded in main window, pop out
            self.setParent(None)
            self.setWindowFlags(Qt.WindowType.Window)
            self.show()
        else:
            # If pop-out, this would need to be handled by the parent
            pass
            
    def take_screenshot(self): #vers 1
        """Take a screenshot of the current preview"""
        # Create screenshots directory if it doesn't exist
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = screenshots_dir / filename
        
        # For now, create a dummy screenshot (in real implementation, 
        # this would capture the actual emulator output)
        pixmap = QPixmap(self.preview_frame.size())
        pixmap.fill(Qt.GlobalColor.black)
        
        # Draw a sample image
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, 
                        "Screenshot would appear here\nin real implementation")
        painter.end()
        
        pixmap.save(str(filepath))
        
        print(f"Screenshot saved to: {filepath}")
        self.screenshot_taken.emit(str(filepath))
        
    def toggle_recording(self, checked): #vers 1
        """Toggle recording on/off"""
        if checked:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self): #vers 1
        """Start recording the preview"""
        self.is_recording = True
        self.record_btn.setText("⏹️ Stop")
        self.record_btn.setStyleSheet("background-color: red; color: white;")
        print("Recording started...")
        self.recording_started.emit()
        
    def stop_recording(self): #vers 1
        """Stop recording the preview"""
        self.is_recording = False
        self.record_btn.setText("🔴 Record")
        self.record_btn.setStyleSheet("")
        print("Recording stopped.")
        self.recording_stopped.emit()
        
    def apply_shader(self, shader_name): #vers 1
        """Apply shader effect to preview"""
        shader_map = {
            "None": "none",
            "CRT": "crt",
            "Green Screen": "green_screen",
            "RGB": "rgb",
            "Composite": "composite",
            "Scanlines": "scanlines",
            "Phosphor": "phosphor",
            "LCD": "lcd",
            "Pixel Perfect": "pixel_perfect"
        }
        
        self.current_shader = shader_map.get(shader_name, "none")
        print(f"Applied shader: {self.current_shader}")
        
        # In a real implementation, this would send the shader to the emulator
        # For now, just update the preview visually
        self.update_preview()
        
    def set_volume(self, value): #vers 1
        """Set volume level"""
        self.volume = value
        print(f"Volume set to: {self.volume}%")
        
    def update_preview(self): #vers 1
        """Update the preview display"""
        # This would normally update with actual emulator output
        # For now, just refresh the display
        self.preview_frame.update()
        
    def paintEvent(self, event): #vers 1
        """Custom paint event for preview area"""
        super().paintEvent(event)
        
        if hasattr(self, 'preview_frame'):
            painter = QPainter(self.preview_frame)
            
            # Draw different visual based on shader
            if self.current_shader == "crt":
                # Draw CRT-style effect
                painter.fillRect(self.preview_frame.rect(), Qt.GlobalColor.black)
                painter.setPen(QPen(Qt.GlobalColor.green, 1))
                # Draw scanlines
                for y in range(0, self.preview_frame.height(), 2):
                    painter.drawLine(0, y, self.preview_frame.width(), y)
            elif self.current_shader == "green_screen":
                painter.fillRect(self.preview_frame.rect(), Qt.GlobalColor.green)
            elif self.current_shader == "rgb":
                # Draw RGB color bars
                width = self.preview_frame.width() // 3
                painter.fillRect(0, 0, width, self.preview_frame.height(), Qt.GlobalColor.red)
                painter.fillRect(width, 0, width, self.preview_frame.height(), Qt.GlobalColor.green)
                painter.fillRect(width*2, 0, width, self.preview_frame.height(), Qt.GlobalColor.blue)
            elif self.current_shader == "composite":
                # Draw composite-style blur effect
                painter.fillRect(self.preview_frame.rect(), Qt.GlobalColor.gray)
                painter.setPen(QPen(Qt.GlobalColor.white, 3))
                painter.drawRoundedRect(10, 10, self.preview_frame.width()-20, 
                                      self.preview_frame.height()-20, 10, 10)
            else:
                # Default: black background
                painter.fillRect(self.preview_frame.rect(), Qt.GlobalColor.black)
            
            # Draw placeholder text
            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            painter.drawText(self.preview_frame.rect(), Qt.AlignmentFlag.AlignCenter, 
                           f"Preview Area\nShader: {self.current_shader}\nVolume: {self.volume}%")
            
            painter.end()

def test_preview_window():
    """Test function for preview window"""
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    preview = PreviewWindow()
    preview.show()
    return app.exec()

if __name__ == "__main__":
    test_preview_window()