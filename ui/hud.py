"""
HUD - Heads-Up Display for game stats
Shows score, coins, health, and distance
"""
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPolygonF
from PySide6.QtCore import QRect, Qt, QPointF


class HUD:
    """Heads-up display overlay."""
    
    def __init__(self):
        self.font = QFont("Sans Serif", 16, QFont.Weight.Bold)
        self.small_font = QFont("Sans Serif", 12)
        
    def render(self, painter: QPainter, score: int, coins: int, health: int, distance: int):
        """Render HUD elements."""
        painter.save()
        
        # Semi-transparent background panel
        panel_color = QColor(20, 20, 30, 200)
        painter.setBrush(QBrush(panel_color))
        painter.setPen(QPen(QColor(100, 100, 120), 2))
        painter.drawRoundedRect(10, 10, 280, 100, 10, 10)
        
        # Text color
        text_color = QColor(255, 255, 255)
        painter.setPen(text_color)
        painter.setFont(self.font)
        
        # Score
        painter.drawText(QRect(20, 20, 260, 25), Qt.AlignmentFlag.AlignLeft, f"Score: {score}")
        
        # Coins
        coin_color = QColor(255, 215, 0)
        painter.setPen(coin_color)
        painter.drawText(QRect(20, 48, 260, 25), Qt.AlignmentFlag.AlignLeft, f"💰 Coins: {coins}")
        
        # Health
        self._render_hearts(painter, 20, 76, health, 3)
        
        # Distance (top-right)
        painter.setPen(text_color)
        painter.setFont(self.small_font)
        painter.drawText(QRect(20, 100, 260, 20), Qt.AlignmentFlag.AlignLeft, f"Distance: {distance}m")
        
        painter.restore()
        
    def _render_hearts(self, painter: QPainter, x: int, y: int, current: int, maximum: int):
        """Render health hearts."""
        heart_size = 20
        spacing = 25
        
        for i in range(maximum):
            heart_x = x + i * spacing
            
            if i < current:
                # Full heart
                color = QColor(255, 50, 50)
            else:
                # Empty heart
                color = QColor(100, 100, 100)
                
            self._draw_heart(painter, heart_x, y, heart_size, color)
            
    def _draw_heart(self, painter: QPainter, x: int, y: int, size: int, color: QColor):
        """Draw a heart shape."""
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(200, 50, 50) if color.red() > 200 else QColor(70, 70, 70), 2))
        
        # Simplified heart using circles and triangle
        half = size // 2
        
        # Left circle
        painter.drawEllipse(x, y, half, half)
        # Right circle
        painter.drawEllipse(x + half, y, half, half)
        
        # Bottom triangle
        # FIX: Gunakan QPolygonF dengan QPointF, jangan list biasa
        triangle = QPolygonF([
            QPointF(x, y + half / 2),
            QPointF(x + size, y + half / 2),
            QPointF(x + half, y + size)
        ])
        
        painter.drawPolygon(triangle)