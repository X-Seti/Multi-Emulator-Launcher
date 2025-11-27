#!/usr/bin/env python3
#this belongs in apps/methods/mel_app_icon.py - Version: 1
# X-Seti - November26 2025 - Multi-Emulator Launcher - App Icon Generator

"""
MEL App Icon Generator
Creates the Multi-Emulator Launcher application icon
Can generate different sizes: 16x16, 32x32, 64x64, 128x128, 256x256
"""

from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPixmap, QPainter, QIcon
from PyQt6.QtCore import Qt
from pathlib import Path

##Methods list -
# generate_icon
# save_icon_to_file
# get_mel_svg

def get_mel_svg(size: int = 64) -> str: #vers 1
    """
    Generate MEL app icon SVG
    
    Features:
    - Gradient blue/purple background
    - White "MEL" text
    - Retro gaming elements (D-pad, buttons, cartridge)
    - Rounded corners for modern look
    
    Args:
        size: Icon size in pixels
    
    Returns:
        SVG string data
    """
    svg_data = f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <!-- Background rounded square -->
        <rect width="64" height="64" rx="12" fill="url(#grad1)"/>
        
        <!-- Gradient definition -->
        <defs>
            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#4A90E2;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#7B68EE;stop-opacity:1" />
            </linearGradient>
        </defs>
        
        <!-- Controller D-pad top left -->
        <g transform="translate(8, 8)">
            <rect x="4" y="0" width="4" height="12" fill="#ffffff" opacity="0.3"/>
            <rect x="0" y="4" width="12" height="4" fill="#ffffff" opacity="0.3"/>
        </g>
        
        <!-- Controller buttons top right -->
        <circle cx="52" cy="12" r="2.5" fill="#ffffff" opacity="0.3"/>
        <circle cx="56" cy="16" r="2.5" fill="#ffffff" opacity="0.3"/>
        
        <!-- MEL Text -->
        <text x="32" y="40" font-family="Arial, sans-serif" font-size="22" 
              font-weight="bold" fill="#ffffff" text-anchor="middle">MEL</text>
        
        <!-- Subtitle -->
        <text x="32" y="52" font-family="Arial, sans-serif" font-size="7" 
              fill="#ffffff" opacity="0.8" text-anchor="middle">EMULATOR</text>
        
        <!-- Game cartridge icon bottom -->
        <rect x="24" y="56" width="16" height="6" rx="1" fill="#ffffff" opacity="0.3"/>
    </svg>'''
    return svg_data

def generate_icon(size: int = 64) -> QIcon: #vers 1
    """
    Generate QIcon from MEL SVG
    
    Args:
        size: Icon size in pixels
    
    Returns:
        QIcon object
    """
    svg_data = get_mel_svg(size)
    renderer = QSvgRenderer(svg_data.encode())
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    
    return QIcon(pixmap)

def save_icon_to_file(output_path: str, size: int = 256) -> bool: #vers 1
    """
    Save MEL icon to PNG file
    
    Args:
        output_path: Path to save PNG file
        size: Icon size in pixels (default 256 for high quality)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        svg_data = get_mel_svg(size)
        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        success = pixmap.save(output_path)
        if success:
            print(f"✓ Icon saved: {output_path} ({size}x{size})")
        return success
    except Exception as e:
        print(f"✗ Error saving icon: {e}")
        return False


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
    import sys
    
    app = QApplication(sys.argv)
    
    # Create test window
    window = QWidget()
    window.setWindowTitle("MEL App Icon Generator")
    window.setStyleSheet("background: #2b2b2b;")
    layout = QVBoxLayout(window)
    
    # Show different sizes
    sizes = [16, 32, 64, 128]
    
    for size in sizes:
        label = QLabel(f"MEL Icon {size}x{size}")
        label.setStyleSheet("color: white; font-weight: bold; margin-top: 10px;")
        layout.addWidget(label)
        
        icon_label = QLabel()
        icon = generate_icon(size)
        icon_label.setPixmap(icon.pixmap(size, size))
        layout.addWidget(icon_label)
    
    # Generate icon files
    output_dir = Path("icons")
    output_dir.mkdir(exist_ok=True)
    
    print("\nGenerating MEL icon files...")
    for size in [16, 32, 64, 128, 256]:
        filename = output_dir / f"mel_icon_{size}x{size}.png"
        save_icon_to_file(str(filename), size)
    
    print("\n✓ MEL icons generated successfully!")
    print(f"  Location: {output_dir.absolute()}")
    
    window.show()
    sys.exit(app.exec())
