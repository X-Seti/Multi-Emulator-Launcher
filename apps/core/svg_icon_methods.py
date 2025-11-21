#!/usr/bin/env python3
#this belongs in apps/gui/emu_launcher_gui.py - SVG ICON METHODS
# X-Seti - November20 2025 - Multi-Emulator Launcher - SVG Icons
# ADD THESE METHODS TO YOUR EmuLauncherGUI CLASS

"""
Complete SVG Icon Methods
Copy all these methods into your EmuLauncherGUI class
Place them after the main methods, before the 'if __name__' block
"""

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
