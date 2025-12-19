"""
Macan Run - PySide6 Neo Edition
Entry point for the game
© 2025 Macan Angkasa
"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QSurfaceFormat

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.game_window import GameWindow


def main():
    """Initialize and run the game application with OpenGL settings."""
    
    # 1. Setup OpenGL Surface Format
    # This ensures antialiasing (smooth lines) and proper depth buffer
    format = QSurfaceFormat()
    format.setDepthBufferSize(24)
    format.setStencilBufferSize(8)
    format.setVersion(3, 3) # OpenGL 3.3 Core
    format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    # Enable Multisampling (Anti-aliasing) for smoother graphics
    format.setSamples(4) 
    # Enable VSync to prevent tearing
    format.setSwapInterval(1)
    
    # Apply format globally
    QSurfaceFormat.setDefaultFormat(format)
    
    # 2. Enable High DPI scaling
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
