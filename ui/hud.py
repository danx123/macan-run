"""
HUD - Heads Up Display
Displays score, health, coins, and current level
"""
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PySide6.QtCore import QRect, Qt

class HUD:
    """Manages the Heads-Up Display rendering."""
    
    def __init__(self):
        # Fonts
        self.font_large = QFont("Segoe UI", 24, QFont.Weight.Bold)
        self.font_small = QFont("Segoe UI", 16)
        self.font_bold = QFont("Segoe UI", 18, QFont.Weight.Bold)
        
    def render(self, painter: QPainter, score: int, coins: int, health: int, distance: int, level: str = "level1"):
        """Render HUD elements."""
        window_width = painter.device().width()
        
        painter.save()
        
        # --- 1. TAMPILKAN LEVEL (Tengah Atas) ---
        # Format teks: "level1" -> "LEVEL 1"
        level_text = level.replace("level", "LEVEL ").upper()
        
        painter.setFont(self.font_large)
        # Efek Shadow untuk teks Level
        painter.setPen(QColor(0, 0, 0, 150))
        painter.drawText(QRect(2, 12, window_width, 50), Qt.AlignmentFlag.AlignCenter, level_text)
        # Teks Utama Level
        painter.setPen(QColor(255, 215, 0))  # Warna Emas
        painter.drawText(QRect(0, 10, window_width, 50), Qt.AlignmentFlag.AlignCenter, level_text)
        
        # --- 2. Score & Coins (Kiri Atas) ---
        painter.setFont(self.font_bold)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(20, 40, f"SCORE: {score:05d}")
        
        painter.setPen(QColor(255, 223, 0))  # Kuning Koin
        painter.drawText(20, 70, f"COINS: {coins}")
        
        # --- 3. Distance (Kanan Bawah - Opsional) ---
        painter.setFont(self.font_small)
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(window_width - 150, 40, f"DIST: {distance}m")
        
        # --- 4. Health Bar (Kanan Atas) ---
        self._render_health(painter, health, window_width)
        
        painter.restore()
        
    def _render_health(self, painter: QPainter, health: int, width: int):
        """Draw heart icons or health bar."""
        # Gambar 3 kotak/hati melambangkan nyawa
        start_x = width - 140
        y = 60
        box_size = 30
        gap = 10
        
        for i in range(3):
            x = start_x + i * (box_size + gap)
            
            # Border
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            
            if i < health:
                # Nyawa penuh (Merah)
                painter.setBrush(QBrush(QColor(255, 50, 50)))
            else:
                # Nyawa kosong (Transparan/Gelap)
                painter.setBrush(QBrush(QColor(50, 0, 0, 100)))
                
            painter.drawRect(x, y, box_size, box_size)
