"""
Enemy - Basic patrol AI enemy
"""
import math
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF
from PySide6.QtCore import QRectF, Qt, QPointF


class Enemy:
    """Enemy entity with patrol AI."""
    
    def __init__(self, x: float, y: float, patrol_range: float = 150.0):
        # Position and dimensions
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        
        # Patrol AI
        self.spawn_x = x
        self.patrol_range = patrol_range
        self.move_speed = 80.0  # pixels/s
        self.direction = 1  # 1 = right, -1 = left
        
        # State
        self.health = 2
        self.animation_time = 0.0
        
    def update(self, delta_time: float):
        """Update enemy AI."""
        # Move in current direction
        self.x += self.move_speed * self.direction * delta_time
        
        # Check patrol bounds
        distance_from_spawn = abs(self.x - self.spawn_x)
        if distance_from_spawn > self.patrol_range:
            # Turn around
            self.direction *= -1
            
        # Update animation
        self.animation_time += delta_time
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render enemy sprite."""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Skip if off-screen
        if screen_x < -100 or screen_x > 1200:
            return
            
        painter.save()
        
        # Body (spiky circle)
        body_color = QColor(150, 50, 50)  # Dark red
        painter.setBrush(QBrush(body_color))
        painter.setPen(QPen(QColor(100, 30, 30), 2))
        
        center_x = screen_x + self.width / 2
        center_y = screen_y + self.height / 2
        
        # Draw body circle
        painter.drawEllipse(center_x - 14, center_y - 14, 28, 28)
        
        # Draw spikes
        spike_color = QColor(120, 40, 40)
        painter.setBrush(QBrush(spike_color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        num_spikes = 8
        for i in range(num_spikes):
            angle = (i / num_spikes) * 2 * math.pi + self.animation_time * 2
            spike_x = center_x + math.cos(angle) * 12
            spike_y = center_y + math.sin(angle) * 12
            outer_x = center_x + math.cos(angle) * 18
            outer_y = center_y + math.sin(angle) * 18
            
            # Draw spike triangle - FIX: Use QPolygonF
            spike_shape = QPolygonF([
                QPointF(spike_x, spike_y),
                QPointF(outer_x, outer_y),
                QPointF(spike_x + 3, spike_y + 3)
            ])
            painter.drawPolygon(spike_shape)
            
        # Draw eyes
        eye_color = QColor(255, 200, 0)  # Yellow
        painter.setBrush(QBrush(eye_color))
        
        # Direction-based eye position
        eye_offset = 4 if self.direction > 0 else -4
        painter.drawEllipse(center_x + eye_offset - 3, center_y - 6, 6, 6)
        painter.drawEllipse(center_x + eye_offset - 3, center_y + 2, 6, 6)
        
        painter.restore()
