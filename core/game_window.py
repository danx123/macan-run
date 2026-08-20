"""
Game window and main widget setup
CHANGED: Reverted from QOpenGLWidget back to plain QWidget.
QOpenGLWidget caused flicker for this game (pure QPainter 2D rendering,
no raw GL draw calls) because the back buffer content between paintGL()
calls is undefined unless explicitly cleared, and mixing QPainter's GL
paint engine with a CoreProfile context is unreliable on several
drivers. A plain QWidget with WA_OpaquePaintEvent / WA_NoSystemBackground
avoids both problems and skips Qt's default background auto-fill, which
was the other common source of paint flicker.
"""
import os
os.environ["QT_OPENGL"] = "desktop" 
import sys
from PySide6.QtWidgets import QMainWindow, QWidget
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QPalette, QColor, QIcon
from core.engine import GameEngine


class GameWidget(QWidget):
    """
    Central widget that hosts the game engine.
    Plain QWidget + custom paintEvent, software/raster rendering via QPainter.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(QSize(1024, 768))        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Prevent Qt from auto-filling the background with the palette
        # color before paintEvent runs each frame - this is the classic
        # source of flicker with custom-painted widgets.
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        # We fully repaint every pixel every frame ourselves, so no need
        # for Qt to track/repaint dirty regions.
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents, True)
        
        # Initialize game engine
        self.engine = GameEngine(self)
        
        # Setup Render Loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        # 16ms ~ 60 FPS
        self.timer.start(16)

    def resizeEvent(self, event):
        """Called whenever the widget has been resized."""
        self.engine.on_resize(event.size())
        super().resizeEvent(event)

    def paintEvent(self, event):
        """Renders the current frame via QPainter."""
        self.engine.render(event)
        
    def update_game(self):
        """Tick the game logic and request a repaint."""
        self.engine.tick()
        self.update()
        
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
