"""
Game window and main widget setup
ENHANCED: Fullscreen support + optimized rendering
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
        
        # Enable optimizations
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)  # No background clearing
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)  # Custom background
        
        # Initialize game engine (but don't start yet - show menu)
        self.engine = GameEngine(self)
        
        # Start timer for menu rendering
        self.engine.timer.start(self.engine.frame_time)
        
    def paintEvent(self, event):
        """Render game via engine - optimized."""
        self.engine.render(event)
        
    def keyPressEvent(self, event):
        """Forward key press to engine."""
        # Handle fullscreen toggle
        if event.key() == Qt.Key.Key_F11:
            self.parent().toggle_fullscreen()
            return
            
        self.engine.on_key_press(event)
        
    def keyReleaseEvent(self, event):
        """Forward key release to engine."""
        self.engine.on_key_release(event)
        
    def resizeEvent(self, event):
        """Handle widget resize."""
        super().resizeEvent(event)
        self.engine.on_resize(event.size())


class GameWindow(QMainWindow):
    """Main game window with fullscreen support."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macan Run - Neo Edition")
        self.resize(1024, 768)
        
        # Icon
        icon_path = "run.ico"
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, icon_path)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Set dark palette for better game aesthetics
        self._setup_palette()
        
        # Fullscreen state
        self.is_fullscreen = False
        self.normal_geometry = None
        
        # Create and set central widget
        self.game_widget = GameWidget(self)
        self.setCentralWidget(self.game_widget)
        
        # Start in fullscreen
        self.toggle_fullscreen()
        
    def _setup_palette(self):
        """Setup dark color palette."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(20, 20, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.setPalette(palette)
        
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        if self.is_fullscreen:
            # Exit fullscreen
            self.showNormal()
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.is_fullscreen = False
            print("📺 Windowed mode")
        else:
            # Enter fullscreen
            self.normal_geometry = self.geometry()
            self.showFullScreen()
            self.is_fullscreen = True
            print("🖥️ Fullscreen mode (Press F11 to exit)")
            
    def keyPressEvent(self, event):
        """Handle window-level key events."""
        if event.key() == Qt.Key.Key_F11:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)
        
    def closeEvent(self, event):
        """Handle window close."""
        # Save game state before closing
        if hasattr(self.game_widget, 'engine'):
            self.game_widget.engine.shutdown()
        event.accept()
