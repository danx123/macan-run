"""
Power-Up System - Collectible power-ups with various effects
FIXED: Much larger collision box (48x48) and enhanced visibility
Now as easy to collect as coins!
"""
import math
from enum import Enum
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient, QFont
from PySide6.QtCore import Qt, QRectF


class PowerUpType(Enum):
    """Types of power-ups available."""
    SPEED = "speed"
    SHIELD = "shield"
    TRIPLE_JUMP = "triple_jump"
    HEALTH = "health"


class PowerUp:
    """Collectible power-up entity with visual effects."""
    
    def __init__(self, x: float, y: float, powerup_type: PowerUpType):
        """
        Initialize power-up.
        
        Args:
            x, y: World position
            powerup_type: Type of power-up effect
        """
        self.x = x
        self.y = y
        # MUCH LARGER collision box - same as tile size for easy pickup!
        self.width = 48  # Same as tile size (easy to collect)
        self.height = 48  # Same as tile size (easy to collect)
        self.type = powerup_type
        
        # Animation
        self.animation_time = 0.0
        self.float_offset = 0.0
        self.rotation = 0.0
        self.pulse_scale = 1.0
        
        # Visual properties per type
        self.properties = {
            PowerUpType.SPEED: {
                'color': QColor(100, 200, 255),
                'symbol': '⚡',
                'name': 'Speed Boost'
            },
            PowerUpType.SHIELD: {
                'color': QColor(200, 200, 100),
                'symbol': '🛡',
                'name': 'Shield'
            },
            PowerUpType.TRIPLE_JUMP: {
                'color': QColor(200, 100, 255),
                'symbol': '⬆',
                'name': 'Triple Jump'
            },
            PowerUpType.HEALTH: {
                'color': QColor(255, 100, 100),
                'symbol': '+',
                'name': 'Health'
            }
        }
        
    def update(self, delta_time: float):
        """Update power-up animation."""
        self.animation_time += delta_time
        
        # Floating animation (BIGGER movement for visibility)
        self.float_offset = math.sin(self.animation_time * 2.5) * 12
        
        # Rotation animation (slower, smoother)
        self.rotation = self.animation_time * 60  # degrees per second
        
        # Pulsing scale for attention
        self.pulse_scale = 1.0 + math.sin(self.animation_time * 4) * 0.15
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render power-up with VERY visible glow effect."""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y + self.float_offset
        
        # Skip if off-screen
        if screen_x < -100 or screen_x > 1200:
            return
            
        painter.save()
        
        props = self.properties[self.type]
        center_x = screen_x + self.width / 2
        center_y = screen_y + self.height / 2
        
        # Draw VERY LARGE pulsing glow (multiple layers)
        pulse = self.pulse_scale
        
        # Outer glow (biggest)
        glow_radius_outer = self.width * 1.8 * pulse
        gradient_outer = QRadialGradient(center_x, center_y, glow_radius_outer)
        glow_color_outer = QColor(props['color'])
        glow_color_outer.setAlpha(80)
        gradient_outer.setColorAt(0.0, glow_color_outer)
        glow_color_outer.setAlpha(0)
        gradient_outer.setColorAt(1.0, glow_color_outer)
        
        painter.setBrush(QBrush(gradient_outer))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            center_x - glow_radius_outer, 
            center_y - glow_radius_outer,
            glow_radius_outer * 2, 
            glow_radius_outer * 2
        )
        
        # Middle glow
        glow_radius_mid = self.width * 1.3 * pulse
        gradient_mid = QRadialGradient(center_x, center_y, glow_radius_mid)
        glow_color_mid = QColor(props['color'])
        glow_color_mid.setAlpha(150)
        gradient_mid.setColorAt(0.0, glow_color_mid)
        glow_color_mid.setAlpha(0)
        gradient_mid.setColorAt(1.0, glow_color_mid)
        
        painter.setBrush(QBrush(gradient_mid))
        painter.drawEllipse(
            center_x - glow_radius_mid, 
            center_y - glow_radius_mid,
            glow_radius_mid * 2, 
            glow_radius_mid * 2
        )
        
        # Rotate for effect
        painter.translate(center_x, center_y)
        painter.rotate(self.rotation)
        painter.scale(pulse, pulse)
        painter.translate(-center_x, -center_y)
        
        # Draw main icon box (LARGE and VISIBLE)
        painter.setBrush(QBrush(props['color']))
        painter.setPen(QPen(QColor(255, 255, 255), 4))
        painter.drawRoundedRect(
            screen_x + 6, screen_y + 6,
            self.width - 12, self.height - 12,
            10, 10
        )
        
        # Draw inner shine
        inner_color = QColor(255, 255, 255, 180)
        painter.setBrush(QBrush(inner_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(
            screen_x + 14, screen_y + 14,
            self.width - 28, self.height - 28,
            8, 8
        )
        
        painter.restore()
        
        # Draw symbol (not rotated, LARGE)
        painter.save()
        painter.setPen(QColor(50, 50, 50))  # Dark outline for contrast
        font = QFont("Sans Serif", 26, QFont.Weight.Bold)
        painter.setFont(font)
        
        text_rect = QRectF(screen_x, screen_y, self.width, self.height)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, props['symbol'])
        
        painter.restore()
        
    def apply_to_player(self, player):
        """
        Apply power-up effect to player.
        
        Args:
            player: Player object to apply effect to
            
        Returns:
            bool: True if effect was applied successfully
        """
        # Ensure player has power_up_effects dict
        if not hasattr(player, 'power_up_effects'):
            player.power_up_effects = {}
        if not hasattr(player, 'has_shield'):
            player.has_shield = False
            
        print(f"🎁 Power-up collected: {self.properties[self.type]['name']}")
        
        if self.type == PowerUpType.SPEED:
            # Speed boost for 10 seconds
            player.move_speed = 400.0  # Faster movement
            player.power_up_effects['speed'] = 10.0
            print(f"  ⚡ Speed increased! {player.move_speed} pixels/s for 10s")
            return True
            
        elif self.type == PowerUpType.SHIELD:
            # Shield for 15 seconds
            player.power_up_effects['shield'] = 15.0
            player.has_shield = True
            print("  🛡️ Shield activated for 15s!")
            return True
            
        elif self.type == PowerUpType.TRIPLE_JUMP:
            # Triple jump ability for 20 seconds
            player.max_jumps = 3
            player.jumps_remaining = 3
            player.power_up_effects['triple_jump'] = 20.0
            print("  ⬆⬆⬆ Triple jump activated for 20s!")
            return True
            
        elif self.type == PowerUpType.HEALTH:
            # Restore 1 health (instant, no timer)
            if player.health < player.max_health:
                player.heal(1)
                print(f"  ❤️ Health restored! {player.health}/{player.max_health}")
                return True
            else:
                print(f"  ❤️ Health already full! {player.health}/{player.max_health}")
                return False  # Don't collect if health is full
                
        return False


class PowerUpManager:
    """Manages power-up timers and effects on player."""
    
    def __init__(self, player):
        """Initialize manager with player reference."""
        self.player = player
        
        # Ensure player has power-up tracking
        if not hasattr(player, 'power_up_effects'):
            player.power_up_effects = {}
            player.has_shield = False
            
    def update(self, delta_time: float):
        """
        Update active power-up timers.
        
        Args:
            delta_time: Time elapsed since last frame
        """
        effects_to_remove = []
        
        for effect_name, time_remaining in self.player.power_up_effects.items():
            time_remaining -= delta_time
            
            if time_remaining <= 0:
                # Effect expired
                print(f"⏱️ Power-up expired: {effect_name}")
                self._remove_effect(effect_name)
                effects_to_remove.append(effect_name)
            else:
                # Update timer
                self.player.power_up_effects[effect_name] = time_remaining
                
        # Remove expired effects
        for effect_name in effects_to_remove:
            del self.player.power_up_effects[effect_name]
            
    def _remove_effect(self, effect_name: str):
        """Remove effect and restore default values."""
        if effect_name == 'speed':
            # Restore to base speed
            self.player.move_speed = self.player.base_move_speed
            print(f"  Speed restored to {self.player.move_speed}")
        elif effect_name == 'shield':
            self.player.has_shield = False
            print("  Shield expired")
        elif effect_name == 'triple_jump':
            # Restore to base jumps
            self.player.max_jumps = self.player.base_max_jumps
            print(f"  Jumps restored to {self.player.max_jumps}")
            
    def render_active_effects(self, painter: QPainter, x: int, y: int):
        """
        Render active power-up indicators.
        (This is now handled by HUD, but kept for compatibility)
        
        Args:
            painter: QPainter object
            x, y: Position to start drawing
        """
        # This method is no longer used as HUD handles rendering
        pass
