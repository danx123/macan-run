"""
Particle System - Visual effects with particles
Creates explosions, trails, and various particle effects
"""
import random
import math
from typing import List
from PySide6.QtGui import QPainter, QColor, QBrush, QPen
from PySide6.QtCore import Qt


class Particle:
    """Single particle in a particle system."""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 color: QColor, lifetime: float, size: float = 4.0):
        """
        Initialize particle.
        
        Args:
            x, y: Initial position
            vx, vy: Initial velocity
            color: Particle color
            lifetime: How long particle lives (seconds)
            size: Particle radius
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        self.size = size
        self.initial_size = size
        
    def update(self, delta_time: float, gravity: float = 300.0) -> bool:
        """
        Update particle physics.
        
        Args:
            delta_time: Time elapsed
            gravity: Gravity strength
            
        Returns:
            True if particle is still alive, False if expired
        """
        self.age += delta_time
        
        # Check if expired
        if self.age >= self.lifetime:
            return False
            
        # Apply gravity
        self.vy += gravity * delta_time
        
        # Update position
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        
        # Shrink over time
        life_ratio = self.age / self.lifetime
        self.size = self.initial_size * (1 - life_ratio * 0.5)
        
        return True
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render particle with fade-out effect."""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Calculate alpha based on remaining lifetime
        life_ratio = self.age / self.lifetime
        alpha = int(255 * (1 - life_ratio))
        
        # Create faded color
        color = QColor(self.color)
        color.setAlpha(alpha)
        
        # Draw particle
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            int(screen_x - self.size/2), 
            int(screen_y - self.size/2),
            int(self.size), 
            int(self.size)
        )


class ParticleSystem:
    """Manages multiple particle effects."""
    
    def __init__(self):
        """Initialize particle system."""
        self.particles: List[Particle] = []
        self.max_particles = 500  # Performance limit
        
    def emit_burst(self, x: float, y: float, count: int = 10, 
                   color: QColor = None, speed_range: tuple = (50, 200)):
        """
        Emit explosion burst of particles.
        
        Args:
            x, y: Origin point
            count: Number of particles
            color: Particle color (default: yellow)
            speed_range: (min, max) speed range
        """
        if color is None:
            color = QColor(255, 200, 0)
            
        for _ in range(count):
            # Random direction
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 100  # Bias upward
            
            # Random lifetime
            lifetime = random.uniform(0.5, 1.5)
            
            # Random size
            size = random.uniform(3, 7)
            
            # Slight color variation
            r = min(255, color.red() + random.randint(-20, 20))
            g = min(255, color.green() + random.randint(-20, 20))
            b = min(255, color.blue() + random.randint(-20, 20))
            particle_color = QColor(r, g, b)
            
            self._add_particle(Particle(x, y, vx, vy, particle_color, lifetime, size))
            
    def emit_trail(self, x: float, y: float, vx: float, vy: float,
                   color: QColor = None, intensity: int = 1):
        """
        Emit trail particles behind moving object.
        
        Args:
            x, y: Current position
            vx, vy: Current velocity
            color: Trail color (default: white)
            intensity: Number of particles to emit
        """
        if color is None:
            color = QColor(200, 200, 200)
            
        for _ in range(intensity):
            # Offset from center
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)
            
            # Velocity opposite to movement
            trail_vx = -vx * 0.3 + random.uniform(-20, 20)
            trail_vy = -vy * 0.3 + random.uniform(-20, 20)
            
            lifetime = random.uniform(0.3, 0.8)
            size = random.uniform(2, 4)
            
            self._add_particle(Particle(
                x + offset_x, y + offset_y,
                trail_vx, trail_vy,
                color, lifetime, size
            ))
            
    def emit_jump_dust(self, x: float, y: float, direction: int = 0):
        """
        Emit dust particles when jumping/landing.
        
        Args:
            x, y: Position
            direction: -1 for left, 1 for right, 0 for both sides
        """
        dust_color = QColor(150, 150, 150)
        
        count = 8
        for i in range(count):
            # Spread particles to sides
            if direction == 0:
                angle = random.uniform(-math.pi, 0)  # Downward spread
            elif direction < 0:
                angle = random.uniform(-math.pi * 0.8, -math.pi * 0.2)
            else:
                angle = random.uniform(-math.pi * 0.2, math.pi * 0.2)
                
            speed = random.uniform(30, 80)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            lifetime = random.uniform(0.3, 0.6)
            size = random.uniform(3, 6)
            
            self._add_particle(Particle(x, y, vx, vy, dust_color, lifetime, size))
            
    def emit_coin_sparkle(self, x: float, y: float):
        """Emit sparkle effect when collecting coin."""
        sparkle_color = QColor(255, 223, 0)
        
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 150)
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            lifetime = random.uniform(0.4, 0.8)
            size = random.uniform(2, 5)
            
            self._add_particle(Particle(x, y, vx, vy, sparkle_color, lifetime, size))
            
    def emit_damage_effect(self, x: float, y: float):
        """Emit red particles when taking damage."""
        damage_color = QColor(255, 50, 50)
        
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 200)
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 50
            
            lifetime = random.uniform(0.3, 0.7)
            size = random.uniform(3, 6)
            
            self._add_particle(Particle(x, y, vx, vy, damage_color, lifetime, size))
            
    def emit_enemy_death(self, x: float, y: float):
        """Emit explosion when enemy dies."""
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 250)
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Mix of red and orange
            color = QColor(
                random.randint(200, 255),
                random.randint(50, 150),
                random.randint(0, 50)
            )
            
            lifetime = random.uniform(0.5, 1.2)
            size = random.uniform(4, 8)
            
            self._add_particle(Particle(x, y, vx, vy, color, lifetime, size))
            
    def _add_particle(self, particle: Particle):
        """Add particle with limit check."""
        if len(self.particles) < self.max_particles:
            self.particles.append(particle)
            
    def update(self, delta_time: float):
        """Update all particles, removing dead ones."""
        self.particles = [
            p for p in self.particles 
            if p.update(delta_time)
        ]
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render all active particles."""
        for particle in self.particles:
            particle.render(painter, camera_x, camera_y)
            
    def clear(self):
        """Remove all particles."""
        self.particles.clear()
        
    def get_particle_count(self) -> int:
        """Get current number of active particles."""
        return len(self.particles)