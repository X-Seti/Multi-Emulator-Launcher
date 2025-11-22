# X-Seti - November21 2025 - Multi-Emulator Launcher - Platform SVG Icons
# This file goes in /apps/methods/platform_icons.py - Version: 1
"""
Platform SVG Icon Factory - System icons for all supported platforms
Generates consistent SVG icons for emulator platforms/systems
"""

from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray, QSize

##Methods list -
# amiga_icon
# atari_2600_icon
# atari_800_icon
# atari_st_icon
# dreamcast_icon
# game_boy_advance_icon
# game_boy_icon
# gamecube_icon
# genesis_icon
# n64_icon
# nes_icon
# playstation_1_icon
# playstation_2_icon
# playstation_3_icon
# psp_icon
# saturn_icon
# snes_icon
# switch_icon
# wii_icon
# xbox_360_icon
# get_platform_icon

class PlatformIcons: #vers 1
    """Factory for platform/system SVG icons"""
    
    @staticmethod
    def _create_icon_from_svg(svg_data, size=32): #vers 1
        """Convert SVG data to QIcon"""
        byte_array = QByteArray(svg_data.encode())
        renderer = QSvgRenderer(byte_array)
        
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(0x00000000)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return QIcon(pixmap)
    
    @staticmethod
    def amiga_icon(color="#FF6B35", size=32): #vers 1
        """Amiga checkmark logo"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <path d="M6 16 L12 22 L26 8" stroke="{color}" stroke-width="3" 
                  fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="16" cy="16" r="14" stroke="{color}" stroke-width="2" fill="none"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def atari_2600_icon(color="#E85D75", size=32): #vers 1
        """Atari 2600 joystick"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="12" y="18" width="8" height="10" fill="{color}" rx="2"/>
            <circle cx="16" cy="10" r="6" fill="{color}"/>
            <line x1="16" y1="16" x2="16" y2="18" stroke="{color}" stroke-width="2"/>
            <rect x="14" y="22" width="4" height="2" fill="#ffffff"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def atari_800_icon(color="#E85D75", size=32): #vers 1
        """Atari 800 computer"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="10" width="24" height="14" fill="{color}" rx="2"/>
            <rect x="6" y="12" width="20" height="8" fill="#2a2a2a"/>
            <rect x="4" y="25" width="24" height="2" fill="{color}"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def atari_st_icon(color="#E85D75", size=32): #vers 1
        """Atari ST computer"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="8" width="24" height="16" fill="{color}" rx="2"/>
            <rect x="6" y="10" width="20" height="10" fill="#2a2a2a"/>
            <circle cx="26" cy="22" r="1.5" fill="#00ff00"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def dreamcast_icon(color="#0089CF", size=32): #vers 1
        """Sega Dreamcast swirl"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 4 Q26 8 26 16 Q26 24 16 28 Q6 24 6 16 Q6 8 16 4 Z" 
                  fill="none" stroke="{color}" stroke-width="3"/>
            <path d="M16 8 Q22 10 22 16 Q22 22 16 24" 
                  fill="none" stroke="{color}" stroke-width="2"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def game_boy_advance_icon(color="#8B4789", size=32): #vers 1
        """Game Boy Advance"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="6" y="4" width="20" height="24" fill="{color}" rx="3"/>
            <rect x="8" y="8" width="16" height="10" fill="#9fdf9f"/>
            <circle cx="12" cy="22" r="2" fill="#2a2a2a"/>
            <circle cx="20" cy="22" r="2" fill="#2a2a2a"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def game_boy_icon(color="#8B4789", size=32): #vers 1
        """Game Boy"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="8" y="4" width="16" height="24" fill="{color}" rx="2"/>
            <rect x="10" y="8" width="12" height="8" fill="#9fdf9f"/>
            <rect x="11" y="20" width="3" height="1" fill="#2a2a2a"/>
            <rect x="12" y="19" width="1" height="3" fill="#2a2a2a"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def gamecube_icon(color="#6A5ACD", size=32): #vers 1
        """Nintendo GameCube"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="8" y="8" width="16" height="16" fill="{color}" rx="2"/>
            <path d="M12 12 L16 16 L12 20 Z" fill="#ffffff"/>
            <circle cx="20" cy="16" r="3" fill="none" stroke="#ffffff" stroke-width="2"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def genesis_icon(color="#0089CF", size=32): #vers 1
        """Sega Genesis/Mega Drive"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="12" width="24" height="10" fill="{color}" rx="2"/>
            <circle cx="10" cy="17" r="2.5" fill="#2a2a2a"/>
            <circle cx="22" cy="17" r="1.5" fill="#ff4444"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def n64_icon(color="#FFD700", size=32): #vers 1
        """Nintendo 64"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 6 L28 16 L16 26 L4 16 Z" fill="{color}"/>
            <text x="16" y="19" text-anchor="middle" font-size="10" 
                  font-weight="bold" fill="#2a2a2a">64</text>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def nes_icon(color="#E60012", size=32): #vers 1
        """Nintendo Entertainment System"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="12" width="24" height="10" fill="{color}" rx="2"/>
            <rect x="8" y="15" width="4" height="4" fill="#2a2a2a" rx="1"/>
            <circle cx="22" cy="17" r="1.5" fill="#ffffff"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def playstation_1_icon(color="#003087", size=32): #vers 1
        """PlayStation 1"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <text x="16" y="20" text-anchor="middle" font-size="16" 
                  font-weight="bold" fill="{color}">PS</text>
            <circle cx="16" cy="16" r="13" stroke="{color}" stroke-width="2" fill="none"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def playstation_2_icon(color="#003087", size=32): #vers 1
        """PlayStation 2"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <text x="16" y="18" text-anchor="middle" font-size="14" 
                  font-weight="bold" fill="{color}">PS2</text>
            <circle cx="16" cy="16" r="13" stroke="{color}" stroke-width="2" fill="none"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def playstation_3_icon(color="#003087", size=32): #vers 1
        """PlayStation 3"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <text x="16" y="18" text-anchor="middle" font-size="14" 
                  font-weight="bold" fill="{color}">PS3</text>
            <circle cx="16" cy="16" r="13" stroke="{color}" stroke-width="2" fill="none"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def psp_icon(color="#003087", size=32): #vers 1
        """PlayStation Portable"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="10" width="24" height="12" fill="{color}" rx="3"/>
            <rect x="8" y="13" width="10" height="6" fill="#2a2a2a"/>
            <circle cx="22" cy="16" r="2" fill="#2a2a2a"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def saturn_icon(color="#0089CF", size=32): #vers 1
        """Sega Saturn"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="10" fill="none" stroke="{color}" stroke-width="3"/>
            <ellipse cx="16" cy="16" rx="14" ry="4" fill="none" stroke="{color}" stroke-width="2"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def snes_icon(color="#8B8B8B", size=32): #vers 1
        """Super Nintendo"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="12" width="24" height="10" fill="{color}" rx="2"/>
            <rect x="8" y="15" width="4" height="4" fill="#6a5acd" rx="1"/>
            <circle cx="20" cy="17" r="1.5" fill="#e60012"/>
            <circle cx="24" cy="17" r="1.5" fill="#ffde00"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def switch_icon(color="#E60012", size=32): #vers 1
        """Nintendo Switch"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="6" y="4" width="20" height="24" fill="{color}" rx="3"/>
            <rect x="8" y="6" width="16" height="20" fill="#2a2a2a" rx="2"/>
            <circle cx="12" cy="10" r="2" fill="#00d8ff"/>
            <circle cx="20" cy="22" r="2" fill="#ff4444"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def wii_icon(color="#009AC7", size=32): #vers 1
        """Nintendo Wii"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="11" y="6" width="3" height="20" fill="{color}" rx="1.5"/>
            <rect x="18" y="6" width="3" height="20" fill="{color}" rx="1.5"/>
            <circle cx="12.5" cy="9" r="1.5" fill="#ffffff"/>
            <circle cx="19.5" cy="9" r="1.5" fill="#ffffff"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def xbox_360_icon(color="#107C10", size=32): #vers 1
        """Xbox 360"""
        svg = f'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="12" fill="none" stroke="{color}" stroke-width="3"/>
            <path d="M16 8 Q10 12 10 16 T16 24 Q22 20 22 16 T16 8" 
                  fill="{color}"/>
        </svg>'''
        return PlatformIcons._create_icon_from_svg(svg, size)
    
    @staticmethod
    def get_platform_icon(platform_name, size=32): #vers 1
        """Get icon for platform by name"""
        # Normalize platform name
        name_lower = platform_name.lower()
        
        # Platform mapping
        if "amiga" in name_lower:
            return PlatformIcons.amiga_icon(size=size)
        elif "atari 2600" in name_lower:
            return PlatformIcons.atari_2600_icon(size=size)
        elif "atari 800" in name_lower or "atari-8" in name_lower:
            return PlatformIcons.atari_800_icon(size=size)
        elif "atari st" in name_lower:
            return PlatformIcons.atari_st_icon(size=size)
        elif "dreamcast" in name_lower:
            return PlatformIcons.dreamcast_icon(size=size)
        elif "game boy advance" in name_lower or "gba" in name_lower:
            return PlatformIcons.game_boy_advance_icon(size=size)
        elif "game boy" in name_lower or "gb" in name_lower:
            return PlatformIcons.game_boy_icon(size=size)
        elif "gamecube" in name_lower:
            return PlatformIcons.gamecube_icon(size=size)
        elif "genesis" in name_lower or "mega drive" in name_lower:
            return PlatformIcons.genesis_icon(size=size)
        elif "nintendo 64" in name_lower or "n64" in name_lower:
            return PlatformIcons.n64_icon(size=size)
        elif "nes" in name_lower or "nintendo entertainment" in name_lower:
            return PlatformIcons.nes_icon(size=size)
        elif "playstation 3" in name_lower or "ps3" in name_lower:
            return PlatformIcons.playstation_3_icon(size=size)
        elif "playstation 2" in name_lower or "ps2" in name_lower:
            return PlatformIcons.playstation_2_icon(size=size)
        elif "playstation 1" in name_lower or "ps1" in name_lower or "psx" in name_lower:
            return PlatformIcons.playstation_1_icon(size=size)
        elif "psp" in name_lower or "playstation portable" in name_lower:
            return PlatformIcons.psp_icon(size=size)
        elif "saturn" in name_lower:
            return PlatformIcons.saturn_icon(size=size)
        elif "super nintendo" in name_lower or "snes" in name_lower:
            return PlatformIcons.snes_icon(size=size)
        elif "switch" in name_lower:
            return PlatformIcons.switch_icon(size=size)
        elif "wii" in name_lower:
            return PlatformIcons.wii_icon(size=size)
        elif "xbox 360" in name_lower:
            return PlatformIcons.xbox_360_icon(size=size)
        else:
            # Default generic icon
            return PlatformIcons.amiga_icon(color="#888888", size=size)
