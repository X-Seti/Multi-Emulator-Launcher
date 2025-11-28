#!/usr/bin/env python3
#this belongs in apps/methods/platform_scanner.py - Version: 4
# X-Seti - November28 2025 - Multi-Emulator Launcher - Platform Scanner

"""
Dynamic Platform Scanner
Discovers emulator platforms by scanning ROM directories
Handles spaces in names, ignores system files, supports compressed formats (ZIP/7Z/RAR)
Integrates with dynamic core detection and BIOS management
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from .system_core_scanner import SystemCoreScanner
from .bios_manager import BiosManager

##Methods list -
# __init__
# get_platform_info
# get_platforms
# scan_platforms
# update_platform_config_with_cores
# _count_roms_in_directory
# _detect_file_extensions
# _guess_platform_type
# _is_system_file

class PlatformScanner: #vers 4
    """Dynamically discovers platforms from ROM directory structure with core detection"""
    
    # Files/folders to ignore
    IGNORE_PATTERNS = {
        '.folder',  # System marker files
        '.DS_Store',  # macOS
        'Thumbs.db',  # Windows
        'desktop.ini',  # Windows
        '.git', '.gitignore',
        '__pycache__',
        'bootcode.bin',  # Raspberry Pi boot files
        'kernel.img', 'kernel7.img', 'kernel8-32.img',
        'bcm', #Raspberry Pi device tree files (start with bcm)
        'HXCSDFE.CFG', 'IMAGE_A.CFG',  # HxC floppy emulator
        '.iso',  # Boot ISOs like SPECCY97.iso
    }
    
    # Extension patterns
    EXTENSION_HINTS = {
        ".adf": ["Amiga"],
        ".ipf": ["Amiga"],
        ".dms": ["Amiga"],
        ".st": ["Atari ST"],
        ".stx": ["Atari ST"],
        ".a26": ["Atari 2600"],
        ".a52": ["Atari 5200"],
        ".a78": ["Atari 7800"],
        ".xex": ["Atari 800"],
        ".atr": ["Atari 800"],
        ".cas": ["Atari 800"],
        ".cue": ["PlayStation 1"],
        ".bin": ["PlayStation 1", "Atari 2600"],
        ".iso": ["PlayStation 2"],
        ".tap": ["ZX Spectrum", "Amstrad CPC"],
        ".tzx": ["ZX Spectrum"],
        ".sna": ["ZX Spectrum"],
        ".z80": ["ZX Spectrum"],
        ".dsk": ["Amstrad CPC", "MSX"],
        ".cdt": ["Amstrad CPC"],
        ".d64": ["C64"],
        ".t64": ["C64"],
        ".crt": ["C64"],
        ".prg": ["C64"],
        ".d81": ["C128"],
        ".rom": ["MSX", "Plus4", "Sam Coupe"],
        ".mx1": ["MSX"],
        ".mx2": ["MSX"],
        ".p41": ["Plus4"],
        ".mgt": ["Sam Coupe"],
        ".sad": ["Sam Coupe"],
        ".nes": ["Nintendo Entertainment System"],
        ".sfc": ["Super Nintendo"],
        ".smc": ["Super Nintendo"],
        ".gba": ["Game Boy Advance"],
        ".gen": ["Genesis"],
        ".md": ["Genesis"],
        ".smd": ["Genesis"],
    }
    
    # Platform to core mapping for dynamic detection
    PLATFORM_CORE_MAPPING = {
        "Amiga": ["puae", "uae"],
        "Atari 2600": ["stella", "stella2014"],
        "Atari 5200": ["atari800", "atari800_libretro"],
        "Atari 7800": ["prosystem"],
        "Atari 800": ["atari800", "atari800_libretro"],
        "Atari ST": ["hatari"],
        "Amstrad CPC": ["cap32", "crocods"],
        "BBC Micro": ["mame", "mess"],
        "C64": ["vice_x64", "vice_x64_libretro"],
        "Commodore 64": ["vice_x64", "vice_x64_libretro"],
        "MSX": ["fmsx", "bluemsx", "mesen-s"],
        "MSX1": ["fmsx", "bluemsx"],
        "MSX2": ["fmsx", "bluemsx"],
        "ZX Spectrum": ["fuse", "scummvm"],
        "ZX Spectrum 128": ["fuse"],
        "Z81-Spec256": ["fuse", "vaporspec"],
        "MS-DOS": ["dosbox_pure", "dosbox"],
        "Dragon 32-64": ["xroar"],
        "Sam Coupe": ["mame"],
        "Oric Atmos": ["mame"],
        "TRS-80": ["mame"],
        "Fujitsu FM-7": ["mame"],
        "Plus4": ["vice_xplus4"],
    }
    
    # Platform aliases for fuzzy matching
    PLATFORM_ALIASES = {
        # Sinclair variants
        "zxspectrum": ["zx spectrum", "zx-spectrum", "zxspectrum", "spectrum", "zxspeccy", "spec256", "z81-spec256", "z81 spec256", "z81spec256"],
        "zx81": ["zx 81", "zx-81", "zx81", "sinclair zx81"],
        
        # MSX variants
        "msx": ["msx", "msx1", "msx2", "msx2+", "msx turbo", "msx-turbo"],
        "msx1": ["msx1", "msx 1"],
        "msx2": ["msx2", "msx 2"],
        
        # SAM Coupe variants
        "samcoupe": ["sam coupe", "samcoupe", "sam-coupe", "sam_couple"],
        
        # Amstrad variants
        "amstradcpc": ["amstrad cpc", "amstradcpc", "cpc", "amstrad6128", "amstrad464", "amstrad 6128", "amstrad 464"],
        
        # Atari variants
        "atarist": ["atari st", "atari-st", "atari_st", "atarist"],
        "atari800": ["atari 800", "atari800", "atari800xl", "atari 800xl", "atari-xl", "atari-xe"],
        "atari5200": ["atari 5200", "atari-5200", "atari_5200", "a5200", "atari5200"],
        "atari2600": ["atari 2600", "atari-2600", "atari_2600", "a2600"],
        "atari7800": ["atari 7800", "atari-7800", "atari_7800", "a7800", "atari7800"],
        "atarilynx": ["atari lynx", "atari-lynx", "atari_lynx", "lynx", "atarilynx"],
        "atarijaguar": ["atari jaguar", "atari-jaguar", "atari_jaguar", "jaguar", "atarijaguar"],
        
        # Commodore variants
        "amiga": ["commodore amiga", "amiga", "amiga500", "amiga1200", "amiga4000", "amiga1000", "amiga600", "amiga1200", "amiga4000"],
        "c64": ["commodore 64", "commodore64", "c64", "cbm64", "commodore-64"],
        "c128": ["commodore 128", "c128", "commodore128"],
        "vic20": ["commodore vic-20", "vic20", "vic-20"],
        "pet": ["commodore pet", "pet", "commodorepet"],
        
        # Nintendo variants
        "nes": ["nintendo", "nintendo entertainment system", "famicom", "nes"],
        "snes": ["super nintendo", "super nintendo entertainment system", "snes", "sfc", "nintendo super system"],
        "n64": ["nintendo 64", "n64", "nintendo64"],
        "gamecube": ["game cube", "game-cube", "game_cube", "gc", "gamecube"],
        "wii": ["nintendo wii", "wii"],
        "ds": ["nintendo ds", "nintendo-ds", "nds", "ds"],
        "switch": ["nintendo switch", "switch"],
        "3ds": ["nintendo 3ds", "3ds"],
        "gb": ["gameboy", "game boy", "game-boy", "gb", "gameboj"],
        "gba": ["gameboy advance", "game boy advance", "gba", "gba"],
        "gbc": ["gameboy color", "game boy color", "gbc", "gbcolor"],
        
        # Sega variants
        "mastersystem": ["master system", "master-system", "master_system", "sms", "segamastersystem"],
        "genesis": ["sega genesis", "genesis", "megadrive", "mega drive", "mega-drive", "md", "segagenesis"],
        "gamegear": ["game gear", "game-gear", "game_gear", "gg", "segagamegear"],
        "saturn": ["sega saturn", "saturn", "segasaturn"],
        "dreamcast": ["sega dreamcast", "dreamcast", "segadreamcast"],
        
        # Sony PlayStation variants
        "psx": ["playstation", "ps1", "psone", "psx", "playstation1", "sony playstation"],
        "ps2": ["playstation 2", "playstation2", "ps2", "playstation-2", "playstation_2"],
        "ps3": ["playstation 3", "playstation3", "ps3", "playstation-3", "playstation_3"],
        "psp": ["playstation portable", "psp"],
        
        # Microsoft variants
        "xbox": ["xbox360", "xbox 360", "xbox-360", "xbox360"],
        "xboxone": ["xbox one", "xbox-one", "xbox_one", "xbox1", "xboxone"],
        "xboxseries": ["xbox series", "xboxseries"],
        
        # NEC variants
        "pcengine": ["pc engine", "pc-engine", "pc_engine", "pce", "turbografx16", "turbografx-16", "tg16"],
        "supergrafx": ["super grafx", "super-grafx", "super_grafx", "sgfx"],
        "pc88": ["pc-88", "pc88", "pc-8801", "pc8801"],
        "pc98": ["pc-98", "pc98", "pc-9801", "pc9801"],
        "pcfx": ["pc fx", "pc-fx", "pcfx"],
        
        # SNK variants
        "neogeo": ["neo geo", "neo-geo", "neogeo", "neogeo"],
        "neogeocd": ["neo geo cd", "neogeocd", "neogeocd"],
        
        # Other home computers
        "apple2": ["apple ][", "apple2", "apple ii", "apple-2", "apple2e", "apple //e"],
        "adam": ["adam", "coleco adam"],
        "aquarius": ["aquarius", "mattel aquarius"],
        "channelf": ["channel f", "channelf", "fairchild channel f", "fairchild"],
        "colecovision": ["coleco", "colecovision", "coleco vision"],
        "creativision": ["creativision", "apf", "apf m1000"],
        "dragon32": ["dragon32", "dragon 32", "dragon32/64", "dragon"],
        "fmtowns": ["fm towns", "fmtowns", "fm-towns"],
        "intellivision": ["intellivision", "intv"],
        "vectrex": ["vectrex", "vector"],
        "x68000": ["x68000", "x6800", "x68k"],
        
        # Handhelds
        "ngp": ["neo geo pocket", "ngp"],
        "ngpc": ["neo geo pocket color", "ngpc"],
        "wswan": ["wonderswan", "wonder swan", "wonderswan", "wswan"],
        "wswanc": ["wonderswan color", "wonderswan color", "wswanc"],
        "pokemini": ["pokemini", "pokemon mini"],
        "virtualboy": ["virtual boy", "virtualboy", "vb"],
        
        # Arcade
        "mame": ["mame", "mame-libretro"],
        "fbneo": ["fbneo", "final burn neo", "fighting"],
        
        # 3DO and other CD-based
        "3do": ["3do", "3do interactive multiplayer"],
        "cdi": ["cdi", "philips cdi"],
        "segacd": ["sega cd", "segacd", "mega-cd"],
        
        # Other platforms
        "arduboy": ["arduboy"],
        "gw": ["game and watch", "game&watch", "gw"],
        "lutro": ["lutro", "love"],
        "prboom": ["prboom", "doom"],
        "vecx": ["vecx", "vectrex"],
        "scummvm": ["scummvm", "scumm"],
        "stella": ["stella", "atari2600"],
        "prosystem": ["prosystem", "atari5200"],
        "snes9x": ["snes9x", "snes"],
        "fceumm": ["fceumm", "nes"],
        "gambatte": ["gambatte", "gb"],
        "mgba": ["mgba", "gba"],
        "quicknes": ["quicknes", "nes"],
        "beetle_psx": ["beetle_psx", "psx"],
        "parallel_n64": ["parallel_n64", "n64"],
        "pcsx_rearmed": ["pcsx_rearmed", "psx"],
        "mednafen_snes": ["mednafen_snes", "snes"],
        "mednafen_pce": ["mednafen_pce", "pcengine"],
        "mednafen_pcfx": ["mednafen_pcfx", "pcfx"],
        "mednafen_saturn": ["mednafen_saturn", "saturn"],
        "kronos": ["kronos", "saturn"],
        "mednafen_psx": ["mednafen_psx", "psx"],
        "fbalpha2012_cps1": ["fbalpha2012_cps1", "neogeo"],
        "fbalpha2012_cps2": ["fbalpha2012_cps2", "neogeo"],
        "fbalpha2012_cps3": ["fbalpha2012_cps3", "neogeo"],
        "mame2003_plus": ["mame2003_plus", "mame"],
        "mame2010": ["mame2010", "mame"],
        "mame2016": ["mame2016", "mame"],
        "desmume": ["desmume", "ds"],
        "melonds": ["melonds", "ds"],
        "citra": ["citra", "3ds"],
        "ppsspp": ["ppsspp", "psp"],
        "duckstation": ["duckstation", "psx"],
        "pcsx2": ["pcsx2", "ps2"],
        "rpcs3": ["rpcs3", "ps3"],
        "xemu": ["xemu", "xbox"],
        "xenia": ["xenia", "xbox"],
        "cemu": ["cemu", "wiiu"],
        "dolphin": ["dolphin", "gamecube", "wii"],
        "yuzu": ["yuzu", "switch"],
        "ryujinx": ["ryujinx", "switch"],
        "suyu": ["suyu", "switch"],
        "lime3ds": ["lime3ds", "3ds"],
        "panda3ds": ["panda3ds", "3ds"],
        "ares": ["ares", "multi"],
        "mu": ["mu", "multi"],
        "play": ["play", "ps2"],
        "bizhawk": ["bizhawk", "multi"],
        "raine": ["raine", "mame"],
        "mame4all": ["mame4all", "mame"],
        "xmame": ["xmame", "mame"],
        "advancecash": ["advancecash", "multi"],
        "devilutionx": ["devilutionx", "diablo"],
        "eduke32": ["eduke32", "duke3d"],
        "gemrb": ["gemrb", "baldursgate"],
        "gme": ["gme", "game-music-emu"],
        "gpsp": ["gpsp", "gba"],
        "handy": ["handy", "lynx"],
        "hatari": ["hatari", "atarist"],
        "hatarib": ["hatarib", "atarist"],
        "imageviewer": ["imageviewer", "image"],
        "mupen64plus": ["mupen64plus", "n64"],
        "nekop2": ["nekop2", "neogeocd"],
        "nestopia": ["nestopia", "nes"],
        "np2kai": ["np2kai", "pc98"],
        "nxengine": ["nxengine", "cavestory"],
        "o2em": ["o2em", "intellivision"],
        "opera": ["opera", "3do"],
        "pcsx1": ["pcsx1", "psx"],
        "pocketcpc": ["pocketcpc", "cpc"],
        "potator": ["potator", "gamecom"],
        "quasi88": ["quasi88", "pc88"],
        "race": ["race", "enhanced"],
        "redbook": ["redbook", "cd", "audio"],
        "reicast": ["reicast", "dreamcast"],
        "retro8": ["retro8", "basic8"],
        "sameduck": ["sameduck", "n64"],
        "same_cdi": ["same_cdi", "cdi"],
        "simcp": ["simcp", "cp"],
        "smsplus": ["smsplus", "mastersystem"],
        "stonesoup": ["stonesoup", "brogue"],
        "swanstation": ["swanstation", "psx"],
        "tempgba": ["tempgba", "gba"],
        "tyrquake": ["tyrquake", "quake"],
        "uae": ["uae", "amiga"],
        "vaporspec": ["vaporspec", "spec256", "z81-spec256", "z81 spec256", "z81spec256"],
        "vecx": ["vecx", "vectrex"],
        "virtualjaguar": ["virtualjaguar", "jaguar"],
        "vitaquake2": ["vitaquake2", "quake2"],
        "x1": ["x1", "xone"],
        "yabasanshiro": ["yabasanshiro", "saturn"],
        "yabause": ["yabause", "saturn"]
    }
    
    # Core name aliases for backward compatibility
    CORE_ALIASES = {
        "uae": "puae",
        "stella2014": "stella",
        "atari800_libretro": "atari800",
        "vice_x64_libretro": "vice_x64",
        "mess": "mame",
    }
    
    def normalize_platform_name(self, platform_name: str) -> str:
        """Normalize platform name using fuzzy matching with aliases
        
        Args:
            platform_name: The platform name to normalize
            
        Returns:
            The normalized platform name or the original if no match found
        """
        platform_lower = platform_name.lower().strip()
        
        # Check if the platform name matches any of our standard platform keys directly (case-insensitive)
        for key in self.PLATFORM_CORE_MAPPING.keys():
            if key.lower() == platform_lower:
                return key  # Return the original case key
                
        # Check if the platform name matches any of the PLATFORM_ALIASES keys directly
        for key in self.PLATFORM_ALIASES.keys():
            if key.lower() == platform_lower:
                # If this alias key matches a PLATFORM_CORE_MAPPING key, return that
                for core_key in self.PLATFORM_CORE_MAPPING.keys():
                    if core_key.lower() == key.lower():
                        return core_key
                # If the alias key itself appears in any PLATFORM_CORE_MAPPING key's aliases, return that PLATFORM_CORE_MAPPING key
                for standard_name, aliases in self.PLATFORM_ALIASES.items():
                    if key.lower() == standard_name.lower():
                        for core_key in self.PLATFORM_CORE_MAPPING.keys():
                            if core_key.lower() in [a.lower() for a in aliases]:
                                return core_key
                return key  # Return the original case key
        
        # Check aliases to find a match
        for standard_name, aliases in self.PLATFORM_ALIASES.items():
            if platform_lower == standard_name.lower():
                # If the standard name matches a PLATFORM_CORE_MAPPING key, return that
                for key in self.PLATFORM_CORE_MAPPING.keys():
                    if key.lower() == standard_name.lower():
                        return key
                # If the standard name itself appears in any PLATFORM_CORE_MAPPING key's aliases, return that PLATFORM_CORE_MAPPING key
                for key in self.PLATFORM_CORE_MAPPING.keys():
                    if key.lower() in [a.lower() for a in aliases]:
                        return key
                return standard_name  # Return the standard name from aliases
            for alias in aliases:
                if platform_lower == alias.lower():
                    # If the standard name from aliases matches a PLATFORM_CORE_MAPPING key, return that
                    for key in self.PLATFORM_CORE_MAPPING.keys():
                        if key.lower() == standard_name.lower():
                            return key
                    # If the standard name itself appears in any PLATFORM_CORE_MAPPING key's aliases, return that PLATFORM_CORE_MAPPING key
                    for key in self.PLATFORM_CORE_MAPPING.keys():
                        if key.lower() in [a.lower() for a in aliases]:
                            return key
                    # Otherwise return the standard name from aliases
                    return standard_name
        
        # If no exact match found, return the original name
        return platform_name

    def __init__(self, roms_dir: Path, cores_dir: Path = None): #vers 3
        """Initialize platform scanner with core detection
        
        Args:
            roms_dir: Directory containing ROMs
            cores_dir: Directory containing cores (optional, defaults to ./cores)
        """
        self.roms_dir = Path(roms_dir)
        self.platforms = {}
        self.core_scanner = SystemCoreScanner(cores_dir or Path("./cores"))
        self.bios_manager = BiosManager()
        
        # Get available cores
        self.available_cores = self.core_scanner.get_installed_cores()
        print(f"Available cores: {list(self.available_cores.keys())}")
        
    def _is_system_file(self, name: str) -> bool: #vers 1
        """Check if file/folder should be ignored
        
        Args:
            name: File or folder name
            
        Returns:
            True if should be ignored
        """
        name_lower = name.lower()
        
        # Check exact matches
        if name in self.IGNORE_PATTERNS:
            return True
            
        # Check if name starts with ignore pattern
        for pattern in self.IGNORE_PATTERNS:
            if name_lower.startswith(pattern.lower()):
                return True
                
        # Ignore files starting with dot
        if name.startswith('.'):
            return True
            
        # Ignore .zip BIOS files
        if 'bios' in name_lower and name_lower.endswith('.zip'):
            return True
            
        return False
    
    def update_platform_config_with_cores(self, platform_config: Dict) -> Dict:
        """Update platform configuration with available cores
        
        Args:
            platform_config: Original platform configuration
            
        Returns:
            Updated platform configuration with available cores
        """
        # Make a copy of the original config
        updated_config = platform_config.copy()
        
        # Get the platform name for core mapping
        platform_name = updated_config.get("name", "")
        
        # Normalize the platform name using fuzzy matching
        normalized_platform_name = self.normalize_platform_name(platform_name)
        
        # Find available cores for this platform
        available_platform_cores = []
        
        # Check platform-specific core mappings using normalized name
        if normalized_platform_name in self.PLATFORM_CORE_MAPPING:
            for core_candidate in self.PLATFORM_CORE_MAPPING[normalized_platform_name]:
                # Check if core exists (try both original and alias)
                actual_core = self.CORE_ALIASES.get(core_candidate, core_candidate)
                if actual_core in self.available_cores:
                    available_platform_cores.append(actual_core)
                elif core_candidate in self.available_cores:
                    available_platform_cores.append(core_candidate)
        # Also check the original name in case normalization didn't work
        elif platform_name in self.PLATFORM_CORE_MAPPING:
            for core_candidate in self.PLATFORM_CORE_MAPPING[platform_name]:
                # Check if core exists (try both original and alias)
                actual_core = self.CORE_ALIASES.get(core_candidate, core_candidate)
                if actual_core in self.available_cores:
                    available_platform_cores.append(actual_core)
                elif core_candidate in self.available_cores:
                    available_platform_cores.append(core_candidate)
        
        # If no specific mapping found, try to determine from existing cores
        if not available_platform_cores and "cores" in updated_config:
            for core_candidate in updated_config["cores"]:
                actual_core = self.CORE_ALIASES.get(core_candidate, core_candidate)
                if actual_core in self.available_cores:
                    available_platform_cores.append(actual_core)
                elif core_candidate in self.available_cores:
                    available_platform_cores.append(core_candidate)
        
        # Update the cores list with only available ones
        updated_config["cores"] = available_platform_cores
        updated_config["core_available"] = len(available_platform_cores) > 0
        
        # Add BIOS information
        bios_info = self.bios_manager.get_platform_bios_info(platform_name)
        updated_config["bios_complete"] = bios_info["bios_complete"]
        updated_config["missing_bios"] = bios_info["missing_files"]
        updated_config["bios_required"] = len(bios_info["required_files"]) > 0
        
        return updated_config
    
    def scan_platforms(self) -> Dict[str, Dict]: #vers 3
        """Scan ROM directory and discover platforms - handles spaces
        Integrates with dynamic core detection and BIOS management
        """
        if not self.roms_dir.exists():
            print(f"ROM directory not found: {self.roms_dir}")
            return {}
            
        print(f"Scanning for platforms in: {self.roms_dir}")
        print("=" * 60)
        
        platforms = {}
        
        # Scan all subdirectories
        for item in self.roms_dir.iterdir():
            # Skip non-directories
            if not item.is_dir():
                continue
            
            # Skip system files/folders    
            if self._is_system_file(item.name):
                print(f"Skipping system folder: {item.name}")
                continue
                
            platform_name = item.name
            
            # Count ROMs
            rom_count = self._count_roms_in_directory(item)
            
            if rom_count == 0:
                print(f"Skipping {platform_name} (no ROM files found)")
                continue
                
            # Detect file extensions
            extensions = self._detect_file_extensions(item)
            
            # Guess platform type
            platform_type = self._guess_platform_type(platform_name, extensions)
            
            # Create basic platform config
            basic_config = {
                "name": platform_name,
                "path": str(item),
                "rom_count": rom_count,
                "extensions": list(extensions),
                "type": platform_type,
                # Default values that will be updated with dynamic detection
                "cores": [],
                "core_available": False,
                "bios_required": False,
                "bios_complete": False,
                "missing_bios": [],
            }
            
            # Update with dynamic core detection and BIOS info
            platform_config = self.update_platform_config_with_cores(basic_config)
            
            # Only add platform if it has available cores (to avoid "No core available" messages)
            if platform_config["core_available"]:
                platforms[platform_name] = platform_config
                print(f"✓ {platform_name}: {rom_count} ROMs, cores: {platform_config['cores']}, BIOS: {'✓' if platform_config['bios_complete'] else '✗' if platform_config['bios_required'] else 'N/A'}")
            else:
                print(f"✗ {platform_name}: No available core found for this platform")
                
        print(f"\nLoaded {len(platforms)} platform(s): {', '.join(platforms.keys())}")
        
        self.platforms = platforms
        return platforms
    
    def get_platforms(self) -> List[str]: #vers 1
        """Get list of platform names"""
        return list(self.platforms.keys())
    
    def get_platform_info(self, platform_name: str) -> Optional[Dict]: #vers 1
        """Get info for specific platform"""
        return self.platforms.get(platform_name)
    
    def _count_roms_in_directory(self, directory: Path) -> int: #vers 3
        """Count ROM files in directory - ignore system files, include archives"""
        count = 0
        rom_extensions = {
            '.adf', '.ipf', '.dms',  # Amiga
            '.st', '.stx',  # Atari ST
            '.a26', '.a52', '.a78',  # Atari consoles
            '.xex', '.atr', '.cas',  # Atari 8-bit
            '.tap', '.tzx', '.sna', '.z80',  # Spectrum
            '.dsk', '.cdt',  # Amstrad
            '.d64', '.t64', '.crt', '.prg',  # C64
            '.d81',  # C128
            '.rom', '.mx1', '.mx2',  # MSX
            '.nes', '.sfc', '.smc', '.gba',  # Nintendo
            '.gen', '.md', '.smd',  # Sega
            '.cue', '.bin', '.iso',  # Disc formats
            '.zip', '.7z', '.rar',  # Compressed archives
        }
        
        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue
                
            # Skip system files
            if self._is_system_file(file_path.name):
                continue
                
            if file_path.suffix.lower() in rom_extensions:
                count += 1
                    
        return count
        
    def _detect_file_extensions(self, directory: Path) -> Set[str]: #vers 2
        """Detect all ROM file extensions - ignore system files"""
        extensions = set()
        
        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue
                
            # Skip system files
            if self._is_system_file(file_path.name):
                continue
                
            ext = file_path.suffix.lower()
            if ext and ext != '.folder':
                extensions.add(ext)
                    
        return extensions
        
    def _guess_platform_type(self, platform_name: str, extensions: Set[str]) -> str: #vers 1
        """Guess platform type from name and extensions"""
        matches = {}
        
        for ext in extensions:
            if ext in self.EXTENSION_HINTS:
                for platform_type in self.EXTENSION_HINTS[ext]:
                    if platform_type not in matches:
                        matches[platform_type] = 0
                    matches[platform_type] += 1
                    
        if matches:
            best_match = max(matches.items(), key=lambda x: x[1])[0]
            
            if best_match.lower() in platform_name.lower() or \
               platform_name.lower() in best_match.lower():
                return best_match
                
        # Normalize the platform name using fuzzy matching
        normalized_name = self.normalize_platform_name(platform_name)
        if normalized_name != platform_name:
            return normalized_name
                
        return platform_name
