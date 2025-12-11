"""
Player - Player character with movement, animation, and state
"""
import math
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient
from PySide6.QtCore import QRectF, Qt


class Player:
    """Player character entity."""
    
    def __init__(self, x: float, y: float):
        # Position and dimensions
        self.x = x
        self.y = y
        self.width = 32
        self.height = 48
        
        # Physics
        self.vx = 0.0  # Velocity X
        self.vy = 0.0  # Velocity Y
        self.on_ground = False
        
        # Movement parameters
        self.move_speed = 250.0  # pixels/s
        self.jump_force = 450.0  # pixels/s
        self.max_jumps = 2  # Double jump
        self.jumps_remaining = 2
        
        # State
        self.health = 3
        self.max_health = 3
        self.facing_right = True
        self.invulnerable_time = 0.0
        self.invulnerable_duration = 1.0  # 1 second after taking damage
        
        # Animation
        self.animation_time = 0.0
        self.frame = 0
        
    def update(self, delta_time: float, input_manager):
        """Update player state and handle input."""
        # Handle movement input
        if input_manager.is_move_left():
            self.vx = -self.move_speed
            self.facing_right = False
        elif input_manager.is_move_right():
            self.vx = self.move_speed
            self.facing_right = True
            
        # Handle jump input
        if input_manager.is_jump():
            if self.jumps_remaining > 0:
                from core.physics import PhysicsEngine
                physics = PhysicsEngine()
                physics.apply_jump_force(self, self.jump_force)
                input_manager.clear_key('Space')
                input_manager.clear_key('W')
                
        # Update animation
        if abs(self.vx) > 10:
            self.animation_time += delta_time * 10
            self.frame = int(self.animation_time) % 4
        else:
            self.frame = 0
            
        # Update invulnerability
        if self.invulnerable_time > 0:
            self.invulnerable_time -= delta_time
            
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render player sprite using QPainter."""
        # Screen position
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Skip if off-screen
        if screen_x < -100 or screen_x > 1200:
            return
            
        # Flashing effect when invulnerable
        if self.invulnerable_time > 0 and int(self.invulnerable_time * 10) % 2 == 0:
            return
            
        painter.save()
        
        # Flip sprite if facing left
        if not self.facing_right:
            painter.translate(screen_x + self.width, screen_y)
            painter.scale(-1, 1)
            screen_x = 0
            screen_y = 0
            
        # Draw player body (rounded rectangle)
        gradient = QLinearGradient(screen_x, screen_y, screen_x, screen_y + self.height)
        gradient.setColorAt(0.0, QColor(255, 140, 0))  # Orange
        gradient.setColorAt(1.0, QColor(200, 100, 0))  # Darker orange
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(100, 50, 0), 2))
        
        # Animated body (slight bounce)
        bounce = math.sin(self.animation_time * 5) * 2 if abs(self.vx) > 10 else 0
        body_rect = QRectF(screen_x + 4, screen_y + 8 + bounce, self.width - 8, self.height - 12)
        painter.drawRoundedRect(body_rect, 8, 8)
        
        # Draw head
        head_color = QColor(255, 180, 100)  # Skin tone
        painter.setBrush(QBrush(head_color))
        painter.setPen(QPen(QColor(100, 50, 0), 2))
        
        head_rect = QRectF(screen_x + 8, screen_y + bounce, self.width - 16, 16)
        painter.drawEllipse(head_rect)
        
        # Draw eyes
        eye_color = QColor(50, 50, 50)
        painter.setBrush(QBrush(eye_color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        eye_y = screen_y + 6 + bounce
        painter.drawEllipse(screen_x + 12, eye_y, 4, 4)
        painter.drawEllipse(screen_x + 20, eye_y, 4, 4)
        
        # Draw legs (animated walking)
        painter.setBrush(QBrush(QColor(100, 50, 0)))
        leg_offset = math.sin(self.animation_time * 8) * 3 if abs(self.vx) > 10 else 0
        
        # Left leg
        painter.drawRect(screen_x + 8, screen_y + self.height - 8 + leg_offset, 6, 8)
        # Right leg
        painter.drawRect(screen_x + 18, screen_y + self.height - 8 - leg_offset, 6, 8)
        
        painter.restore()
        
        # Draw health bar above player
        self._draw_health_bar(painter, screen_x if self.facing_right else screen_x - self.width, screen_y - 10)
        
    def _draw_health_bar(self, painter: QPainter, x: float, y: float):
        """Draw health bar above player."""
        bar_width = 40
        bar_height = 4
        
        # Background
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x - 4, y, bar_width, bar_height)
        
        # Health
        health_ratio = self.health / self.max_health
        health_width = bar_width * health_ratio
        
        # Color based on health
        if health_ratio > 0.6:
            health_color = QColor(0, 255, 0)
        elif health_ratio > 0.3:
            health_color = QColor(255, 255, 0)
        else:
            health_color = QColor(255, 0, 0)
            
        painter.setBrush(QBrush(health_color))
        painter.drawRect(x - 4, y, health_width, bar_height)
        
    def take_damage(self, amount: int = 1):
        """Take damage if not invulnerable."""
        if self.invulnerable_time <= 0:
            self.health -= amount
            self.invulnerable_time = self.invulnerable_duration
            # Knockback
            self.vy = -200
            
    def heal(self, amount: int = 1):
        """Heal player."""
        self.health = min(self.health + amount, self.max_health)