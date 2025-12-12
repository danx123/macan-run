"""
Coin - Collectible item, Spikes, and Finish Flag
FIXED: Finish flag collision box and visibility
"""
import math
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient, QPolygonF
from PySide6.QtCore import Qt, QPointF


class Coin:
    """Collectible coin entity."""
    
    def __init__(self, x: float, y: float):
        # Position and dimensions
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        
        # Animation
        self.animation_time = 0.0
        self.float_offset = 0.0
        
    def update(self, delta_time: float):
        """Update coin animation."""
        self.animation_time += delta_time
        # Floating animation
        self.float_offset = math.sin(self.animation_time * 3) * 4
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render coin sprite."""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y + self.float_offset
        
        # Skip if off-screen
        if screen_x < -50 or screen_x > 1200:
            return
            
        painter.save()
        
        # Rotation animation
        rotation = math.sin(self.animation_time * 4) * 20
        
        center_x = screen_x + self.width / 2
        center_y = screen_y + self.height / 2
        
        painter.translate(center_x, center_y)
        painter.rotate(rotation)
        painter.translate(-center_x, -center_y)
        
        # Draw coin with gradient
        gradient = QRadialGradient(center_x, center_y, self.width / 2)
        gradient.setColorAt(0.0, QColor(255, 223, 0))  # Bright gold
        gradient.setColorAt(0.7, QColor(255, 215, 0))  # Gold
        gradient.setColorAt(1.0, QColor(200, 170, 0))  # Dark gold
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(150, 120, 0), 2))
        
        # Main coin circle
        painter.drawEllipse(screen_x + 2, screen_y + 2, self.width - 4, self.height - 4)
        
        # Inner circle detail
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(200, 170, 0), 1))
        painter.drawEllipse(screen_x + 6, screen_y + 6, self.width - 12, self.height - 12)
        
        painter.restore()


class Spike:
    """Hazard spike entity."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 48
        self.height = 48
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render spike."""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if screen_x < -100 or screen_x > 1200:
            return
            
        painter.save()
        
        # Draw spike triangle
        spike_color = QColor(150, 150, 150)
        painter.setBrush(QBrush(spike_color))
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        
        # Triangle points
        triangle = QPolygonF([
            QPointF(screen_x + self.width / 2, screen_y),          # Top
            QPointF(screen_x, screen_y + self.height),             # Bottom left
            QPointF(screen_x + self.width, screen_y + self.height) # Bottom right
        ])
        
        painter.drawPolygon(triangle)
        
        painter.restore()


class Finish:
    """Level finish flag - FIXED collision box."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        # LARGER collision box for easier detection
        self.width = 64
        self.height = 96
        self.animation_time = 0.0
        
    def update(self, delta_time: float):
        """Update animation."""
        self.animation_time += delta_time
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render finish flag - ALWAYS VISIBLE."""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # DON'T skip rendering - always show finish flag!
        # Removed off-screen culling to ensure visibility
        
        painter.save()
        
        # Flag pole (thicker for visibility)
        painter.setBrush(QBrush(QColor(139, 69, 19)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(screen_x + 26, screen_y, 12, self.height)
        
        # Flag (waving animation)
        wave = math.sin(self.animation_time * 5) * 5
        
        # BRIGHT GREEN flag for visibility
        flag_color = QColor(50, 255, 50)
        painter.setBrush(QBrush(flag_color))
        painter.setPen(QPen(QColor(30, 200, 30), 2))
        
        # Flag polygon
        flag_shape = QPolygonF([
            QPointF(screen_x + 38, screen_y + 15),
            QPointF(screen_x + 78 + wave, screen_y + 35),
            QPointF(screen_x + 38, screen_y + 55)
        ])
        
        painter.drawPolygon(flag_shape)
        
        # Add "GOAL" text for clarity
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(painter.font())
        painter.drawText(int(screen_x + 5), int(screen_y + self.height + 20), "GOAL")
        
        # Debug: Draw collision box (optional - comment out in production)
        # painter.setPen(QPen(QColor(255, 0, 0, 100), 2))
        # painter.setBrush(Qt.BrushStyle.NoBrush)
        # painter.drawRect(screen_x, screen_y, self.width, self.height)
        
        painter.restore()
