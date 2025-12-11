# Macan Run - Complete Setup Guide

## Quick Start (5 Minutes)

### 1. Project Structure

Create this directory structure:

```
macan-run/
├── main.py
├── requirements.txt
├── README.md
├── core/
│   ├── __init__.py
│   ├── game_window.py
│   ├── engine.py
│   ├── renderer.py
│   ├── physics.py
│   └── input_manager.py
├── game/
│   ├── __init__.py
│   ├── player.py
│   ├── enemy.py
│   ├── coin.py
│   ├── tilemap.py
│   └── level_manager.py
├── ui/
│   ├── __init__.py
│   └── hud.py
├── services/
│   ├── __init__.py
│   └── save_manager.py
├── levels/
│   └── level1.txt
└── assets/
    └── README_assets.txt
```

### 2. Create Empty `__init__.py` Files

Create empty files (or with docstrings) in each package:
- `core/__init__.py`
- `game/__init__.py`
- `ui/__init__.py`
- `services/__init__.py`

### 3. Install Dependencies

```bash
pip install PySide6
```

### 4. Run the Game

```bash
python main.py
```

## Detailed Setup Instructions

### For Windows

1. **Install Python 3.11+**
   - Download from https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation

2. **Open Command Prompt**
   ```cmd
   cd path\to\macan-run
   pip install -r requirements.txt
   python main.py
   ```

### For Linux (Ubuntu/Debian)

1. **Install Python and pip**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3-pip
   ```

2. **Install dependencies**
   ```bash
   cd ~/macan-run
   pip3 install -r requirements.txt
   python3 main.py
   ```

### For macOS

1. **Install Python via Homebrew**
   ```bash
   brew install python@3.11
   ```

2. **Run the game**
   ```bash
   cd ~/macan-run
   pip3 install -r requirements.txt
   python3 main.py
   ```

## Building Standalone Executables

### PyInstaller (Easiest)

**Windows:**
```cmd
pip install pyinstaller
pyinstaller --noconsole --onefile --name="MacanRun" main.py
```

**Linux/Mac:**
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name="MacanRun" main.py
```

Output: `dist/MacanRun.exe` (Windows) or `dist/MacanRun` (Linux/Mac)

### Nuitka (Best Performance)

**Windows (with MinGW):**
```cmd
pip install nuitka
python -m nuitka --standalone --mingw64 --plugin-enable=pyside6 --windows-disable-console --output-dir=dist main.py
```

**Windows (with MSVC):**
```cmd
pip install nuitka
python -m nuitka --standalone --plugin-enable=pyside6 --windows-disable-console --output-dir=dist main.py
```

**Linux:**
```bash
pip install nuitka
python3 -m nuitka --standalone --plugin-enable=pyside6 --output-dir=dist main.py
```

**macOS:**
```bash
pip install nuitka
python3 -m nuitka --standalone --plugin-enable=pyside6 --macos-create-app-bundle --output-dir=dist main.py
```

### Build Options Explained

**PyInstaller Flags:**
- `--noconsole`: Hide console window (Windows)
- `--onefile`: Create single executable
- `--name`: Set executable name
- `--icon`: Add custom icon (requires .ico file)

**Nuitka Flags:**
- `--standalone`: Include all dependencies
- `--plugin-enable=pyside6`: Enable PySide6 support
- `--mingw64`: Use MinGW compiler (Windows)
- `--windows-disable-console`: Hide console (Windows)
- `--lto=yes`: Link-time optimization (slower build, faster runtime)
- `--macos-create-app-bundle`: Create .app bundle (macOS)

## Troubleshooting

### "ModuleNotFoundError: No module named 'PySide6'"

**Solution:**
```bash
pip install --upgrade PySide6
```

### "DLL load failed" (Windows)

**Solution:**
Install Visual C++ Redistributable:
https://aka.ms/vs/17/release/vc_redist.x64.exe

### "command not found: python" (Linux/Mac)

**Solution:**
Use `python3` instead:
```bash
python3 main.py
```

### Game runs but no window appears

**Solution:**
1. Check if firewall is blocking
2. Try running with console:
   ```bash
   python main.py
   ```
3. Check error messages in console

### Low FPS / Laggy

**Solution:**
1. Close other applications
2. Lower window resolution (edit `game_window.py`, change `resize(1024, 768)` to smaller size)
3. Disable antialiasing (comment out `setRenderHint` in `renderer.py`)

### Save file not created

**Solution:**
1. Check permissions:
   - Windows: `%LOCALAPPDATA%`
   - Linux: `~/.local/share`
   - Mac: `~/Library/Application Support`
2. Manually create directory if needed
3. Run game as administrator (if necessary)

### Build fails with Nuitka

**Windows:**
- Install MinGW-w64 or Visual Studio Build Tools
- Use `--mingw64` flag if you have MinGW

**Linux:**
- Install required packages:
  ```bash
  sudo apt install patchelf ccache
  ```

**macOS:**
- Install Xcode Command Line Tools:
  ```bash
  xcode-select --install
  ```

## Testing Your Installation

After setup, test each feature:

1. **Launch Game**: Window opens with menu
2. **Controls**: Arrow keys and Space work
3. **Gameplay**: Player can move, jump, collect coins
4. **Collision**: Player collides with tiles and enemies
5. **Pause**: P key pauses/resumes
6. **Save**: Game saves on exit

## Performance Benchmarks

Expected performance on modern hardware:

- **Startup time**: < 2 seconds
- **FPS**: 60 (stable)
- **Memory usage**: ~50-100 MB
- **CPU usage**: ~5-10% (single core)

If your performance is significantly lower, check:
- Python version (3.11+ recommended)
- PySide6 version (6.6.0+ recommended)
- GPU drivers up to date
- No background applications consuming resources

## Development Setup

For developers wanting to modify the game:

### Recommended IDE Setup

**VS Code:**
```json
{
  "python.analysis.typeCheckingMode": "basic",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black"
}
```

**PyCharm:**
- Set Python interpreter to 3.11+
- Enable PySide6 completion
- Configure run configuration for `main.py`

### Optional Dev Dependencies

```bash
pip install black pylint mypy  # Code formatting and linting
pip install pytest  # Testing framework
```

## Next Steps

After successful setup:

1. Play through the demo level
2. Read the [README.md](README.md) for game features
3. Check [assets/README_assets.txt](assets/README_assets.txt) for asset specs
4. Create custom levels by editing `levels/level1.txt`
5. Explore the code and modify as desired

## Support

For issues or questions:
- Check console output for error messages
- Review the troubleshooting section above
- Ensure all files are present and properly structured
- Verify Python and PySide6 versions

---

**Happy Gaming!** 🎮

If you encounter any other issues not covered here, check the Python and PySide6 documentation.
