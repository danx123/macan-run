"""
Game window and main widget setup
Handles window creation and central game widget
"""
import os
import sys
from PySide6.QtWidgets import QMainWindow, QWidget
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPalette, QColor, QIcon
from core.engine import GameEngine


class GameWidget(QWidget):
    """Central widget that hosts the game engine and handles rendering."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(QSize(1024, 768))        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Initialize game engine
        self.engine = GameEngine(self)
        self.engine.start()
        
    def paintEvent(self, event):
        """Render game via engine."""
        self.engine.render(event)
        
    def keyPressEvent(self, event):
        """Forward key press to engine."""
        self.engine.on_key_press(event)
        
    def keyReleaseEvent(self, event):
        """Forward key release to engine."""
        self.engine.on_key_release(event)
        
    def resizeEvent(self, event):
        """Handle widget resize."""
        super().resizeEvent(event)
        self.engine.on_resize(event.size())


class GameWindow(QMainWindow):
    """Main game window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macan Run - Neo Edition")
        self.resize(1024, 768)
        icon_path = "run.ico"
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, icon_path)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Set dark palette for better game aesthetics
        self._setup_palette()
        
        # Create and set central widget
        self.game_widget = GameWidget(self)
        self.setCentralWidget(self.game_widget)
        
    def _setup_palette(self):
        """Setup dark color palette."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(20, 20, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.setPalette(palette)
        
    def closeEvent(self, event):
        """Handle window close."""
        # Save game state before closing
        if hasattr(self.game_widget, 'engine'):
            self.game_widget.engine.shutdown()
        event.accept()
