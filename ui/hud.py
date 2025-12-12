"""
HUD - Heads Up Display
Displays score, health, coins, current level, and active power-ups
FIXED: Better power-up layout to prevent overlapping
"""
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient
from PySide6.QtCore import QRect, Qt, QRectF

class HUD:
    """Manages the Heads-Up Display rendering."""
    
    def __init__(self):
        # Fonts
        self.font_large = QFont("Segoe UI", 24, QFont.Weight.Bold)
        self.font_small = QFont("Segoe UI", 16)
        self.font_bold = QFont("Segoe UI", 18, QFont.Weight.Bold)
        self.font_tiny = QFont("Segoe UI", 11, QFont.Weight.Bold)
        
    def render(self, painter: QPainter, score: int, coins: int, health: int, 
               distance: int, level: str = "level1", power_up_effects: dict = None):
        """
        Render HUD elements.
        
        Args:
            painter: QPainter object
            score: Current score
            coins: Coins collected
            health: Player health
            distance: Distance traveled
            level: Current level name
            power_up_effects: Dict of active power-up effects with timers
        """
        window_width = painter.device().width()
        
        painter.save()
        
        # --- 1. LEVEL NAME (Top Center) ---
        level_text = level.replace("level", "LEVEL ").upper()
        
        painter.setFont(self.font_large)
        # Shadow effect
        painter.setPen(QColor(0, 0, 0, 150))
        painter.drawText(QRect(2, 12, window_width, 50), Qt.AlignmentFlag.AlignCenter, level_text)
        # Main text
        painter.setPen(QColor(255, 215, 0))  # Gold
        painter.drawText(QRect(0, 10, window_width, 50), Qt.AlignmentFlag.AlignCenter, level_text)
        
        # --- 2. Score & Coins (Top Left) ---
        painter.setFont(self.font_bold)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(20, 40, f"SCORE: {score:05d}")
        
        painter.setPen(QColor(255, 223, 0))  # Coin yellow
        painter.drawText(20, 70, f"💰 COINS: {coins}")
        
        # --- 3. Distance (Top Right - Optional) ---
        painter.setFont(self.font_small)
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(window_width - 150, 40, f"📍 {distance}m")
        
        # --- 4. Health Bar (Top Right) ---
        self._render_health(painter, health, window_width)
        
        # --- 5. Power-Up Status (HORIZONTAL layout below level name) ---
        if power_up_effects:
            self._render_power_up_status_horizontal(painter, power_up_effects, window_width)
        
        painter.restore()
        
    def _render_health(self, painter: QPainter, health: int, width: int):
        """Draw health hearts."""
        start_x = width - 140
        y = 60
        heart_size = 30
        gap = 10
        
        for i in range(3):
            x = start_x + i * (heart_size + gap)
            
            # Border
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            
            if i < health:
                # Full health (Red heart)
                painter.setBrush(QBrush(QColor(255, 50, 50)))
            else:
                # Empty health (Dark/transparent)
                painter.setBrush(QBrush(QColor(50, 0, 0, 100)))
                
            # Draw heart shape (simplified as rounded rect)
            painter.drawRoundedRect(x, y, heart_size, heart_size, 6, 6)
    
    def _render_power_up_status_horizontal(self, painter: QPainter, power_up_effects: dict, window_width: int):
        """
        Render active power-up indicators HORIZONTALLY below level name.
        
        Args:
            painter: QPainter object
            power_up_effects: Dict like {'speed': 8.5, 'shield': 12.3}
            window_width: Window width for centering
        """
        if not power_up_effects:
            return
            
        painter.save()
        
        # Power-up icons and colors
        powerup_info = {
            'speed': {'icon': '⚡', 'color': QColor(100, 200, 255), 'name': 'SPEED'},
            'shield': {'icon': '🛡️', 'color': QColor(200, 200, 100), 'name': 'SHIELD'},
            'triple_jump': {'icon': '↑↑↑', 'color': QColor(200, 100, 255), 'name': 'JUMP'}
        }
        
        # Box dimensions
        box_width = 120
        box_height = 50
        gap = 10
        
        # Calculate total width and starting X for centering
        total_width = len(power_up_effects) * box_width + (len(power_up_effects) - 1) * gap
        start_x = (window_width - total_width) // 2
        y = 60  # Below level name
        
        offset_x = 0
        for effect_name, time_remaining in power_up_effects.items():
            if effect_name not in powerup_info:
                continue
                
            info = powerup_info[effect_name]
            x = start_x + offset_x
            
            # Background box with gradient
            gradient = QLinearGradient(x, y, x, y + box_height)
            bg_color = QColor(info['color'])
            bg_color.setAlpha(200)
            gradient.setColorAt(0.0, bg_color)
            bg_color.setAlpha(120)
            gradient.setColorAt(1.0, bg_color)
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(255, 255, 255, 230), 2))
            painter.drawRoundedRect(x, y, box_width, box_height, 8, 8)
            
            # Icon (larger)
            painter.setFont(QFont("Segoe UI", 20))
            painter.setPen(QColor(255, 255, 255))
            icon_rect = QRect(x, y + 5, box_width, 25)
            painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, info['icon'])
            
            # Timer text
            painter.setFont(self.font_tiny)
            painter.setPen(QColor(255, 255, 255))
            timer_text = f"{int(time_remaining)}s"
            timer_rect = QRect(x, y + 30, box_width, 15)
            painter.drawText(timer_rect, Qt.AlignmentFlag.AlignCenter, timer_text)
            
            offset_x += box_width + gap
            
        painter.restore()
        
    def render_continue_prompt(self, painter: QPainter, window_size):
        """
        Render continue/restart prompt on game over screen.
        
        Args:
            painter: QPainter object
            window_size: Window QSize
        """
        painter.save()
        
        width = window_size.width()
        height = window_size.height()
        
        # Prompt box
        box_width = 450
        box_height = 140
        box_x = (width - box_width) // 2
        box_y = height // 2 + 100
        
        # Background with gradient
        gradient = QLinearGradient(box_x, box_y, box_x, box_y + box_height)
        gradient.setColorAt(0.0, QColor(40, 40, 40, 240))
        gradient.setColorAt(1.0, QColor(20, 20, 20, 240))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(255, 215, 0), 3))  # Gold border
        painter.drawRoundedRect(box_x, box_y, box_width, box_height, 12, 12)
        
        # Text
        painter.setFont(self.font_bold)
        painter.setPen(QColor(255, 255, 255))
        
        text1 = "Press SPACE to Continue"
        text2 = "Press R to Restart from Level 1"
        
        painter.drawText(
            QRect(box_x, box_y + 30, box_width, 30),
            Qt.AlignmentFlag.AlignCenter,
            text1
        )
        
        painter.setFont(self.font_small)
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(
            QRect(box_x, box_y + 75, box_width, 30),
            Qt.AlignmentFlag.AlignCenter,
            text2
        )
        
        painter.restore()
