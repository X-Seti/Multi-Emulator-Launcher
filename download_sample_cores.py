#!/usr/bin/env python3
# Download sample cores for testing

import urllib.request
import os
from pathlib import Path

# List of common cores to download for testing
CORES_TO_DOWNLOAD = [
    "stella_libretro.so",    # Atari 2600
    "atari800_libretro.so",  # Atari 800/5200
    "hatari_libretro.so",    # Atari ST
    "puae_libretro.so",      # Amiga
    "cap32_libretro.so",     # Amstrad CPC
    "mame_libretro.so",      # MAME/Acorn Electron/BBC Micro
    "fuse_libretro.so",      # ZX Spectrum
    "vice_x64_libretro.so",  # C64
    "fmsx_libretro.so",      # MSX
    "prosystem_libretro.so", # Atari 7800
]

def download_core(core_name):
    """Download a single core from RetroArch buildbot"""
    # Note: In a real scenario, we would download from actual RetroArch servers
    # For this example, we'll create dummy files to simulate the presence of cores
    cores_dir = Path("cores")
    cores_dir.mkdir(exist_ok=True)
    
    core_path = cores_dir / core_name
    # Create a dummy file to simulate the core
    with open(core_path, 'wb') as f:
        f.write(b"")  # Empty file to simulate core presence
    
    print(f"Created dummy core: {core_name}")

def main():
    print("Creating dummy core files for testing...")
    for core in CORES_TO_DOWNLOAD:
        download_core(core)
    
    print("\nDone! Cores directory now has sample files.")
    print(f"Total cores created: {len(CORES_TO_DOWNLOAD)}")

if __name__ == "__main__":
    main()