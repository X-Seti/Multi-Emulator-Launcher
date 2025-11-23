#!/usr/bin/env python3
# Fix Core Names - Add _libretro suffix if missing

from pathlib import Path
import shutil

cores_dir = Path("./cores")

if not cores_dir.exists():
    print(f"ERROR: cores directory not found")
    exit(1)

# Find cores without _libretro suffix
core_files = list(cores_dir.glob("*.so")) + list(cores_dir.glob("*.dll")) + list(cores_dir.glob("*.dylib"))
to_rename = [c for c in core_files if '_libretro' not in c.name]

if not to_rename:
    print("✓ All cores already have '_libretro' suffix")
    exit(0)

print(f"Found {len(to_rename)} core(s) to rename:")
print("=" * 70)

for core in to_rename:
    new_name = core.stem + "_libretro" + core.suffix
    new_path = core.parent / new_name
    
    print(f"  {core.name}")
    print(f"    → {new_name}")
    
    # Check if target already exists
    if new_path.exists():
        print(f"    ⚠️ SKIP: Target already exists")
        continue
    
    # Rename
    try:
        shutil.move(str(core), str(new_path))
        print(f"    ✓ Renamed")
    except Exception as e:
        print(f"    ✗ ERROR: {e}")

print("\n" + "=" * 70)
print("Done! Run check_cores.py to verify.")
