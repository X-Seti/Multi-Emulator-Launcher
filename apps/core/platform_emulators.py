# X-Seti - December27 2025 - Multi-Emulator Launcher - Platform Emulator Mappings
#this belongs in apps/core/platform_emulators.py - Version: 1
"""
Platform to Emulator Mapping
Maps platform/system names to compatible emulators
Supports platform aliases for variant folder names
"""

##Methods list -
# get_emulators_for_platform
# normalize_platform

# Platform aliases - maps variant names to canonical names
PLATFORM_ALIASES = {
    # Amstrad variants
    'Amstrad 464': 'Amstrad CPC',
    'Amstrad 6128': 'Amstrad CPC',
    'CPC 464': 'Amstrad CPC',
    'CPC 6128': 'Amstrad CPC',
    'CPC6128': 'Amstrad CPC',
    
    # Atari 8-bit variants
    'Atari-8-bit': 'Atari 800',
    'Atari 400': 'Atari 800',
    'Atari 800XL': 'Atari 800',
    'Atari 130XE': 'Atari 800',
    
    # Commodore 64 variants
    'Commodore 64': 'C64',
    'C-64': 'C64',
    
    # BBC Micro variants  
    'BBC Model B': 'BBC Micro',
    'BBC B': 'BBC Micro',
}

# Platform to emulators mapping
# Format: 'Platform Name': ['emulator1', 'emulator2', 'core.so']
PLATFORM_EMULATORS = {
    # Amstrad
    'Amstrad CPC': ['cap32', 'caprice32', 'crocods_libretro.so', 'cap32_libretro.so'],
    
    # Atari 8-bit
    'Atari 800': ['atari800', 'atari++', 'atari800_libretro.so'],
    
    # Atari ST
    'Atari ST': ['hatari', 'hatari_libretro.so'],
    'Atari STE': ['hatari', 'hatari_libretro.so'],
    
    # Atari 2600
    'Atari 2600': ['stella', 'stella_libretro.so', 'stella2014_libretro.so'],
    
    # Atari 7800
    'Atari 7800': ['prosystem', 'prosystem_libretro.so', 'mame'],
    
    # Acorn / BBC
    'BBC Micro': ['b2', 'beebem', 'jsbeeb', 'b-em_libretro.so'],
    'Acorn Electron': ['elkulator', 'mame', 'fuse_libretro.so'],
    
    # Commodore
    'C64': ['vice', 'x64', 'x64sc', 'vice_x64_libretro.so', 'vice_x64sc_libretro.so'],
    'Amiga': ['fs-uae', 'amiberry', 'puae_libretro.so', 'uae_libretro.so'],
    
    # PlayStation
    'PlayStation': ['duckstation-qt', 'duckstation', 'pcsx_rearmed_libretro.so', 'swanstation_libretro.so'],
    'PlayStation 2': ['pcsx2', 'pcsx2-qt'],
    'PSP': ['ppsspp', 'ppsspp-qt', 'ppsspp-sdl', 'ppsspp_libretro.so'],
    
    # Nintendo
    'Nintendo 64': ['mupen64plus', 'mupen64plus_next_libretro.so', 'parallel_n64_libretro.so'],
    'SNES': ['snes9x-gtk', 'snes9x', 'snes9x_libretro.so', 'bsnes_libretro.so'],
    'NES': ['fceux', 'nestopia', 'fceumm_libretro.so', 'nestopia_libretro.so'],
    'Game Boy': ['mgba-qt', 'vba', 'mgba_libretro.so', 'gambatte_libretro.so'],
    'Game Boy Advance': ['mgba-qt', 'vba', 'mgba_libretro.so', 'vba_next_libretro.so'],
    'Nintendo DS': ['melonds', 'desmume', 'melonds_libretro.so', 'desmume_libretro.so'],
    'GameCube': ['dolphin-emu', 'dolphin_libretro.so'],
    'Wii': ['dolphin-emu', 'dolphin_libretro.so'],
    '3DS': ['citra', 'citra-qt', 'citra_libretro.so'],
    
    # Sega
    'Sega Genesis': ['blastem', 'gens', 'genesis_plus_gx_libretro.so'],
    'Sega Mega Drive': ['blastem', 'gens', 'genesis_plus_gx_libretro.so'],
    'Sega Master System': ['blastem', 'genesis_plus_gx_libretro.so'],
    'Sega Game Gear': ['genesis_plus_gx_libretro.so'],
    'Sega CD': ['genesis_plus_gx_libretro.so'],
    'Sega Saturn': ['mednafen_saturn_libretro.so', 'yabause_libretro.so'],
    'Dreamcast': ['reicast_libretro.so', 'flycast_libretro.so'],
    
    # Others
    'ZX Spectrum': ['fuse', 'fuse_libretro.so'],
    'MSX': ['bluemsx', 'bluemsx_libretro.so', 'fmsx_libretro.so'],
    'Neo Geo': ['mame', 'fbneo_libretro.so'],
    'Arcade': ['mame', 'fbneo_libretro.so', 'fbalpha_libretro.so'],
}


def normalize_platform(platform_name): #vers 1
    """Normalize platform name to canonical name
    
    Args:
        platform_name: Raw platform name from folder
        
    Returns:
        Canonical platform name
        
    Examples:
        'Amstrad 6128' → 'Amstrad CPC'
        'Atari-8-bit' → 'Atari 800'
    """
    # Try direct alias lookup
    if platform_name in PLATFORM_ALIASES:
        return PLATFORM_ALIASES[platform_name]
    
    # Return as-is if no alias
    return platform_name


def get_emulators_for_platform(platform_name): #vers 1
    """Get list of compatible emulators for platform
    
    Args:
        platform_name: Platform name (will be normalized)
        
    Returns:
        List of emulator names (empty if platform unknown)
        
    Examples:
        'Amstrad 6128' → ['cap32', 'caprice32', ...]
        'BBC Micro' → ['b2', 'beebem', ...]
        'Unknown Platform' → []
    """
    # Normalize platform name
    canonical = normalize_platform(platform_name)
    
    # Look up emulators
    return PLATFORM_EMULATORS.get(canonical, [])


# Example usage
if __name__ == "__main__":
    # Test platform normalization
    test_platforms = [
        'Amstrad 6128',
        'Amstrad 464',
        'Atari-8-bit',
        'BBC Micro',
        'C64',
        'PlayStation',
    ]
    
    print("Platform Normalization Test:")
    print("=" * 60)
    for platform in test_platforms:
        canonical = normalize_platform(platform)
        emulators = get_emulators_for_platform(platform)
        print(f"{platform:20} → {canonical:20} → {emulators}")
