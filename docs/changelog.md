# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Cover art/box art display
- Favorites system
- Search and filter functionality
- Recently played games list

### Added
- Ribbon toolbars: Platforms, Games, View, Tools. Movable, SVG icons, layout saved in mel_settings.json.
- Menu drop-down button left of Settings: every command, grouped like the ribbons.
- `apps/methods/ribbon_system.py`: RibbonMixin shared by MEL windows.
- Two icons in svg_icon_factory: menu_icon, refresh_icon.
- Ribbon button display modes from the Settings icon option: icons and text (default), icons only, text only.
- Short button labels with longer tooltips; View and Tools ribbons start a second row.
- Right viewport is tabbed: Emulator Display plus closable tool tabs. BIOS Manager and Scan Results open there; Results ribbon button reopens them.
- Ribbon Manager (Tools > Ribbons, or the Menu): reorder buttons, move between ribbons, create/delete ribbons, dividers, hide buttons, custom icons, icon size, presets.

### Fixed
- Platform list keeps its names in every icon mode; the display mode now only styles the ribbon buttons and no longer blanks the left bar.
- Scan Complete was a modal dialog; the scan summary and BIOS list now open as tabs in the right viewport.
- Mojibake emoji text removed from all sources; the garbled bullets in the Scan Complete list are now plain text.
- Theme colours now come from the active theme everywhere; 51 hardcoded hex values removed from emu_launcher_gui.py.
- `_get_theme_colors` never merged the theme palette, so every lookup used a hardcoded set. Now delegates to AppSettings.
- Ribbons follow the theme: button text, hover, pressed and separator colours.
- Saved `icon_display_mode` was ignored at startup (hardcoded icons_and_text); now loaded, so lists and ribbons match.
- Settings dialog crash: emulator display-mode methods lived in the dialog, not MELSettingsManager. Moved to the manager.
- RetroArch artwork never loaded: live `_find_artwork_file` shadowed the version that checked thumbnails. Merged both.
- `apply_table_theme` called missing `apply_all_window_themes`; now calls `_apply_theme`. Hit on every theme change.
- `log_message` wrote to non-existent `self.log`; now prints timestamped lines. Hit by theme dialog debug buttons.
- `_apply_theme` fallback and `_initialize_features` called methods that don't exist. Removed both calls.
- Missing imports for CoreDownloader, CoreLauncher, RomLoader, GameScanner, BiosManager; NameError when GUI built un-injected.

### Removed
- Dead files: `apps/gui/gui_window.py`, `apps/gui/example.py`, `apps/core/svg_icon_methods.py`, `apps/core/CORE_LAUNCHER_ADDITIONS.txt`.
- 19 shadowed duplicate definitions removed from emu_launcher_gui.py, app_settings_system.py, imgfactory_svg_icons.py, App_System_Setting_Svg_icons.py.
- 15 unreachable Img Factory methods in EmuLauncherGUI: dock, tearoff, workshop, window resize, splitter/log styling. -975 lines.

### Changed
- `cc.py` renamed `cc.sh`; it held shell commands, not Python.
- `emu_launcher_gui.py` 5344 → 4101 lines.

## [1.0.0] - 2025-01-XX

### Added
- Initial release
- Multi-platform emulator frontend
- PS4 DualShock 4 controller support with full navigation
- Automatic ROM scanning and platform detection
- ZIP file support with intelligent extraction and caching
- Multi-disk game detection and grouping
- Folder-based game support (e.g., Turrican-II structure)
- BIOS management with verification
- PyQt6 dark theme GUI
- Tab-based platform navigation
- Game list with type indicators (ZIP 📦, Multi-disk 💾, Folder 📁)
- Settings tab with cache management
- Keyboard navigation fallback
- Smart game name cleaning
- RetroArch integration via command line
- Save state directory management
- Platform configurations for:
  - Acorn Electron
  - Amiga (P-UAE core)
  - Amstrad 464/6128/CPC (Caprice32 core)
  - Apple II
  - Atari 2600 (Stella core)
  - Atari 800/8-bit
  - Atari ST (Hatari core)

### Documentation
- Comprehensive README with installation guide
- CONTRIBUTING guide for developers
- QUICKSTART guide for new users
- GIT_SETUP_GUIDE for repository management
- PROJECT_SUMMARY for overview
- Code comments and docstrings

### Technical
- Python 3.8+ support
- Cross-platform compatibility (Linux, macOS, Windows)
- Modular architecture with separate concerns
- JSON-based configuration
- Virtual environment support
- Automated setup script

---

## Version Format

### [MAJOR.MINOR.PATCH]

- **MAJOR**: Incompatible API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes

---

## Future Versions (Planned)

### [1.1.0] - Game Enhancements
- Cover art display from local images
- Game metadata (year, developer, genre)
- Favorites marking system
- Recently played list
- Play time tracking

### [1.2.0] - UI Improvements
- Search functionality
- Filter by genre/year
- Grid view option
- Custom themes
- Screenshot preview

### [1.3.0] - Controller Expansion
- Xbox controller support
- Switch Pro controller support
- Custom button mapping
- Controller profiles

### [2.0.0] - Advanced Features
- Direct libretro core loading (no RetroArch required)
- Built-in save state manager
- Shader selection UI
- Netplay integration
- Cloud save support

---

## Template for New Entries

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature description

### Changed
- Changed feature description

### Fixed
- Bug fix description

### Removed
- Removed feature description
```

---

[Unreleased]: https://github.com/yourusername/multi-emulator-launcher/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/multi-emulator-launcher/releases/tag/v1.0.0
