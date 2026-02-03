# Macan Run - Neo Edition

A professional 2D platformer game built with Python and PySide6, featuring manual-coded UI, QPainter rendering, and physics-based gameplay.

© 2026 Macan Angkasa

## Features

- **Pure QPainter Rendering**: All graphics Player, Coin, Powerups, Enemy drawn by code - no image files needed
- **Physics Engine**: Custom gravity, velocity integration, and AABB collision detection
- **Double Jump Mechanic**: Jump twice in the air for advanced movement
- **Smooth Camera**: Lerp-based camera following the player
- **Save System**: Automatic game state persistence to OS-appropriate locations
- **Modular Architecture**: Clean OOP design with separated concerns
- **60 FPS Game Loop**: QTimer-based game loop with delta time integration

## Game Controls

| Key | Action |
|-----|--------|
| **Arrow Keys** or **A/D** | Move left/right |
| **Space** or **W** | Jump (press twice for double jump) |
| **P** | Pause/Resume |
| **ESC** | Pause or return to menu |

## Screenshot
<img width="1365" height="767" alt="Screenshot 2025-12-19 202237" src="https://github.com/user-attachments/assets/9636dae0-13d2-42f8-ba3e-2f4deccc7588" />
<img width="1365" height="767" alt="Screenshot 2025-12-19 202537" src="https://github.com/user-attachments/assets/f5e0c8ec-9c44-40d4-8f03-d9cd8f67d216" />










## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Setup

1. **Clone or download this project**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

The `requirements.txt` contains:
```
PySide6>=6.6.0
```

## Running the Game

Simply execute:

```bash
python main.py
```

The game window will appear and you can start playing immediately by pressing **SPACE** on the menu screen.

## Project Structure

```
macan-run/
├── main.py                 # Entry point
├── core/
|   ├── asset_manager.py    # Manage Asset
|   ├── create_all_level.py # Create level automatically
│   ├── game_window.py      # Main window and widget
│   ├── engine.py           # Game engine and loop
│   ├── renderer.py         # QPainter rendering
│   ├── physics.py          # Physics engine
│   └── input_manager.py    # Keyboard input
├── game/
|   ├── particles.py        # Particles effect
│   ├── player.py           # Player character
|   ├── powerup.py          # Boost Player Speed, Health, Jump
│   ├── enemy.py            # Enemy AI
│   ├── coin.py             # Collectibles and hazards
│   ├── tilemap.py          # Tile rendering
│   └── level_manager.py    # Level loading
├── ui/
│   └── hud.py              # Heads-up display
├── services/
│   └── save_manager.py     # Save/load system
├── levels/
│   └── level1.txt          # Level data (ASCII)
├── assets/
│   └── README_assets.txt   # Asset specifications
└── README.md
```

## Level Format

Levels are defined using ASCII art in `.txt` files within the `levels/` folder.

### Tile Legend

| Character | Meaning |
|-----------|---------|
| `.` or ` ` | Empty space |
| `#` | Ground block (solid) |
| `=` | Platform (pass-through from below) |
| `\|` | Wall (solid) |
| `^` | Spike (hazard) |
| `C` | Coin (collectible) |
| `E` | Enemy spawn |
| `P` | Player spawn point |
| `F` | Flying Enemy |
| 'G` | Goal/Finish |
| 'H` | Health |
| 'J` | Jump |
| 'S` | Speed |
| 'D` | Shield |


### Example Level

See `levels/level1.txt` for a complete example level.

## Building Executables

### Using PyInstaller

Create a standalone executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Build (no console window, single file)
pyinstaller --noconsole --onefile main.py

# Output will be in dist/main.exe (Windows) or dist/main (Linux/Mac)
```

### Using Nuitka

For better performance and smaller size:

```bash
# Install Nuitka
pip install nuitka

# Windows (with MinGW64)
nuitka --standalone --plugin-enable=pyside6 --mingw64 --output-dir=dist main.py

# Linux/Mac
nuitka --standalone --plugin-enable=pyside6 --output-dir=dist main.py

# Output will be in dist/main.dist/ or dist/main.bin/
```

**Notes**:
- **Windows**: Requires MSVC (Visual Studio) or MinGW64. Use `--mingw64` flag for MinGW.
- **Linux**: May require `patchelf` package: `sudo apt install patchelf`
- **macOS**: Xcode command line tools required

### Build Optimizations

For production builds, consider:

```bash
# PyInstaller with optimizations
pyinstaller --noconsole --onefile --optimize=2 main.py

# Nuitka with full optimizations (slower build, faster runtime)
nuitka --standalone --plugin-enable=pyside6 --lto=yes --output-dir=dist main.py
```

## Save File Location

Game progress is automatically saved to:

- **Windows**: `%LOCALAPPDATA%\MacanRun\save.json`
- **Linux**: `~/.local/share/MacanRun/save.json`
- **macOS**: `~/Library/Application Support/MacanRun/save.json`

The save file stores:
- Current level
- Player position and health
- Score and coins collected
- Timestamp

## Performance Tips

The game is optimized for smooth 60 FPS gameplay:

1. **Background Caching**: Static backgrounds cached as QPixmap
2. **Culling**: Off-screen entities are not rendered
3. **Batched Rendering**: Tiles rendered row-by-row to minimize state changes
4. **Delta Time Physics**: Frame-rate independent physics
5. **Efficient Collision**: Grid-based spatial partitioning for tile collisions

## Asset Generation

All visual assets are **procedurally generated** using QPainter:

- **Player**: Rounded rectangle body with gradient, animated legs
- **Enemies**: Circular body with rotating spikes
- **Coins**: Radial gradient circles with rotation animation
- **Tiles**: Gradients and geometric patterns
- **Background**: Layered gradients with parallax clouds

See `assets/README.txt` for detailed specifications.

## Development

### Adding New Levels

1. Create a new `.txt` file in `levels/` folder
2. Use the ASCII legend to design your level
3. Load it via `LevelManager.load_level("your_level_name")`

### Extending the Game

- **New Enemies**: Extend the `Enemy` class in `game/enemy.py`
- **Power-ups**: Create new collectible classes similar to `Coin`
- **New Tiles**: Add tile types in `tilemap.py` render method
- **Audio**: Uncomment audio code in `engine.py` and add sound files

## Troubleshooting

### Game won't start
- Ensure Python 3.11+ is installed: `python --version`
- Verify PySide6 is installed: `pip list | grep PySide6`
- Try reinstalling: `pip install --force-reinstall PySide6`

### Low FPS
- Check system resources (CPU/GPU usage)
- Try reducing window size
- Disable antialiasing in renderer (comment out `setRenderHint` line)

### Save file not working
- Check directory permissions for save location
- Manually create directory if needed
- Check console for error messages

## Credits

**Macan Run - PySide6 Neo Edition**

Developed by: Macan Angkasa  
Engine: Python 3.11+ with PySide6  
License: © 2026 Macan Angkasa

## License

© 2026 Macan Angkasa. All rights reserved.

This game is provided as-is for educational and entertainment purposes.

---

**Have fun playing Macan Run!** 🎮🏃‍♂️

For issues or suggestions, please provide feedback through the appropriate channels.
