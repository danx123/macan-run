"""
Particle System - Visual effects with particles
OPTIMIZED: Better culling and batch rendering

MIGRATED: Per-frame particle physics (gravity, integration, size/age
decay) now runs as a single batched call into the macan_physics_native
Rust extension instead of one Python method call per particle, falling
back to the original per-particle Python update if the extension isn't
installed yet.
"""
import random
import math
from typing import List
from PySide6.QtGui import QPainter, QColor, QBrush, QPen
from PySide6.QtCore import Qt

try:
    import macan_physics_native as _native
    _NATIVE_PHYSICS = True
    print("using macan physics native")
except ImportError:
    _native = None
    _NATIVE_PHYSICS = False


class Particle:
    """Single particle in a particle system."""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 color: QColor, lifetime: float, size: float = 4.0):
        """Initialize particle."""
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
        """Update particle physics (pure-Python fallback path)."""
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
    """Manages multiple particle effects with optimizations."""
    
    def __init__(self):
        """Initialize particle system."""
        self.particles: List[Particle] = []
        self.max_particles = 300  # Reduced from 500 for performance
        self.gravity = 300.0  # Matches the default used by Particle.update()
        
    def emit_burst(self, x: float, y: float, count: int = 10, 
                   color: QColor = None, speed_range: tuple = (50, 200)):
        """Emit explosion burst of particles."""
        if color is None:
            color = QColor(255, 200, 0)
        
        # Limit burst size for performance
        count = min(count, 20)
            
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 100
            
            lifetime = random.uniform(0.5, 1.2)
            size = random.uniform(3, 6)
            
            r = min(255, color.red() + random.randint(-20, 20))
            g = min(255, color.green() + random.randint(-20, 20))
            b = min(255, color.blue() + random.randint(-20, 20))
            particle_color = QColor(r, g, b)
            
            self._add_particle(Particle(x, y, vx, vy, particle_color, lifetime, size))
            
    def emit_trail(self, x: float, y: float, vx: float, vy: float,
                   color: QColor = None, intensity: int = 1):
        """Emit trail particles behind moving object."""
        if color is None:
            color = QColor(200, 200, 200)
            
        for _ in range(intensity):
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)
            
            trail_vx = -vx * 0.3 + random.uniform(-20, 20)
            trail_vy = -vy * 0.3 + random.uniform(-20, 20)
            
            lifetime = random.uniform(0.3, 0.6)
            size = random.uniform(2, 4)
            
            self._add_particle(Particle(
                x + offset_x, y + offset_y,
                trail_vx, trail_vy,
                color, lifetime, size
            ))
            
    def emit_jump_dust(self, x: float, y: float, direction: int = 0):
        """Emit dust particles when jumping/landing."""
        dust_color = QColor(150, 150, 150)
        
        count = 5  # Reduced from 8 for performance
        for i in range(count):
            if direction == 0:
                angle = random.uniform(-math.pi, 0)
            elif direction < 0:
                angle = random.uniform(-math.pi * 0.8, -math.pi * 0.2)
            else:
                angle = random.uniform(-math.pi * 0.2, math.pi * 0.2)
                
            speed = random.uniform(30, 80)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            lifetime = random.uniform(0.3, 0.5)
            size = random.uniform(3, 5)
            
            self._add_particle(Particle(x, y, vx, vy, dust_color, lifetime, size))
            
    def emit_coin_sparkle(self, x: float, y: float):
        """Emit sparkle effect when collecting coin."""
        sparkle_color = QColor(255, 223, 0)
        
        count = 8  # Reduced from 12 for performance
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 120)
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            lifetime = random.uniform(0.3, 0.6)
            size = random.uniform(2, 4)
            
            self._add_particle(Particle(x, y, vx, vy, sparkle_color, lifetime, size))
            
    def emit_damage_effect(self, x: float, y: float):
        """Emit red particles when taking damage."""
        damage_color = QColor(255, 50, 50)
        
        count = 10  # Reduced from 15 for performance
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 180)
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 50
            
            lifetime = random.uniform(0.3, 0.6)
            size = random.uniform(3, 5)
            
            self._add_particle(Particle(x, y, vx, vy, damage_color, lifetime, size))
            
    def emit_enemy_death(self, x: float, y: float):
        """Emit explosion when enemy dies."""
        count = 12  # Reduced from 20 for performance
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 200)
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            color = QColor(
                random.randint(200, 255),
                random.randint(50, 150),
                random.randint(0, 50)
            )
            
            lifetime = random.uniform(0.5, 1.0)
            size = random.uniform(4, 7)
            
            self._add_particle(Particle(x, y, vx, vy, color, lifetime, size))
            
    def _add_particle(self, particle: Particle):
        """Add particle with limit check."""
        if len(self.particles) < self.max_particles:
            self.particles.append(particle)
            
    def update(self, delta_time: float):
        """Update all particles, removing dead ones."""
        if not self.particles:
            return

        if _NATIVE_PHYSICS:
            batch_input = [
                (p.x, p.y, p.vx, p.vy, p.age, p.lifetime, p.initial_size)
                for p in self.particles
            ]
            results = _native.particles_update_batch(batch_input, delta_time, self.gravity)

            alive_particles = []
            for particle, (new_x, new_y, new_vx, new_vy, new_size, new_age, alive) in zip(
                self.particles, results
            ):
                if alive:
                    particle.x = new_x
                    particle.y = new_y
                    particle.vx = new_vx
                    particle.vy = new_vy
                    particle.size = new_size
                    particle.age = new_age
                    alive_particles.append(particle)

            self.particles = alive_particles
        else:
            self.particles = [
                p for p in self.particles
                if p.update(delta_time)
            ]
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render all active particles with culling."""
        screen_width = painter.device().width()
        screen_height = painter.device().height()
        
        # Batch rendering setup
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Only render visible particles
        for particle in self.particles:
            screen_x = particle.x - camera_x
            screen_y = particle.y - camera_y
            
            # Cull off-screen particles
            if -50 < screen_x < screen_width + 50 and -50 < screen_y < screen_height + 50:
                particle.render(painter, camera_x, camera_y)
            
    def clear(self):
        """Remove all particles."""
        self.particles.clear()
        
    def get_particle_count(self) -> int:
        """Get current number of active particles."""
        return len(self.particles)
