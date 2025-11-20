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
