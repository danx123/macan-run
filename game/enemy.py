"""
Enemy - Enemy entities with various AI patterns
ENHANCED: Added new enemy types - Jumper, Charger, and Bomber
"""
import math
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF, QRadialGradient
from PySide6.QtCore import QRectF, Qt, QPointF


class Enemy:
    """Base enemy entity with patrol AI."""
    
    def __init__(self, x: float, y: float, patrol_range: float = 150.0):
        """
        Initialize enemy.
        
        Args:
            x, y: Spawn position
            patrol_range: Distance from spawn before turning around
        """
        # Position and dimensions
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        
        # Patrol AI
        self.spawn_x = x
        self.spawn_y = y
        self.patrol_range = patrol_range
        self.move_speed = 80.0  # pixels/s
        self.direction = 1  # 1 = right, -1 = left
        
        # State
        self.health = 2
        self.max_health = 2
        self.animation_time = 0.0
        self.alive = True
        
    def update(self, delta_time: float):
        """
        Update enemy AI and movement.
        
        Args:
            delta_time: Time elapsed since last frame
        """
        if not self.alive:
            return
            
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
        """
        Render enemy sprite.
        
        Args:
            painter: QPainter object
            camera_x, camera_y: Camera offset
        """
        if not self.alive:
            return
            
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
            
            # Draw spike triangle
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
        
        # Draw health bar if damaged
        if self.health < self.max_health:
            self._draw_health_bar(painter, screen_x, screen_y - 10)
            
    def _draw_health_bar(self, painter: QPainter, x: float, y: float):
        """Draw health bar above enemy."""
        bar_width = 32
        bar_height = 3
        
        # Background
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(int(x), int(y), bar_width, bar_height)
        
        # Health
        health_ratio = self.health / self.max_health
        health_width = bar_width * health_ratio
        
        health_color = QColor(255, 50, 50)
        painter.setBrush(QBrush(health_color))
        painter.drawRect(int(x), int(y), int(health_width), bar_height)
        
    def take_damage(self, amount: int = 1):
        """
        Take damage and check if defeated.
        
        Args:
            amount: Damage amount
            
        Returns:
            True if enemy died from this damage
        """
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            return True
        return False


class FlyingEnemy(Enemy):
    """Enemy that flies in sine wave pattern."""
    
    def __init__(self, x: float, y: float, patrol_range: float = 200.0):
        """
        Initialize flying enemy.
        
        Args:
            x, y: Spawn position
            patrol_range: Horizontal patrol distance
        """
        super().__init__(x, y, patrol_range)
        
        # Flying-specific properties
        self.flight_amplitude = 60.0  # Height of sine wave
        self.wave_frequency = 2.0  # Speed of wave oscillation
        self.move_speed = 100.0  # Slightly faster than ground enemy
        self.width = 36
        self.height = 28
        
        # Wing animation
        self.wing_flap_speed = 12.0
        
    def update(self, delta_time: float):
        """Update flying pattern with sine wave movement."""
        if not self.alive:
            return
            
        # Horizontal movement
        self.x += self.move_speed * self.direction * delta_time
        
        # Sine wave vertical movement
        self.animation_time += delta_time
        self.y = self.spawn_y + math.sin(self.animation_time * self.wave_frequency) * self.flight_amplitude
        
        # Check patrol bounds (horizontal only)
        distance_from_spawn = abs(self.x - self.spawn_x)
        if distance_from_spawn > self.patrol_range:
            self.direction *= -1
            
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render flying enemy with wings."""
        if not self.alive:
            return
            
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Skip if off-screen
        if screen_x < -100 or screen_x > 1200:
            return
            
        painter.save()
        
        center_x = screen_x + self.width / 2
        center_y = screen_y + self.height / 2
        
        # Draw wings (animated flapping)
        wing_angle = math.sin(self.animation_time * self.wing_flap_speed) * 25
        wing_color = QColor(100, 100, 200, 180)
        painter.setBrush(QBrush(wing_color))
        painter.setPen(QPen(QColor(70, 70, 150), 2))
        
        # Left wing
        painter.save()
        painter.translate(center_x - 12, center_y)
        painter.rotate(wing_angle)
        painter.drawEllipse(-12, -6, 18, 12)
        painter.restore()
        
        # Right wing
        painter.save()
        painter.translate(center_x + 12, center_y)
        painter.rotate(-wing_angle)
        painter.drawEllipse(-6, -6, 18, 12)
        painter.restore()
        
        # Draw body (oval)
        body_color = QColor(120, 120, 220)
        painter.setBrush(QBrush(body_color))
        painter.setPen(QPen(QColor(80, 80, 180), 2))
        painter.drawEllipse(
            center_x - 14, center_y - 10,
            28, 20
        )
        
        # Draw eyes (looking in movement direction)
        eye_color = QColor(255, 255, 100)
        painter.setBrush(QBrush(eye_color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        eye_offset = 6 if self.direction > 0 else -6
        painter.drawEllipse(center_x + eye_offset - 3, center_y - 4, 6, 6)
        
        # Draw beak/nose
        beak_color = QColor(255, 150, 50)
        painter.setBrush(QBrush(beak_color))
        
        beak_tip = center_x + (12 if self.direction > 0 else -12)
        beak_points = QPolygonF([
            QPointF(center_x + eye_offset, center_y),
            QPointF(beak_tip, center_y - 2),
            QPointF(beak_tip, center_y + 2)
        ])
        painter.drawPolygon(beak_points)
        
        painter.restore()
        
        # Draw health bar if damaged
        if self.health < self.max_health:
            self._draw_health_bar(painter, screen_x, screen_y - 10)


class JumperEnemy(Enemy):
    """Enemy that jumps periodically - NEW!"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, patrol_range=100)
        
        self.move_speed = 60.0
        self.vy = 0.0  # Vertical velocity
        self.on_ground = True
        self.jump_timer = 0.0
        self.jump_interval = 2.0  # Jump every 2 seconds
        self.jump_force = -350.0
        self.health = 2
        self.width = 34
        self.height = 34
        
    def update(self, delta_time: float):
        if not self.alive:
            return
            
        # Horizontal movement
        self.x += self.move_speed * self.direction * delta_time
        
        # Gravity
        if not self.on_ground:
            self.vy += 980 * delta_time
            self.y += self.vy * delta_time
        
        # Simple ground check (reset at spawn_y)
        if self.y >= self.spawn_y:
            self.y = self.spawn_y
            self.vy = 0
            self.on_ground = True
        
        # Jump timer
        self.jump_timer += delta_time
        if self.jump_timer >= self.jump_interval and self.on_ground:
            self.vy = self.jump_force
            self.on_ground = False
            self.jump_timer = 0.0
        
        # Patrol bounds
        distance_from_spawn = abs(self.x - self.spawn_x)
        if distance_from_spawn > self.patrol_range:
            self.direction *= -1
            
        self.animation_time += delta_time
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        if not self.alive:
            return
            
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if screen_x < -100 or screen_x > 1200:
            return
            
        painter.save()
        
        center_x = screen_x + self.width / 2
        center_y = screen_y + self.height / 2
        
        # Body (spring-like)
        body_color = QColor(255, 150, 50)  # Orange
        painter.setBrush(QBrush(body_color))
        painter.setPen(QPen(QColor(200, 100, 30), 2))
        
        # Squash and stretch when jumping
        if not self.on_ground:
            # Stretched in air
            painter.drawEllipse(center_x - 12, center_y - 18, 24, 36)
        else:
            # Squashed on ground
            painter.drawEllipse(center_x - 16, center_y - 14, 32, 28)
        
        # Spring coil lines
        painter.setPen(QPen(QColor(150, 80, 20), 2))
        for i in range(3):
            y_offset = -10 + i * 8
            painter.drawLine(center_x - 10, center_y + y_offset, center_x + 10, center_y + y_offset)
        
        # Eyes
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.setPen(Qt.PenStyle.NoPen)
        eye_offset = 5 if self.direction > 0 else -5
        painter.drawEllipse(center_x + eye_offset - 3, center_y - 8, 6, 6)
        
        painter.restore()
        
        if self.health < self.max_health:
            self._draw_health_bar(painter, screen_x, screen_y - 10)


class ChargerEnemy(Enemy):
    """Enemy that charges at player when in range - NEW!"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, patrol_range=200)
        
        self.normal_speed = 50.0
        self.charge_speed = 250.0
        self.move_speed = self.normal_speed
        self.detection_range = 200.0
        self.is_charging = False
        self.charge_cooldown = 0.0
        self.health = 3
        self.max_health = 3
        self.width = 38
        self.height = 32
        
    def update(self, delta_time: float, player_x: float = None):
        if not self.alive:
            return
        
        # Cooldown
        if self.charge_cooldown > 0:
            self.charge_cooldown -= delta_time
            
        # Check if player is in range
        if player_x is not None and self.charge_cooldown <= 0:
            distance = abs(player_x - self.x)
            if distance < self.detection_range:
                # Start charging
                self.is_charging = True
                self.move_speed = self.charge_speed
                self.direction = 1 if player_x > self.x else -1
            else:
                self.is_charging = False
                self.move_speed = self.normal_speed
        
        # Move
        self.x += self.move_speed * self.direction * delta_time
        
        # Patrol bounds (stop charge at edge)
        distance_from_spawn = abs(self.x - self.spawn_x)
        if distance_from_spawn > self.patrol_range:
            self.direction *= -1
            self.is_charging = False
            self.move_speed = self.normal_speed
            self.charge_cooldown = 2.0
            
        self.animation_time += delta_time
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        if not self.alive:
            return
            
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if screen_x < -100 or screen_x > 1200:
            return
            
        painter.save()
        
        center_x = screen_x + self.width / 2
        center_y = screen_y + self.height / 2
        
        # Body color changes when charging
        if self.is_charging:
            body_color = QColor(255, 50, 50)  # Red when charging
            glow = QRadialGradient(center_x, center_y, 25)
            glow.setColorAt(0.0, QColor(255, 100, 100, 150))
            glow.setColorAt(1.0, QColor(255, 50, 50, 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center_x - 25, center_y - 25, 50, 50)
        else:
            body_color = QColor(150, 100, 150)  # Purple when idle
        
        # Main body (bull-like)
        painter.setBrush(QBrush(body_color))
        painter.setPen(QPen(QColor(100, 50, 100), 2))
        painter.drawEllipse(center_x - 16, center_y - 12, 32, 24)
        
        # Horns
        horn_color = QColor(200, 200, 200)
        painter.setBrush(QBrush(horn_color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        horn_offset = 12 if self.direction > 0 else -12
        # Left horn
        painter.drawPolygon(QPolygonF([
            QPointF(center_x + horn_offset, center_y - 10),
            QPointF(center_x + horn_offset + (8 * self.direction), center_y - 18),
            QPointF(center_x + horn_offset + (4 * self.direction), center_y - 8)
        ]))
        
        # Eyes (angry red)
        painter.setBrush(QBrush(QColor(255, 0, 0) if self.is_charging else QColor(100, 50, 50)))
        painter.drawEllipse(center_x + (5 * self.direction) - 3, center_y - 5, 6, 6)
        
        painter.restore()
        
        if self.health < self.max_health:
            self._draw_health_bar(painter, screen_x, screen_y - 10)


class BomberEnemy(Enemy):
    """Enemy that explodes when player gets close - NEW!"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, patrol_range=80)
        
        self.move_speed = 40.0
        self.fuse_time = 0.0
        self.is_triggered = False
        self.explosion_range = 80.0
        self.trigger_range = 100.0
        self.explosion_delay = 2.0
        self.health = 1
        self.max_health = 1
        self.width = 30
        self.height = 30
        
    def update(self, delta_time: float, player_x: float = None, player_y: float = None):
        if not self.alive:
            return
        
        # Check if player is in trigger range
        if player_x is not None and player_y is not None and not self.is_triggered:
            distance = math.sqrt((player_x - self.x) ** 2 + (player_y - self.y) ** 2)
            if distance < self.trigger_range:
                self.is_triggered = True
                
        if self.is_triggered:
            # Fuse countdown
            self.fuse_time += delta_time
            if self.fuse_time >= self.explosion_delay:
                # Explode!
                self.alive = False
                return
        else:
            # Normal patrol
            self.x += self.move_speed * self.direction * delta_time
            distance_from_spawn = abs(self.x - self.spawn_x)
            if distance_from_spawn > self.patrol_range:
                self.direction *= -1
                
        self.animation_time += delta_time
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        if not self.alive:
            return
            
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if screen_x < -100 or screen_x > 1200:
            return
            
        painter.save()
        
        center_x = screen_x + self.width / 2
        center_y = screen_y + self.height / 2
        
        # Body (bomb shape)
        body_color = QColor(50, 50, 50) if not self.is_triggered else QColor(100, 0, 0)
        painter.setBrush(QBrush(body_color))
        painter.setPen(QPen(QColor(30, 30, 30), 2))
        
        # Bomb sphere
        painter.drawEllipse(center_x - 12, center_y - 12, 24, 24)
        
        # Fuse on top
        fuse_color = QColor(150, 100, 50)
        painter.setBrush(QBrush(fuse_color))
        painter.drawRect(center_x - 2, center_y - 18, 4, 8)
        
        # Spark at fuse tip (if triggered)
        if self.is_triggered:
            spark_size = 4 + math.sin(self.animation_time * 20) * 2
            spark_color = QColor(255, 150, 0)
            painter.setBrush(QBrush(spark_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center_x - spark_size/2, center_y - 20 - spark_size/2, spark_size, spark_size)
            
            # Flashing effect
            if int(self.fuse_time * 6) % 2 == 0:
                flash_color = QColor(255, 0, 0, 100)
                painter.setBrush(QBrush(flash_color))
                painter.drawEllipse(center_x - 18, center_y - 18, 36, 36)
        
        painter.restore()
        
    def should_explode(self) -> bool:
        """Check if bomb should explode."""
        return self.is_triggered and self.fuse_time >= self.explosion_delay
        
    def get_explosion_radius(self) -> float:
        """Get explosion damage radius."""
        return self.explosion_range


class SpinEnemy(Enemy):
    """Enemy that spins in place (existing enemy kept for compatibility)."""
    
    def __init__(self, x: float, y: float):
        """Initialize spin enemy."""
        super().__init__(x, y, patrol_range=0)  # Doesn't patrol
        
        self.move_speed = 0  # Stationary
        self.spin_speed = 180.0  # Degrees per second
        self.spin_angle = 0.0
        self.health = 3
        self.max_health = 3
        
    def update(self, delta_time: float):
        """Update spinning animation."""
        if not self.alive:
            return
            
        self.animation_time += delta_time
        self.spin_angle += self.spin_speed * delta_time
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render spinning enemy."""
        if not self.alive:
            return
            
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if screen_x < -100 or screen_x > 1200:
            return
            
        painter.save()
        
        center_x = screen_x + self.width / 2
        center_y = screen_y + self.height / 2
        
        # Rotate
        painter.translate(center_x, center_y)
        painter.rotate(self.spin_angle)
        painter.translate(-center_x, -center_y)
        
        # Draw core
        core_color = QColor(100, 50, 150)
        painter.setBrush(QBrush(core_color))
        painter.setPen(QPen(QColor(70, 30, 120), 2))
        painter.drawEllipse(center_x - 12, center_y - 12, 24, 24)
        
        # Draw rotating blades
        blade_color = QColor(150, 100, 200)
        painter.setBrush(QBrush(blade_color))
        
        for i in range(4):
            angle = (i * 90) * math.pi / 180
            blade_x = center_x + math.cos(angle) * 18
            blade_y = center_y + math.sin(angle) * 18
            
            painter.drawEllipse(blade_x - 6, blade_y - 6, 12, 12)
            
        painter.restore()
        
        # Draw health bar if damaged
        if self.health < self.max_health:
            self._draw_health_bar(painter, screen_x, screen_y - 10)
