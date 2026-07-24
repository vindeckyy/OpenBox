# OpenBox

**A local-first Linux game library and launcher — the open-source LaunchBox alternative.**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://github.com/vindeckyy/OpenBox)

---

<p align="center">
  <img src="openbox.svg" width="120" alt="OpenBox icon">
</p>

<p align="center">
  Browse, organize, enrich, and launch your entire game collection — native Linux games,<br>
  ROMs, emulators, Steam, Epic, GOG, and everything in between.
</p>

---

## Features

### Library Management
- **Unified library** for native Linux games, ROMs, DOSBox, and emulator titles
- Search across game metadata, platform, genre, collection, developer, and series
- Favorites, recently played, never played, and missing file views
- Editable metadata with per-game descriptions, ratings, and progress tracking
- Automatic play counts, total playtime, and 500-session history
- Custom collections and smart filters (save and recall filter presets)
- Bulk editing across multiple games at once
- "Surprise Me" random picker from your visible library

### Import & Discovery
- **Steam** — installed game import with metadata, artwork, and launch integration
- **Epic, GOG, Amazon** — import through Heroic Games Launcher
- **EA, Ubisoft, Xbox** — import through Lutris
- **MAME & FinalBurn** — DAT/XML-aware full-set imports with merged, split, and non-merged classification
- **Recursive folder import** with automatic ROM platform detection by file extension
- Watch folders with automatic background scanning

### LaunchBox Database
- Official **LaunchBox Games Database** daily sync
- Local matching with selective metadata and media downloads
- Cover art, backgrounds, and gameplay screenshots from the database
- Image-group browsing and bulk media downloads for matched libraries

### Emulators
- **Automatic emulator discovery** — detects installed emulators on PATH
- **One-click Flatpak install** for major emulators (Dolphin, PPSSPP, PCSX2, RPCS3, Cemu, MAME, xemu)
- Per-platform emulator profiles with per-game command overrides
- Commands are tokenized safely without a shell — spaces in paths stay safe

### RetroAchievements
- Account integration with progress tracking and badge display
- Documented ROM hashing for automatic game matching
- Per-game achievement progress with hardcore status
- Common platform auto-matching (NES, SNES, GB, GBA, Genesis, N64, and more)

### Sessions & Saves
- Startup and shutdown screens that follow the launched process
- Pause, resume, stop, and restart running games from the UI
- **Automatic save-location discovery** for Steam Cloud, RetroArch, PCSX2, PPSSPP, RPCS3, Dolphin, and Cemu
- Versioned save backups with file and directory support
- Safe restore with automatic pre-restore safety copy

### Plugins
- Local plugin install, update, disable, and recoverable removal
- Isolated library, before_launch, and after_session hooks
- Plugin runner executes in a sandboxed subprocess with timeout protection

### Themes & Big Box
- CSS themes that import, persist, and apply live
- Per-platform theme mapping
- **Big Box** controller-first fullscreen navigation with keyboard and gamepad support
- Filter-aware browsing, paging, favorites, and launch

### Cloud & Backups
- **Cloud sync** through any mounted folder (Dropbox, Google Drive, Syncthing, etc.)
- JSON backup and restore with automatic pre-restore safety copy
- Library audit with provider-aware duplicate cleanup and missing-file checks

### Packaging & Updates
- **Portable AppImage** with bundled Python, desktop metadata, icon, and zsync auto-update
- Flatpak manifest for sandboxed distribution
- Makefile for standard system install/uninstall
- Desktop integration with icon, categories, and AppStream metainfo
- In-app update checker with SHA-256 verified GitHub release downloads

---

## Quick Start

### AppImage (Recommended)

```bash
chmod +x OpenBox-x86_64.AppImage
./OpenBox-x86_64.AppImage
```

The browser UI opens automatically. Pass `--native` for the compact Tk interface.

### System Install

```bash
sudo make install
openbox              # browser UI
openbox-native       # Tk interface
```

### Flatpak

```bash
flatpak-builder --user --install --force-clean build-dir io.openbox.GameLauncher.yml
flatpak run io.openbox.GameLauncher
```

### Run from Source

```bash
python3 web_app.py    # browser UI
python3 openbox.py    # Tk interface
```

---

## Usage

```bash
./OpenBox-x86_64.AppImage                  # Launch browser UI
./OpenBox-x86_64.AppImage --native        # Launch Tk interface
./OpenBox-x86_64.AppImage --self-test     # Run smoke tests

python3 openbox.py --self-test            # Verify core functionality

# Run the full test suite
python3 test_emulators.py
python3 test_updates.py
python3 test_arcade.py
python3 test_archives.py
python3 test_importers.py
python3 test_metadata.py
python3 test_plugins.py
python3 test_retroachievements.py
python3 test_saves.py
python3 test_sessions.py
python3 test_packaging.py
```

---

## Architecture

```
openbox.py              Tk native interface (compact, fast)
web_app.py              Browser UI with REST API
├── importers.py        Steam, Heroic, Lutris imports
├── arcade.py           MAME/FinalBurn DAT-aware import
├── metadata.py         LaunchBox Games Database sync + media
├── emulators.py        Flatpak install + profile discovery
├── retroachievements.py  Account, hashing, matching, progress
├── saves.py            Save backup/restore for 6+ platforms
├── plugins.py          Plugin install/update/hooks API
├── plugin_runner.py    Sandboxed plugin subprocess runner
├── catalog.py          Related games, bulk edits
├── archives.py         ZIP/7z/RAR safe extraction
├── cloud_sync.py       Mounted-folder stat syncing
└── updates.py          GitHub release AppImage updates
```

**Data lives at:** `~/.local/share/openbox-game-launcher/library.json`

---

## Emulator Profiles

Configure profiles with a line like:

```
SNES = retroarch -L /path/to/snes9x_libretro.so {path}
```

Use `{path}` where the ROM should go. Other tokens: `{name}`, `{app_id}`, `{heroic_app_id}`, `{lutris_id}`, `{rom_name}`.

Supported platforms: NES, SNES, Game Boy, GBA, N64, GameCube, Wii, PlayStation, PS2, PS3, PSP, Wii U, Xbox, Arcade, DOSBox, and more.

---

## Plugin API

Plugins are directories containing `plugin.json` and a Python entry file:

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "entry": "plugin.py",
  "hooks": ["library", "before_launch", "after_session"]
}
```

Each hook receives and returns one JSON-compatible dictionary.

---

## License

OpenBox is licensed under the [GNU Affero General Public License v3.0](LICENSE).

---

<p align="center">
  Built for Linux gamers who want control over their library without cloud dependency.
</p>
