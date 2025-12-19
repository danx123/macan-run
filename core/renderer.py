"""
Renderer - Uses image assets for background and scenery.
OPTIMIZED: Uses integer coordinates and view frustum culling.
"""
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QBrush, QPen, QPixmap, QFont
from PySide6.QtCore import QRect, Qt, QSize
import random
# IMPORT ASSET MANAGER
from core.asset_manager import assets

class Renderer:
    """Handles all game rendering using QPainter and Image Assets."""
    
    def __init__(self, size: QSize):
        self.size = size
        
        # Cached background composite layer
        self.bg_composite_cache = None
        self.bg_size = None
        
        # Fonts (cached)
        self.title_font = QFont("Sans Serif", 48, QFont.Weight.Bold)
        self.menu_font = QFont("Sans Serif", 24)
        self.ui_font = QFont("Sans Serif", 18)
        self.small_font = QFont("Sans Serif", 16)
        
        # Pre-load essential assets
        assets.get("bg_sky.png")
        assets.get("bg_mountains.png")
        assets.get("prop_tree.png")
        assets.get("prop_cloud1.png")
        assets.get("prop_cloud2.png")
        assets.get("prop_grass_tuft.png")
        
        # Scenery positions (procedurally generated, cached)
        self.trees = []
        self.clouds = []
        self.grass_patches = []
        
        self._generate_scenery_positions()
        
    def _generate_scenery_positions(self):
        """Generate fixed positions for scenery elements."""
        random.seed(42)  # Fixed seed for consistency
        
        # Trees (Background layer)
        self.trees = []
        for i in range(8):
            x = (i * 250 + random.randint(50, 150)) % (self.size.width() * 1.5)
            # Posisi Y agak random di dekat garis cakrawala
            y = self.size.height() - random.randint(280, 350)
            scale = random.uniform(0.8, 1.2)
            self.trees.append((x, y, scale))
            
        # Clouds
        self.clouds = []
        for i in range(6):
            x = (i * 300 + random.randint(0, 100)) % (self.size.width() * 2)
            y = random.randint(50, 200)
            asset_name = random.choice(["prop_cloud1.png", "prop_cloud2.png"])
            self.clouds.append((x, y, asset_name))

        # Foreground Grass Patches positions generated in render loop based on camera
            
    def _generate_background_composite(self):
        """
        Composites sky, mountains, and distant trees into a single layer.
        This layer will scroll slowly (parallax).
        """
        # Kita buat cache background sedikit lebih lebar dari layar untuk scrolling mulus
        cache_width = int(self.size.width() * 1.5)
        self.bg_composite_cache = QPixmap(cache_width, self.size.height())
        self.bg_size = self.size
        
        painter = QPainter(self.bg_composite_cache)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        
        # 1. Draw Sky (stretched to fit)
        sky_pix = assets.get("bg_sky.png")
        painter.drawPixmap(QRect(0, 0, cache_width, self.size.height()), sky_pix)
        
        # 2. Draw Mountains (at the bottom portion, stretched horizontally)
        mount_pix = assets.get("bg_mountains.png")
        mount_h = mount_pix.height()
        # Gambar gunung di bagian bawah, sedikit overlap ke bawah layar
        painter.drawPixmap(QRect(0, self.size.height() - mount_h + 100, cache_width, mount_h), mount_pix)
        
        # 3. Draw Clouds (Fixed in background layer)
        for x, y, name in self.clouds:
            pix = assets.get(name)
            painter.drawPixmap(int(x), int(y), pix)
            
        # 4. Draw Background Trees
        tree_pix = assets.get("prop_tree.png")
        orig_w = tree_pix.width()
        orig_h = tree_pix.height()
        
        for x, y, scale in self.trees:
            w = int(orig_w * scale)
            h = int(orig_h * scale)
            # Gambar pohon dengan anchor point di bawah-tengah
            painter.drawPixmap(QRect(int(x - w/2), int(y), w, h), tree_pix)
            
        painter.end()
        
    def render_background(self, painter: QPainter, camera_x: float):
        """Render composite background with parallax scrolling."""
        if not self.bg_composite_cache or self.bg_size != self.size:
            self._generate_background_composite()
            
        cache_w = self.bg_composite_cache.width()
        
        # Parallax effect: scroll 30% speed of camera
        # Use int() for precision
        scroll_x = int(camera_x * 0.3) % cache_w
        
        # Draw twice for seamless looping
        painter.drawPixmap(-scroll_x, 0, self.bg_composite_cache)
        painter.drawPixmap(cache_w - scroll_x, 0, self.bg_composite_cache)
        
    def render_foreground_grass(self, painter: QPainter, camera_x: float, level_width: int):
        """Render foreground grass tufts using assets."""
        painter.save()
        pixmap = assets.get("prop_grass_tuft.png")
        if not pixmap:
            painter.restore()
            return

        random.seed(99) # Consistent seed
        
        ground_y = self.size.height() - 55 # Tepat di atas tile tanah
        
        # Optimization: Only loop through visible range
        start_index = int(camera_x // 60)
        end_index = int((camera_x + self.size.width()) // 60) + 2
        
        for i in range(start_index, end_index):
            # Jarak antar rumput sekitar 60px dengan variasi acak
            world_x = i * 60 + random.randint(-20, 20)
            
            # Use int() for screen coordinate
            screen_x = int(world_x - camera_x)
            
            # Gambar dengan sedikit variasi ukuran
            scale = random.uniform(0.9, 1.1)
            w = int(pixmap.width() * scale)
            h = int(pixmap.height() * scale)
            
            # Anchor point di bawah-tengah
            painter.drawPixmap(QRect(screen_x - w//2, ground_y - h + 10, w, h), pixmap)
        
        painter.restore()
        
    def render_menu(self, painter: QPainter, size: QSize, has_save: bool = False):
        """Render main menu screen."""
        # Background: Use the sky asset slightly darkened
        sky_pix = assets.get("bg_sky.png")
        painter.drawPixmap(QRect(0, 0, size.width(), size.height()), sky_pix)
        painter.fillRect(0,0, size.width(), size.height(), QColor(0,0,0,100)) # Dark overlay

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
        """Render level complete screen."""
        # Gradient background (keep gradient for victory screen as it's simple)
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
        
        # Continue hint
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
        
        # Box background
        painter.setBrush(QBrush(QColor(60, 60, 80)))
        painter.setPen(QPen(QColor(255, 100, 100), 3))
        painter.drawRoundedRect(box_x, box_y, box_width, box_height, 15, 15)
        
        # Warning icon
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
        
        # Yes button
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QBrush(QColor(200, 50, 50)))
        yes_btn_x = box_x + 80
        yes_btn_y = box_y + 180
        painter.drawRoundedRect(yes_btn_x, yes_btn_y, 140, 50, 8, 8)
        painter.setPen(QColor(255, 255, 255))
        yes_text_rect = QRect(yes_btn_x, yes_btn_y, 140, 50)
        painter.drawText(yes_text_rect, Qt.AlignmentFlag.AlignCenter, "YES (Y)")
        
        # No button
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
        # Regenerate background composite on resize
        self._generate_background_composite()
