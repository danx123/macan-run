"""
Renderer - All rendering via QPainter
Uses caching for static elements and draw-by-code for sprites
"""
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QBrush, QPen, QPixmap, QFont
from PySide6.QtCore import QRect, QRectF, Qt, QSize


class Renderer:
    """Handles all game rendering using QPainter."""
    
    def __init__(self, size: QSize):
        self.size = size
        
        # Cached backgrounds
        self.bg_cache = None
        self.bg_size = None
        
        # Fonts
        self.title_font = QFont("Sans Serif", 48, QFont.Weight.Bold)
        self.menu_font = QFont("Sans Serif", 24)
        self.ui_font = QFont("Sans Serif", 18)
        
        self._generate_background_cache()
        
    def _generate_background_cache(self):
        """Generate cached background layers."""
        # Create pixmap for background
        self.bg_cache = QPixmap(self.size)
        self.bg_size = self.size
        
        painter = QPainter(self.bg_cache)
        
        # Sky gradient
        gradient = QLinearGradient(0, 0, 0, self.size.height())
        gradient.setColorAt(0.0, QColor(135, 206, 235))  # Sky blue
        gradient.setColorAt(0.7, QColor(255, 200, 150))  # Horizon orange
        gradient.setColorAt(1.0, QColor(255, 160, 100))  # Ground level
        
        painter.fillRect(0, 0, self.size.width(), self.size.height(), QBrush(gradient))
        
        # Draw clouds (simple circles)
        cloud_color = QColor(255, 255, 255, 180)
        painter.setBrush(QBrush(cloud_color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        for i in range(5):
            x = (i * 250 + 100) % self.size.width()
            y = 50 + (i * 30) % 100
            painter.drawEllipse(x, y, 80, 40)
            painter.drawEllipse(x + 30, y - 10, 60, 35)
            painter.drawEllipse(x + 50, y, 70, 38)
            
        painter.end()
        
    def render_background(self, painter: QPainter, camera_x: float):
        """Render scrolling background with parallax."""
        if not self.bg_cache or self.bg_size != self.size:
            self._generate_background_cache()
            
        # Parallax effect - background scrolls slower
        offset = int(camera_x * 0.3) % self.size.width()
        
        # Draw background twice for seamless scrolling
        painter.drawPixmap(-offset, 0, self.bg_cache)
        painter.drawPixmap(self.size.width() - offset, 0, self.bg_cache)
        
    def render_menu(self, painter: QPainter, size: QSize):
        """Render main menu screen."""
        # Background
        gradient = QLinearGradient(0, 0, 0, size.height())
        gradient.setColorAt(0.0, QColor(40, 40, 80))
        gradient.setColorAt(1.0, QColor(20, 20, 40))
        painter.fillRect(0, 0, size.width(), size.height(), QBrush(gradient))
        
        # Title
        painter.setPen(QColor(255, 215, 0))  # Gold
        painter.setFont(self.title_font)
        title_rect = QRect(0, size.height() // 3, size.width(), 100)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "MACAN RUN")
        
        # Subtitle
        painter.setPen(QColor(200, 200, 200))
        painter.setFont(self.menu_font)
        subtitle_rect = QRect(0, size.height() // 3 + 80, size.width(), 50)
        painter.drawText(subtitle_rect, Qt.AlignmentFlag.AlignCenter, "Neo Edition")
        
        # Instructions
        painter.setFont(self.ui_font)
        instructions = [
            "Press SPACE to Start",
            "",
            "Controls:",
            "Arrow Keys / A-D: Move",
            "Space: Jump (double jump available)",
            "P: Pause",
            "ESC: Menu"
        ]
        
        y = size.height() // 2 + 50
        for line in instructions:
            text_rect = QRect(0, y, size.width(), 30)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, line)
            y += 35
            
    def render_pause(self, painter: QPainter, size: QSize):
        """Render pause overlay."""
        # Semi-transparent overlay
        painter.fillRect(0, 0, size.width(), size.height(), QColor(0, 0, 0, 150))
        
        # Pause text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(self.title_font)
        pause_rect = QRect(0, size.height() // 2 - 50, size.width(), 100)
        painter.drawText(pause_rect, Qt.AlignmentFlag.AlignCenter, "PAUSED")
        
        painter.setFont(self.ui_font)
        hint_rect = QRect(0, size.height() // 2 + 50, size.width(), 30)
        painter.drawText(hint_rect, Qt.AlignmentFlag.AlignCenter, "Press P to Resume")
        
    def render_game_over(self, painter: QPainter, size: QSize, score: int):
        """Render game over screen."""
        # Dark overlay
        painter.fillRect(0, 0, size.width(), size.height(), QColor(20, 20, 20))
        
        # Game Over text
        painter.setPen(QColor(255, 50, 50))
        painter.setFont(self.title_font)
        text_rect = QRect(0, size.height() // 2 - 100, size.width(), 100)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "GAME OVER")
        
        # Score
        painter.setPen(QColor(200, 200, 200))
        painter.setFont(self.menu_font)
        score_rect = QRect(0, size.height() // 2, size.width(), 50)
        painter.drawText(score_rect, Qt.AlignmentFlag.AlignCenter, f"Score: {score}")
        
        # Restart hint
        painter.setFont(self.ui_font)
        hint_rect = QRect(0, size.height() // 2 + 80, size.width(), 30)
        painter.drawText(hint_rect, Qt.AlignmentFlag.AlignCenter, "Press SPACE to Restart")
        
    def render_level_complete(self, painter: QPainter, size: QSize, score: int):
        """Render level complete screen."""
        # Gradient background
        gradient = QLinearGradient(0, 0, 0, size.height())
        gradient.setColorAt(0.0, QColor(50, 150, 50))
        gradient.setColorAt(1.0, QColor(20, 80, 20))
        painter.fillRect(0, 0, size.width(), size.height(), QBrush(gradient))
        
        # Victory text
        painter.setPen(QColor(255, 215, 0))
        painter.setFont(self.title_font)
        text_rect = QRect(0, size.height() // 2 - 100, size.width(), 100)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "LEVEL COMPLETE!")
        
        # Score
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(self.menu_font)
        score_rect = QRect(0, size.height() // 2, size.width(), 50)
        painter.drawText(score_rect, Qt.AlignmentFlag.AlignCenter, f"Score: {score}")
        
        # Continue hint
        painter.setFont(self.ui_font)
        hint_rect = QRect(0, size.height() // 2 + 80, size.width(), 30)
        painter.drawText(hint_rect, Qt.AlignmentFlag.AlignCenter, "Press SPACE to Continue")
        
    def on_resize(self, size: QSize):
        """Handle renderer resize."""
        self.size = size
        self._generate_background_cache()