#!/usr/bin/env python3
#this belongs in apps/methods/rom_extractor.py - Version: 1
# X-Seti - December27 2025 - Multi-Emulator Launcher - ROM Extractor

"""
ROM Extraction Helper
Extracts compressed ROM files (.zip, .7z, .rar) for emulators that can't handle them
"""

import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple

##Methods list -
# extract_if_needed
# is_compressed
# cleanup_extraction

class RomExtractor: #vers 1
    """Handles extraction of compressed ROM files"""
    
    def __init__(self): #vers 1
        """Initialize ROM extractor"""
        self.temp_dir = None
        self.extracted_file = None
    
    @staticmethod
    def is_compressed(file_path: Path) -> bool: #vers 1
        """Check if file is compressed
        
        Args:
            file_path: Path to check
            
        Returns:
            True if compressed format
        """
        compressed_extensions = {'.zip', '.7z', '.rar', '.gz'}
        return file_path.suffix.lower() in compressed_extensions
    
    def extract_if_needed(self, rom_path: Path, emulator_name: str) -> Tuple[Path, bool]: #vers 1
        """Extract ROM if compressed and emulator doesn't support it
        
        Args:
            rom_path: Path to ROM file
            emulator_name: Name of emulator
            
        Returns:
            Tuple of (path_to_use, was_extracted)
        """
        # Emulators that can handle .zip natively
        zip_capable = {
            'retroarch', 'mame', 'mednafen', 'stella',
            'snes9x-gtk', 'snes9x', 'fceux', 'nestopia'
        }
        
        # If not compressed, return as-is
        if not self.is_compressed(rom_path):
            return (rom_path, False)
        
        # If emulator can handle zip, return as-is
        if emulator_name.lower() in zip_capable and rom_path.suffix.lower() == '.zip':
            print(f"✓ {emulator_name} can handle .zip files directly")
            return (rom_path, False)
        
        # Need to extract
        print(f"Extracting {rom_path.name}...")
        
        try:
            # Create temp directory
            self.temp_dir = Path(tempfile.mkdtemp(prefix='mel_rom_'))
            
            # Extract based on format
            if rom_path.suffix.lower() == '.zip':
                self.extracted_file = self._extract_zip(rom_path, self.temp_dir)
            elif rom_path.suffix.lower() == '.7z':
                self.extracted_file = self._extract_7z(rom_path, self.temp_dir)
            elif rom_path.suffix.lower() == '.rar':
                self.extracted_file = self._extract_rar(rom_path, self.temp_dir)
            else:
                print(f"⚠ Unsupported compression format: {rom_path.suffix}")
                return (rom_path, False)
            
            if self.extracted_file:
                print(f"✓ Extracted to: {self.extracted_file}")
                return (self.extracted_file, True)
            else:
                print("⚠ Extraction failed")
                return (rom_path, False)
                
        except Exception as e:
            print(f"Error extracting ROM: {e}")
            self.cleanup_extraction()
            return (rom_path, False)
    
    def _extract_zip(self, zip_path: Path, dest_dir: Path) -> Optional[Path]: #vers 1
        """Extract .zip file
        
        Args:
            zip_path: Path to .zip file
            dest_dir: Destination directory
            
        Returns:
            Path to extracted ROM file
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # Get list of files
                files = zf.namelist()
                
                # Filter out directories and system files
                rom_files = [f for f in files if not f.endswith('/') and not f.startswith('__MACOSX')]
                
                if not rom_files:
                    print("No ROM files found in archive")
                    return None
                
                # Extract first ROM file
                first_rom = rom_files[0]
                zf.extract(first_rom, dest_dir)
                
                return dest_dir / first_rom
                
        except Exception as e:
            print(f"Error extracting .zip: {e}")
            return None
    
    def _extract_7z(self, archive_path: Path, dest_dir: Path) -> Optional[Path]: #vers 1
        """Extract .7z file
        
        Args:
            archive_path: Path to .7z file
            dest_dir: Destination directory
            
        Returns:
            Path to extracted ROM file
        """
        try:
            import py7zr
            
            with py7zr.SevenZipFile(archive_path, 'r') as archive:
                # Get list of files
                files = archive.getnames()
                
                # Filter out directories
                rom_files = [f for f in files if not f.endswith('/')]
                
                if not rom_files:
                    print("No ROM files found in archive")
                    return None
                
                # Extract first ROM file
                first_rom = rom_files[0]
                archive.extract(dest_dir, [first_rom])
                
                return dest_dir / first_rom
                
        except ImportError:
            print("⚠ py7zr not installed. Install with: pip install py7zr --break-system-packages")
            return None
        except Exception as e:
            print(f"Error extracting .7z: {e}")
            return None
    
    def _extract_rar(self, rar_path: Path, dest_dir: Path) -> Optional[Path]: #vers 1
        """Extract .rar file
        
        Args:
            rar_path: Path to .rar file
            dest_dir: Destination directory
            
        Returns:
            Path to extracted ROM file
        """
        try:
            import rarfile
            
            with rarfile.RarFile(rar_path, 'r') as rf:
                # Get list of files
                files = rf.namelist()
                
                # Filter out directories
                rom_files = [f for f in files if not f.endswith('/')]
                
                if not rom_files:
                    print("No ROM files found in archive")
                    return None
                
                # Extract first ROM file
                first_rom = rom_files[0]
                rf.extract(first_rom, dest_dir)
                
                return dest_dir / first_rom
                
        except ImportError:
            print("⚠ rarfile not installed. Install with: pip install rarfile --break-system-packages")
            return None
        except Exception as e:
            print(f"Error extracting .rar: {e}")
            return None
    
    def cleanup_extraction(self): #vers 1
        """Clean up temporary extracted files"""
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                print(f"✓ Cleaned up temp files: {self.temp_dir}")
                self.temp_dir = None
                self.extracted_file = None
            except Exception as e:
                print(f"Error cleaning up temp files: {e}")
