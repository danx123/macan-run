"""
Renderer - All rendering via QPainter
OPTIMIZED: Better culling, caching, and performance
Uses view frustum culling and only renders visible objects
"""
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QBrush, QPen, QPixmap, QFont, QPolygonF, QRadialGradient
from PySide6.QtCore import QRect, QRectF, Qt, QSize, QPointF
import math
import random


class Renderer:
    """Handles all game rendering using QPainter with optimizations."""
    
    def __init__(self, size: QSize):
        self.size = size
        
        # Cached backgrounds
        self.bg_cache = None
        self.bg_size = None
        
        # Fonts (cached)
        self.title_font = QFont("Sans Serif", 48, QFont.Weight.Bold)
        self.menu_font = QFont("Sans Serif", 24)
        self.ui_font = QFont("Sans Serif", 18)
        self.small_font = QFont("Sans Serif", 16)
        
        # Tree and grass positions (procedurally generated, cached)
        self.trees = []
        self.grass_patches = []
        
        # Performance: Render hints cache
        self.render_hints_set = False
        
        self._generate_background_cache()
        
    def _generate_background_cache(self):
        """Generate cached background layers with trees and grass."""
        # Create pixmap for background
        self.bg_cache = QPixmap(self.size)
        self.bg_size = self.size
        
        painter = QPainter(self.bg_cache)
        
        # Sky gradient
        gradient = QLinearGradient(0, 0, 0, self.size.height())
        gradient.setColorAt(0.0, QColor(135, 206, 235))  # Sky blue
        gradient.setColorAt(0.7, QColor(255, 200, 150))  # Horizon orange
        gradient.setColorAt(1.0, QColor(255, 160, 100))  # Ground level
        
        painter.fillRect(0, 0, self.size.width(), self.size.height(), QBrush(gradient))
        
        # Generate tree positions (random but consistent)
        random.seed(42)  # Fixed seed for consistency
        self.trees = []
        for i in range(8):
            x = (i * 180 + random.randint(30, 100)) % self.size.width()
            y = self.size.height() - random.randint(250, 350)
            size = random.uniform(0.8, 1.2)
            self.trees.append((x, y, size))
        
        # Generate grass patches
        self.grass_patches = []
        for i in range(20):
            x = (i * 80 + random.randint(0, 40)) % self.size.width()
            y = self.size.height() - random.randint(50, 150)
            self.grass_patches.append((x, y))
        
        # Draw distant mountains (far background)
        self._draw_mountains(painter)
        
        # Draw clouds (simple circles)
        cloud_color = QColor(255, 255, 255, 180)
        painter.setBrush(QBrush(cloud_color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        for i in range(5):
            x = (i * 250 + 100) % self.size.width()
            y = 50 + (i * 30) % 100
            painter.drawEllipse(x, y, 80, 40)
            painter.drawEllipse(x + 30, y - 10, 60, 35)
            painter.drawEllipse(x + 50, y, 70, 38)
        
        # Draw trees in background
        for x, y, size in self.trees:
            self._draw_tree(painter, x, y, size)
        
        # Draw grass patches
        for x, y in self.grass_patches:
            self._draw_grass_patch(painter, x, y)
            
        painter.end()
    
    def _draw_mountains(self, painter: QPainter):
        """Draw distant mountain silhouettes."""
        painter.save()
        
        # Far mountains (lighter, more distant)
        mountain_color = QColor(100, 120, 140, 150)
        painter.setBrush(QBrush(mountain_color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Mountain 1
        mountain1 = QPolygonF([
            QPointF(0, self.size.height() * 0.6),
            QPointF(200, self.size.height() * 0.4),
            QPointF(400, self.size.height() * 0.6)
        ])
        painter.drawPolygon(mountain1)
        
        # Mountain 2
        mountain2 = QPolygonF([
            QPointF(300, self.size.height() * 0.65),
            QPointF(550, self.size.height() * 0.35),
            QPointF(800, self.size.height() * 0.65)
        ])
        painter.drawPolygon(mountain2)
        
        # Mountain 3
        mountain3 = QPolygonF([
            QPointF(700, self.size.height() * 0.62),
            QPointF(900, self.size.height() * 0.45),
            QPointF(self.size.width(), self.size.height() * 0.62)
        ])
        painter.drawPolygon(mountain3)
        
        painter.restore()
    
    def _draw_tree(self, painter: QPainter, x: float, y: float, size: float = 1.0):
        """Draw a tree with trunk and foliage."""
        painter.save()
        
        # Trunk
        trunk_width = int(15 * size)
        trunk_height = int(60 * size)
        trunk_color = QColor(101, 67, 33)
        
        painter.setBrush(QBrush(trunk_color))
        painter.setPen(QPen(QColor(70, 45, 20), 2))
        painter.drawRect(
            int(x - trunk_width/2), 
            int(y), 
            trunk_width, 
            trunk_height
        )
        
        # Tree foliage (3 circles for leafy effect)
        foliage_color = QColor(34, 139, 34)  # Forest green
        painter.setBrush(QBrush(foliage_color))
        painter.setPen(QPen(QColor(20, 100, 20), 2))
        
        # Bottom layer
        radius1 = int(40 * size)
        painter.drawEllipse(
            int(x - radius1), 
            int(y - 20 * size), 
            radius1 * 2, 
            radius1 * 2
        )
        
        # Middle layer
        radius2 = int(35 * size)
        painter.drawEllipse(
            int(x - radius2), 
            int(y - 45 * size), 
            radius2 * 2, 
            radius2 * 2
        )
        
        # Top layer
        radius3 = int(28 * size)
        painter.drawEllipse(
            int(x - radius3), 
            int(y - 65 * size), 
            radius3 * 2, 
            radius3 * 2
        )
        
        painter.restore()
    
    def _draw_grass_patch(self, painter: QPainter, x: float, y: float):
        """Draw a patch of grass blades."""
        painter.save()
        
        grass_colors = [
            QColor(50, 200, 50),
            QColor(60, 180, 60),
            QColor(40, 220, 40)
        ]
        
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Draw multiple grass blades
        for i in range(8):
            offset_x = (i - 4) * 5
            blade_height = random.randint(15, 25)
            color = random.choice(grass_colors)
            color.setAlpha(200)
            
            painter.setBrush(QBrush(color))
            
            # Grass blade (thin triangle)
            blade = QPolygonF([
                QPointF(x + offset_x, y),
                QPointF(x + offset_x - 2, y - blade_height),
                QPointF(x + offset_x + 2, y - blade_height)
            ])
            painter.drawPolygon(blade)
        
        painter.restore()
        
    def render_background(self, painter: QPainter, camera_x: float):
        """Render scrolling background with parallax."""
        if not self.bg_cache or self.bg_size != self.size:
            self._generate_background_cache()
            
        # Parallax effect - background scrolls slower
        offset = int(camera_x * 0.3) % self.size.width()
        
        # Draw background twice for seamless scrolling
        painter.drawPixmap(-offset, 0, self.bg_cache)
        painter.drawPixmap(self.size.width() - offset, 0, self.bg_cache)
        
    def render_foreground_grass(self, painter: QPainter, camera_x: float, level_width: int):
        """Render foreground grass that scrolls with the level (parallax layer)."""
        painter.save()
        
        # Generate consistent grass positions based on level
        random.seed(99)  # Different seed for foreground
        
        # Draw grass along the ground level
        ground_y = self.size.height() - 100
        
        for i in range(0, level_width // 50):
            x = i * 50 + random.randint(-10, 10)
            screen_x = x - camera_x
            
            # Only draw if on screen
            if -50 < screen_x < self.size.width() + 50:
                self._draw_grass_patch(painter, screen_x, ground_y)
        
        painter.restore()
        
    def render_menu(self, painter: QPainter, size: QSize, has_save: bool = False):
        """Render main menu screen with save/load option."""
        # Background
        gradient = QLinearGradient(0, 0, 0, size.height())
        gradient.setColorAt(0.0, QColor(40, 40, 80))
        gradient.setColorAt(1.0, QColor(20, 20, 40))
        painter.fillRect(0, 0, size.width(), size.height(), QBrush(gradient))
        
        # Title
        painter.setPen(QColor(255, 215, 0))  # Gold
        painter.setFont(self.title_font)
        title_rect = QRect(0, size.height() // 3, size.width(), 100)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "MACAN RUN")
        
        # Subtitle
        painter.setPen(QColor(200, 200, 200))
        painter.setFont(self.menu_font)
        subtitle_rect = QRect(0, size.height() // 3 + 80, size.width(), 50)
        painter.drawText(subtitle_rect, Qt.AlignmentFlag.AlignCenter, "Neo Edition")
        
        # Instructions
        painter.setFont(self.ui_font)
        instructions = [
            "Press SPACE to Start New Game",
        ]
        
        # Add Load option if save exists
        if has_save:
            instructions.append("Press L to Load Saved Game")
            instructions.append("")
        else:
            instructions.append("")
        
        instructions.extend([
            "Controls:",
            "Arrow Keys / A-D: Move",
            "Space: Jump (double jump available)",
            "P: Pause  |  Q: Quit",
            "F11: Fullscreen"
        ])
        
        y = size.height() // 2 + 30
        for i, line in enumerate(instructions):
            if i == 1 and has_save:
                # Highlight Load option in green
                painter.setPen(QColor(100, 255, 100))
            else:
                painter.setPen(QColor(200, 200, 200))
                
            text_rect = QRect(0, y, size.width(), 30)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, line)
            y += 35
            
    def render_pause(self, painter: QPainter, size: QSize):
        """Render pause overlay."""
        # Semi-transparent overlay
        painter.fillRect(0, 0, size.width(), size.height(), QColor(0, 0, 0, 150))
        
        # Pause text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(self.title_font)
        pause_rect = QRect(0, size.height() // 2 - 50, size.width(), 100)
        painter.drawText(pause_rect, Qt.AlignmentFlag.AlignCenter, "PAUSED")
        
        painter.setFont(self.ui_font)
        hint_rect = QRect(0, size.height() // 2 + 50, size.width(), 30)
        painter.drawText(hint_rect, Qt.AlignmentFlag.AlignCenter, "Press P to Resume")
        
        hint_rect2 = QRect(0, size.height() // 2 + 85, size.width(), 30)
        painter.drawText(hint_rect2, Qt.AlignmentFlag.AlignCenter, "Press ESC to Menu (Auto-Save)")
        
        hint_rect3 = QRect(0, size.height() // 2 + 120, size.width(), 30)
        painter.setPen(QColor(255, 100, 100))
        painter.drawText(hint_rect3, Qt.AlignmentFlag.AlignCenter, "Press Q to Quit")
        
    def render_game_over(self, painter: QPainter, size: QSize, score: int):
        """Render game over screen."""
        # Dark overlay
        painter.fillRect(0, 0, size.width(), size.height(), QColor(20, 20, 20))
        
        # Game Over text
        painter.setPen(QColor(255, 50, 50))
        painter.setFont(self.title_font)
        text_rect = QRect(0, size.height() // 2 - 100, size.width(), 100)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "GAME OVER")
        
        # Score
        painter.setPen(QColor(200, 200, 200))
        painter.setFont(self.menu_font)
        score_rect = QRect(0, size.height() // 2, size.width(), 50)
        painter.drawText(score_rect, Qt.AlignmentFlag.AlignCenter, f"Score: {score}")
        
    def render_level_complete(self, painter: QPainter, size: QSize, score: int, countdown: float = 0.0):
        """Render level complete screen with auto-advance countdown."""
        # Gradient background
        gradient = QLinearGradient(0, 0, 0, size.height())
        gradient.setColorAt(0.0, QColor(50, 150, 50))
        gradient.setColorAt(1.0, QColor(20, 80, 20))
        painter.fillRect(0, 0, size.width(), size.height(), QBrush(gradient))
        
        # Victory text
        painter.setPen(QColor(255, 215, 0))
        painter.setFont(self.title_font)
        text_rect = QRect(0, size.height() // 2 - 100, size.width(), 100)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "LEVEL COMPLETE!")
        
        # Score
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(self.menu_font)
        score_rect = QRect(0, size.height() // 2, size.width(), 50)
        painter.drawText(score_rect, Qt.AlignmentFlag.AlignCenter, f"Score: {score}")
        
        # Auto-advance countdown
        painter.setFont(self.ui_font)
        painter.setPen(QColor(200, 255, 200))
        countdown_text = f"Next level in {int(countdown) + 1}..."
        countdown_rect = QRect(0, size.height() // 2 + 60, size.width(), 30)
        painter.drawText(countdown_rect, Qt.AlignmentFlag.AlignCenter, countdown_text)
        
        # Continue hint (optional skip)
        painter.setFont(self.small_font)
        painter.setPen(QColor(180, 180, 180))
        hint_rect = QRect(0, size.height() // 2 + 100, size.width(), 30)
        painter.drawText(hint_rect, Qt.AlignmentFlag.AlignCenter, "Press SPACE to skip")
    
    def render_quit_confirm(self, painter: QPainter, size: QSize):
        """Render quit confirmation dialog."""
        # Dark overlay
        painter.fillRect(0, 0, size.width(), size.height(), QColor(0, 0, 0, 200))
        
        # Dialog box
        box_width = 500
        box_height = 250
        box_x = (size.width() - box_width) // 2
        box_y = (size.height() - box_height) // 2
        
        # Box background with gradient
        gradient = QLinearGradient(box_x, box_y, box_x, box_y + box_height)
        gradient.setColorAt(0.0, QColor(60, 60, 80))
        gradient.setColorAt(1.0, QColor(40, 40, 60))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(255, 100, 100), 3))
        painter.drawRoundedRect(box_x, box_y, box_width, box_height, 15, 15)
        
        # Warning icon (!)
        painter.setPen(QColor(255, 100, 100))
        painter.setFont(QFont("Sans Serif", 48, QFont.Weight.Bold))
        icon_rect = QRect(box_x, box_y + 20, box_width, 60)
        painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, "⚠")
        
        # Title
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(self.menu_font)
        title_rect = QRect(box_x, box_y + 85, box_width, 40)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "Quit Game?")
        
        # Message
        painter.setFont(self.ui_font)
        painter.setPen(QColor(200, 200, 200))
        msg_rect = QRect(box_x, box_y + 130, box_width, 30)
        painter.drawText(msg_rect, Qt.AlignmentFlag.AlignCenter, "Your progress will be saved")
        
        # Buttons
        painter.setFont(QFont("Sans Serif", 20, QFont.Weight.Bold))
        
        # Yes button (red)
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QBrush(QColor(200, 50, 50)))
        yes_btn_x = box_x + 80
        yes_btn_y = box_y + 180
        painter.drawRoundedRect(yes_btn_x, yes_btn_y, 140, 50, 8, 8)
        painter.setPen(QColor(255, 255, 255))
        yes_text_rect = QRect(yes_btn_x, yes_btn_y, 140, 50)
        painter.drawText(yes_text_rect, Qt.AlignmentFlag.AlignCenter, "YES (Y)")
        
        # No button (green)
        painter.setBrush(QBrush(QColor(50, 150, 50)))
        no_btn_x = box_x + 280
        no_btn_y = box_y + 180
        painter.drawRoundedRect(no_btn_x, no_btn_y, 140, 50, 8, 8)
        painter.setPen(QColor(255, 255, 255))
        no_text_rect = QRect(no_btn_x, no_btn_y, 140, 50)
        painter.drawText(no_text_rect, Qt.AlignmentFlag.AlignCenter, "NO (N)")
        
    def on_resize(self, size: QSize):
        """Handle renderer resize."""
        self.size = size
        self._generate_background_cache()
