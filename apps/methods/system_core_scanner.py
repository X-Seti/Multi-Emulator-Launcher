#!/usr/bin/env python3
#this belongs in apps/methods/system_core_scanner.py - Version: 1
# X-Seti - November23 2025 - Multi-Emulator Launcher - System Core Scanner

"""
System Core Scanner
Scans common system library paths for installed libretro cores
Works with package managers: apt, dnf, pacman, yay, flatpak
"""

from pathlib import Path
from typing import List, Dict, Set
import subprocess

##Methods list -
# get_all_cores
# get_installed_cores
# scan_flatpak_cores
# scan_system_cores

##class SystemCoreScanner -

class SystemCoreScanner: #vers 1
    """Scans system for installed libretro cores"""
    
    # Common system library paths where package managers install cores
    SYSTEM_LIB_PATHS = [
        # Arch/Manjaro (pacman/yay)
        Path("/usr/lib/libretro"),
        Path("/usr/lib64/libretro"),
        
        # Debian/Ubuntu (apt)
        Path("/usr/lib/x86_64-linux-gnu/libretro"),
        Path("/usr/lib/i386-linux-gnu/libretro"),
        Path("/usr/lib/aarch64-linux-gnu/libretro"),
        Path("/usr/lib/arm-linux-gnueabihf/libretro"),
        
        # Fedora/RHEL (dnf)
        Path("/usr/lib64/libretro"),
        Path("/usr/lib/libretro"),
        
        # OpenSUSE
        Path("/usr/lib64/libretro"),
        
        # Flatpak
        Path.home() / ".var/app/org.libretro.RetroArch/config/retroarch/cores",
        Path("/var/lib/flatpak/app/org.libretro.RetroArch/current/active/files/lib/libretro"),
        
        # Snap
        Path("/snap/retroarch/current/usr/lib/libretro"),
        
        # User-installed RetroArch
        Path.home() / ".config/retroarch/cores",
        Path.home() / ".local/share/libretro/cores",
    ]
    
    def __init__(self, local_cores_dir: Path = None): #vers 1
        """Initialize system core scanner
        
        Args:
            local_cores_dir: Local cores directory (e.g., ./cores)
        """
        self.local_cores_dir = Path(local_cores_dir) if local_cores_dir else None
        self.cache = {}  # Cache scanned results
    
    def scan_system_cores(self) -> Dict[str, Path]: #vers 1
        """Scan system library paths for cores
        
        Returns:
            Dict of core_name -> core_path
        """
        cores = {}
        
        for lib_path in self.SYSTEM_LIB_PATHS:
            if not lib_path.exists():
                continue
            
            print(f"Scanning: {lib_path}")
            
            # Find all libretro cores
            for ext in ['.so', '.dll', '.dylib']:
                for core_file in lib_path.glob(f"*_libretro{ext}"):
                    core_name = core_file.stem.replace("_libretro", "")
                    
                    # Prefer local cores over system cores
                    if core_name not in cores:
                        cores[core_name] = core_file
                        print(f"  Found: {core_name}")
        
        return cores
    
    def scan_flatpak_cores(self) -> Dict[str, Path]: #vers 1
        """Scan Flatpak RetroArch cores
        
        Returns:
            Dict of core_name -> core_path
        """
        cores = {}
        
        # Check if flatpak is installed
        try:
            result = subprocess.run(
                ["flatpak", "list", "--app"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return cores
            
            # Check if RetroArch flatpak is installed
            if "org.libretro.RetroArch" not in result.stdout:
                return cores
            
            # Scan flatpak core directory
            flatpak_cores = Path.home() / ".var/app/org.libretro.RetroArch/config/retroarch/cores"
            
            if flatpak_cores.exists():
                print(f"Scanning Flatpak: {flatpak_cores}")
                
                for core_file in flatpak_cores.glob("*_libretro.so"):
                    core_name = core_file.stem.replace("_libretro", "")
                    cores[core_name] = core_file
                    print(f"  Found: {core_name}")
        
        except Exception as e:
            print(f"Error scanning Flatpak: {e}")
        
        return cores
    
    def get_installed_cores(self) -> Dict[str, Path]: #vers 1
        """Get all installed cores (system + local + flatpak)
        
        Returns:
            Dict of core_name -> core_path (deduplicated)
        """
        all_cores = {}
        
        # 1. Scan system paths
        system_cores = self.scan_system_cores()
        all_cores.update(system_cores)
        
        # 2. Scan Flatpak
        flatpak_cores = self.scan_flatpak_cores()
        all_cores.update(flatpak_cores)
        
        # 3. Scan local cores directory (highest priority)
        if self.local_cores_dir and self.local_cores_dir.exists():
            print(f"Scanning local: {self.local_cores_dir}")
            
            for ext in ['.so', '.dll', '.dylib']:
                for core_file in self.local_cores_dir.glob(f"*_libretro{ext}"):
                    core_name = core_file.stem.replace("_libretro", "")
                    all_cores[core_name] = core_file  # Override system cores
                    print(f"  Found: {core_name}")
        
        return all_cores
    
    def get_all_cores(self) -> List[tuple]: #vers 1
        """Get all cores with source information
        
        Returns:
            List of (core_name, core_path, source) tuples
            source can be: 'local', 'system', 'flatpak'
        """
        cores_with_source = []
        
        # System cores
        system_cores = self.scan_system_cores()
        for name, path in system_cores.items():
            cores_with_source.append((name, path, 'system'))
        
        # Flatpak cores
        flatpak_cores = self.scan_flatpak_cores()
        for name, path in flatpak_cores.items():
            # Check if not already in system
            if name not in system_cores:
                cores_with_source.append((name, path, 'flatpak'))
        
        # Local cores (override)
        if self.local_cores_dir and self.local_cores_dir.exists():
            for ext in ['.so', '.dll', '.dylib']:
                for core_file in self.local_cores_dir.glob(f"*_libretro{ext}"):
                    core_name = core_file.stem.replace("_libretro", "")
                    
                    # Remove system/flatpak version if exists
                    cores_with_source = [
                        (n, p, s) for n, p, s in cores_with_source if n != core_name
                    ]
                    
                    cores_with_source.append((core_name, core_file, 'local'))
        
        # Sort by name
        cores_with_source.sort(key=lambda x: x[0].lower())
        
        return cores_with_source


def detect_package_manager() -> str: #vers 1
    """Detect which package manager is installed
    
    Returns:
        Package manager name or 'unknown'
    """
    managers = {
        'pacman': 'Arch/Manjaro',
        'yay': 'Arch/Manjaro (AUR)',
        'apt': 'Debian/Ubuntu',
        'dnf': 'Fedora/RHEL',
        'zypper': 'OpenSUSE',
        'flatpak': 'Flatpak',
    }
    
    for cmd, distro in managers.items():
        try:
            result = subprocess.run(
                ['which', cmd],
                capture_output=True,
                timeout=1
            )
            if result.returncode == 0:
                return f"{cmd} ({distro})"
        except:
            continue
    
    return 'unknown'


def list_libretro_packages() -> List[str]: #vers 1
    """List available libretro packages in package manager
    
    Returns:
        List of package names
    """
    packages = []
    
    # Try pacman
    try:
        result = subprocess.run(
            ['pacman', '-Ss', 'libretro'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Parse pacman output
            for line in result.stdout.split('\n'):
                if 'libretro' in line and not line.startswith(' '):
                    pkg_name = line.split()[0].split('/')[1] if '/' in line else line.split()[0]
                    packages.append(pkg_name)
            return packages
    except:
        pass
    
    # Try apt
    try:
        result = subprocess.run(
            ['apt', 'search', 'libretro'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'libretro' in line and line.startswith('libretro-'):
                    pkg_name = line.split('/')[0]
                    packages.append(pkg_name)
            return packages
    except:
        pass
    
    # Try dnf
    try:
        result = subprocess.run(
            ['dnf', 'search', 'libretro'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'libretro' in line and not line.startswith(' '):
                    pkg_name = line.split('.')[0]
                    packages.append(pkg_name)
            return packages
    except:
        pass
    
    return packages


# CLI testing
if __name__ == "__main__":
    print("System Core Scanner")
    print("=" * 70)
    
    # Detect package manager
    pm = detect_package_manager()
    print(f"\nPackage Manager: {pm}")
    
    # Scan for cores
    scanner = SystemCoreScanner(Path("./cores"))
    
    print("\n" + "=" * 70)
    print("Scanning for installed cores...")
    print("=" * 70 + "\n")
    
    cores = scanner.get_all_cores()
    
    if cores:
        print(f"\nFound {len(cores)} core(s):\n")
        
        # Group by source
        by_source = {'local': [], 'system': [], 'flatpak': []}
        for name, path, source in cores:
            by_source[source].append((name, path))
        
        for source in ['local', 'system', 'flatpak']:
            if by_source[source]:
                print(f"\n{source.upper()} CORES ({len(by_source[source])}):")
                print("-" * 70)
                for name, path in by_source[source]:
                    size_kb = path.stat().st_size / 1024
                    print(f"  {name:30} {size_kb:>8.1f} KB  {path}")
    else:
        print("No cores found!")
        print("\nTried searching in:")
        for path in SystemCoreScanner.SYSTEM_LIB_PATHS:
            print(f"  {path}")
    
    # List available packages
    print("\n" + "=" * 70)
    print("Available libretro packages:")
    print("=" * 70)
    
    packages = list_libretro_packages()
    if packages:
        print(f"\nFound {len(packages)} package(s):\n")
        for pkg in packages[:20]:  # Show first 20
            print(f"  {pkg}")
        if len(packages) > 20:
            print(f"  ... and {len(packages) - 20} more")
    else:
        print("\nNo libretro packages found in package manager")
