#!/usr/bin/env python3
# Core Diagnostic - Check installed cores vs database

from pathlib import Path

# Check cores directory
cores_dir = Path("./cores")

if not cores_dir.exists():
    print(f"ERROR: cores directory not found at {cores_dir.absolute()}")
    exit(1)

# List all cores
core_files = list(cores_dir.glob("*.so")) + list(cores_dir.glob("*.dll")) + list(cores_dir.glob("*.dylib"))

print(f"Found {len(core_files)} core(s) in {cores_dir}:")
print("=" * 70)

for core in sorted(core_files):
    print(f"  {core.name}")

print("\n" + "=" * 70)

# Check for Atari cores specifically
print("\nAtari cores:")
atari_cores = [c for c in core_files if 'atari' in c.name.lower()]
if atari_cores:
    for core in atari_cores:
        print(f"  ✓ {core.name}")
else:
    print("  ✗ No Atari cores found")

# Check naming format
print("\nCore naming analysis:")
with_libretro = [c for c in core_files if '_libretro' in c.name]
without_libretro = [c for c in core_files if '_libretro' not in c.name]

print(f"  Cores WITH '_libretro' suffix: {len(with_libretro)}")
print(f"  Cores WITHOUT '_libretro' suffix: {len(without_libretro)}")

if without_libretro:
    print(f"\n  ⚠️ WARNING: {len(without_libretro)} cores missing '_libretro' suffix!")
    print("  These cores won't be found by CoreLauncher.")
    print("\n  First 5 examples:")
    for core in without_libretro[:5]:
        print(f"    {core.name}")
        expected = core.stem + "_libretro" + core.suffix
        print(f"      Should be: {expected}")

print("\n" + "=" * 70)

# Test get_core_path logic
print("\nTesting get_core_path() logic for 'atari800':")

def get_core_path(core_name: str):
    """Simulates CoreLauncher.get_core_path()"""
    for ext in ['.so', '.dll', '.dylib']:
        core_file = cores_dir / f"{core_name}_libretro{ext}"
        if core_file.exists():
            return core_file
    return None

result = get_core_path("atari800")
if result:
    print(f"  ✓ Found: {result}")
else:
    print(f"  ✗ NOT FOUND: atari800_libretro.so")
    
    # Check if it exists without suffix
    alt_path = cores_dir / "atari800.so"
    if alt_path.exists():
        print(f"  ⚠️ But found: {alt_path.name}")
        print(f"  SOLUTION: Rename to atari800_libretro.so")

print("\n" + "=" * 70)
print("\nRECOMMENDED ACTION:")
print("If cores are missing '_libretro' suffix:")
print("  Run: python fix_core_names.py")
print("  This will rename all cores to include '_libretro'")
