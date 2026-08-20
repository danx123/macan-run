"""
Macan Run - PySide6 Neo Edition
Entry point for the game
© 2025 Macan Angkasa

CHANGED: Removed QSurfaceFormat/OpenGL context setup. The game widget
was reverted from QOpenGLWidget to a plain QWidget (see game_window.py)
to fix rendering flicker, so the GL surface format is no longer needed.
"""
import os
os.environ["QT_OPENGL"] = "desktop"
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.game_window import GameWindow


def main():
    """Initialize and run the game application."""

    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Macan Run")
    app.setOrganizationName("Macan Angkasa")
    
    # Create and show game window
    window = GameWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
