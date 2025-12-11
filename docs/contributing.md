# Contributing to Macan Run

Thank you for your interest in improving Macan Run! This guide will help you understand how to extend and modify the game.

## Code Style Guidelines

### Python Style

Follow PEP 8 with these specifics:

```python
# Good: Clear, typed function signatures
def update_entity(self, entity: Entity, delta_time: float) -> None:
    """Update entity state with delta time integration."""
    entity.x += entity.vx * delta_time
    
# Good: Descriptive variable names for important values
player_screen_position = player.x - camera.x
health_percentage = player.health / player.max_health

# Good: Concise names in loops
for i, enemy in enumerate(self.enemies):
    if self._check_collision(player, enemy):
        self._handle_enemy_collision(player, enemy)
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `PhysicsEngine`, `LevelManager`)
- **Functions/Methods**: `snake_case` (e.g., `update_camera`, `check_collision`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_FALL_SPEED`, `TILE_SIZE`)
- **Private methods**: `_snake_case` (e.g., `_resolve_collision`)

### Documentation

Every class and public method should have a docstring:

```python
class Enemy:
    """Enemy entity with patrol AI.
    
    Attributes:
        x, y: Position in world coordinates
        patrol_range: Distance from spawn point before turning
        direction: Current movement direction (1=right, -1=left)
    """
    
    def update(self, delta_time: float) -> None:
        """Update enemy state including movement and animation.
        
        Args:
            delta_time: Time elapsed since last frame in seconds
        """
```

## Adding New Features

### 1. Adding a New Enemy Type

Create a new class in `game/enemy.py` or a new file:

```python
class FlyingEnemy(Enemy):
    """Enemy that flies in sine wave pattern."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.flight_height = 100.0
        self.wave_speed = 2.0
        self.time = 0.0
        
    def update(self, delta_time: float):
        """Update flying pattern."""
        self.time += delta_time
        
        # Sine wave flight
        self.x += self.move_speed * self.direction * delta_time
        self.y = self.spawn_y + math.sin(self.time * self.wave_speed) * self.flight_height
        
        # Check patrol bounds
        if abs(self.x - self.spawn_x) > self.patrol_range:
            self.direction *= -1
            
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render flying enemy with wings."""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Draw body
        painter.setBrush(QBrush(QColor(100, 100, 200)))
        painter.drawEllipse(screen_x, screen_y, self.width, self.height)
        
        # Draw wings
        wing_offset = math.sin(self.time * 10) * 5
        painter.drawEllipse(screen_x - 10, screen_y + wing_offset, 15, 8)
        painter.drawEllipse(screen_x + 25, screen_y + wing_offset, 15, 8)
```

Then register in level manager:

```python
# In level_manager.py _spawn_entities()
elif tile == 'F':  # Flying enemy marker
    self.enemies.append(FlyingEnemy(x, y))
```

### 2. Adding a Power-Up System

Create `game/powerup.py`:

```python
from enum import Enum
from PySide6.QtGui import QPainter, QColor, QBrush
import math

class PowerUpType(Enum):
    SPEED = "speed"
    SHIELD = "shield"
    DOUBLE_JUMP = "double_jump"
    HEALTH = "health"

class PowerUp:
    """Collectible power-up entity."""
    
    def __init__(self, x: float, y: float, type: PowerUpType):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.type = type
        self.animation_time = 0.0
        
        # Type-specific properties
        self.colors = {
            PowerUpType.SPEED: QColor(100, 200, 255),
            PowerUpType.SHIELD: QColor(200, 200, 100),
            PowerUpType.DOUBLE_JUMP: QColor(200, 100, 255),
            PowerUpType.HEALTH: QColor(255, 100, 100)
        }
        
    def update(self, delta_time: float):
        """Update animation."""
        self.animation_time += delta_time
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render power-up."""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Floating animation
        float_y = screen_y + math.sin(self.animation_time * 3) * 5
        
        # Draw glow
        glow_color = self.colors[self.type]
        glow_color.setAlpha(100)
        painter.setBrush(QBrush(glow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(screen_x - 5, float_y - 5, self.width + 10, self.height + 10)
        
        # Draw main icon
        painter.setBrush(QBrush(self.colors[self.type]))
        painter.drawRect(screen_x, float_y, self.width, self.height)
        
    def apply_to_player(self, player):
        """Apply power-up effect to player."""
        if self.type == PowerUpType.SPEED:
            player.move_speed *= 1.5
            player.speed_boost_time = 10.0  # 10 seconds
        elif self.type == PowerUpType.SHIELD:
            player.has_shield = True
            player.shield_time = 15.0
        elif self.type == PowerUpType.DOUBLE_JUMP:
            player.max_jumps = 3  # Triple jump!
        elif self.type == PowerUpType.HEALTH:
            player.heal(1)
```

Add to level manager and collision detection:

```python
# In level_manager.py
self.powerups: List[PowerUp] = []

# In level loading
elif tile == 'S':  # Speed power-up
    self.powerups.append(PowerUp(x, y, PowerUpType.SPEED))

# In engine.py _check_collisions()
for powerup in self.level_manager.powerups[:]:
    if self.physics.check_collision(player, powerup):
        powerup.apply_to_player(player)
        self.level_manager.powerups.remove(powerup)
        self._play_sfx("powerup")
```

### 3. Adding Particle Effects

Create `game/particles.py`:

```python
import random
import math
from typing import List
from PySide6.QtGui import QPainter, QColor, QBrush
from PySide6.QtCore import Qt

class Particle:
    """Single particle in a particle system."""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 color: QColor, lifetime: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        self.size = 4
        
    def update(self, delta_time: float, gravity: float = 300.0) -> bool:
        """Update particle. Returns False when particle should be removed."""
        self.age += delta_time
        
        if self.age >= self.lifetime:
            return False
            
        # Physics
        self.vy += gravity * delta_time
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        
        return True
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render particle."""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Fade out over lifetime
        alpha = int(255 * (1 - self.age / self.lifetime))
        color = QColor(self.color)
        color.setAlpha(alpha)
        
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(screen_x - self.size/2, screen_y - self.size/2, 
                          self.size, self.size)

class ParticleSystem:
    """Manages multiple particle effects."""
    
    def __init__(self):
        self.particles: List[Particle] = []
        
    def emit_burst(self, x: float, y: float, count: int = 10, 
                   color: QColor = QColor(255, 200, 0)):
        """Emit a burst of particles."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 100  # Bias upward
            lifetime = random.uniform(0.5, 1.5)
            
            self.particles.append(Particle(x, y, vx, vy, color, lifetime))
            
    def emit_trail(self, x: float, y: float, vx: float, vy: float,
                   color: QColor = QColor(200, 200, 200)):
        """Emit trail particle behind moving object."""
        offset_x = random.uniform(-5, 5)
        offset_y = random.uniform(-5, 5)
        trail_vx = -vx * 0.3 + random.uniform(-20, 20)
        trail_vy = -vy * 0.3 + random.uniform(-20, 20)
        
        self.particles.append(Particle(
            x + offset_x, y + offset_y, 
            trail_vx, trail_vy, 
            color, 0.5
        ))
        
    def update(self, delta_time: float):
        """Update all particles, removing dead ones."""
        self.particles = [p for p in self.particles 
                         if p.update(delta_time)]
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render all particles."""
        for particle in self.particles:
            particle.render(painter, camera_x, camera_y)
```

Integrate into game engine:

```python
# In engine.py __init__
from game.particles import ParticleSystem
self.particles = ParticleSystem()

# In update()
self.particles.update(self.delta_time)

# In render() - after entities, before HUD
self.particles.render(painter, self.camera_x, self.camera_y)

# When collecting coin
self.particles.emit_burst(coin.x, coin.y, count=15, 
                         color=QColor(255, 215, 0))

# When player is moving fast
if abs(player.vx) > 200:
    self.particles.emit_trail(player.x, player.y + player.height, 
                             player.vx, player.vy)
```

### 4. Adding a Level Editor

Create `tools/level_editor.py`:

```python
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtGui import QPainter, QColor, QBrush
from PySide6.QtCore import Qt, QPoint

class LevelEditorWidget(QWidget):
    """Visual level editor widget."""
    
    def __init__(self):
        super().__init__()
        self.tile_size = 32
        self.grid_width = 40
        self.grid_height = 15
        self.tiles = [['.' for _ in range(self.grid_width)] 
                      for _ in range(self.grid_height)]
        self.current_tile = '#'
        
    def paintEvent(self, event):
        """Render grid."""
        painter = QPainter(self)
        
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                x = col * self.tile_size
                y = row * self.tile_size
                
                tile = self.tiles[row][col]
                color = self._get_tile_color(tile)
                
                painter.fillRect(x, y, self.tile_size, self.tile_size, color)
                painter.drawRect(x, y, self.tile_size, self.tile_size)
                
    def mousePressEvent(self, event):
        """Place tile on click."""
        col = event.pos().x() // self.tile_size
        row = event.pos().y() // self.tile_size
        
        if 0 <= row < self.grid_height and 0 <= col < self.grid_width:
            self.tiles[row][col] = self.current_tile
            self.update()
            
    def export_level(self, filename: str):
        """Export to ASCII file."""
        with open(filename, 'w') as f:
            for row in self.tiles:
                f.write(''.join(row) + '\n')
```

## Testing Your Changes

### Manual Testing Checklist

Before submitting changes:

- [ ] Game starts without errors
- [ ] Player can move, jump, and collect items
- [ ] Collisions work correctly
- [ ] No visual glitches
- [ ] Performance remains at 60 FPS
- [ ] Save/load still works
- [ ] All existing features still work

### Automated Tests

Create tests in `tests/` directory:

```python
# tests/test_physics.py
import unittest
from core.physics import PhysicsEngine

class TestPhysics(unittest.TestCase):
    def setUp(self):
        self.physics = PhysicsEngine()
        
    def test_gravity_application(self):
        """Test that gravity increases velocity."""
        initial_vy = 0
        final_vy = self.physics.gravity * 0.1  # 0.1 second
        self.assertAlmostEqual(final_vy, 98.0, places=1)
        
    def test_aabb_collision(self):
        """Test AABB collision detection."""
        class MockEntity:
            def __init__(self, x, y, w, h):
                self.x, self.y = x, y
                self.width, self.height = w, h
                
        e1 = MockEntity(0, 0, 10, 10)
        e2 = MockEntity(5, 5, 10, 10)
        e3 = MockEntity(20, 20, 10, 10)
        
        self.assertTrue(self.physics.check_collision(e1, e2))
        self.assertFalse(self.physics.check_collision(e1, e3))
```

Run tests:
```bash
python -m unittest discover tests/
```

## Performance Guidelines

### Do's ✅

- Cache expensive calculations
- Use early returns to skip unnecessary work
- Batch similar operations
- Profile before optimizing

```python
# Good: Early return
def render(self, painter, camera_x, camera_y):
    screen_x = self.x - camera_x
    if screen_x < -100 or screen_x > 1200:
        return  # Off-screen, skip rendering
    # ... rest of render code

# Good: Caching
class TileMap:
    def __init__(self):
        self._collision_cache = {}
        
    def get_tile_colliders(self, region):
        if region in self._collision_cache:
            return self._collision_cache[region]
        # ... calculate colliders
        self._collision_cache[region] = colliders
        return colliders
```

### Don'ts ❌

- Don't create objects in hot paths
- Don't use string formatting in tight loops
- Don't call expensive functions unnecessarily

```python
# Bad: Creating objects every frame
def update(self):
    for entity in self.entities:
        color = QColor(255, 0, 0)  # Creates new object every iteration!
        
# Good: Reuse objects
class EntityManager:
    def __init__(self):
        self.red_color = QColor(255, 0, 0)  # Create once
        
    def update(self):
        for entity in self.entities:
            # Use cached color
```

## Submitting Changes

### Commit Message Format

```
[Component] Brief description

Detailed explanation of what changed and why.

- Bullet points for multiple changes
- Reference issue numbers if applicable
```

Examples:
```
[Physics] Fix collision detection edge case

Players were sometimes falling through thin platforms.
Added epsilon value to collision threshold.

[Renderer] Optimize tile rendering

- Batch tiles by row
- Skip off-screen tiles earlier
- Cache frequently used colors

Performance improvement: ~30% faster rendering
```

## Common Issues and Solutions

### Issue: New entity not appearing

**Solution**: Make sure to:
1. Add to level manager's entity list
2. Call `update()` in game loop
3. Call `render()` in render loop
4. Check camera culling bounds

### Issue: Physics feels wrong

**Solution**: Check:
1. Delta time is being used correctly
2. Constants are appropriate scale (pixel-based)
3. Frame rate is stable at 60 FPS
4. Velocity is being clamped appropriately

### Issue: Memory leak

**Solution**:
1. Remove destroyed entities from lists
2. Clear particle systems of dead particles
3. Unregister event listeners
4. Clear caches periodically

## Resources

- **PySide6 Docs**: https://doc.qt.io/qtforpython/
- **QPainter Reference**: https://doc.qt.io/qt-6/qpainter.html
- **Game Dev Patterns**: https://gameprogrammingpatterns.com/

## Questions?

For questions or discussions:
- Check existing documentation first
- Review similar code in the project
- Test your changes thoroughly
- Keep changes focused and incremental

---

Happy coding! 🎮
