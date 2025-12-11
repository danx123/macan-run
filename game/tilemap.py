"""
TileMap - ASCII map rendering and tile management
Tiles drawn via QPainter with no image files
"""
from typing import List
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient
from PySide6.QtCore import QRectF, Qt


class TileMap:
    """Tile map loaded from ASCII grid."""
    
    def __init__(self, tile_size: int = 48):
        self.tile_size = tile_size
        self.tiles: List[List[str]] = []
        self.width = 0
        self.height = 0
        
        # Tile colors
        self.tile_colors = {
            '#': QColor(101, 67, 33),   # Ground - brown
            '=': QColor(80, 80, 80),     # Platform - gray
            '|': QColor(100, 50, 0),     # Wall - dark brown
        }
        
    def load_from_string(self, map_data: str):
        """Load tilemap from ASCII string."""
        lines = map_data.strip().split('\n')
        self.tiles = [list(line) for line in lines]
        self.height = len(self.tiles)
        self.width = max(len(row) for row in self.tiles) if self.tiles else 0
        
        # Pad rows to same width
        for row in self.tiles:
            while len(row) < self.width:
                row.append('.')
                
    def get_tile(self, col: int, row: int) -> str:
        """Get tile at grid position."""
        if 0 <= row < self.height and 0 <= col < len(self.tiles[row]):
            return self.tiles[row][col]
        return '.'
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float, screen_width: int):
        """Render visible tiles."""
        # Calculate visible tile range
        start_col = max(0, int(camera_x / self.tile_size) - 1)
        end_col = min(self.width, int((camera_x + screen_width) / self.tile_size) + 2)
        
        # Render tiles row by row for better batching
        for row in range(self.height):
            for col in range(start_col, end_col):
                tile = self.get_tile(col, row)
                
                if tile == '.' or tile == ' ':
                    continue
                    
                # Skip entity markers (rendered separately)
                if tile in ['P', 'E', 'C', '^', 'F']:
                    continue
                    
                screen_x = col * self.tile_size - camera_x
                screen_y = row * self.tile_size - camera_y
                
                self._render_tile(painter, tile, screen_x, screen_y)
                
    def _render_tile(self, painter: QPainter, tile: str, x: float, y: float):
        """Render a single tile."""
        ts = self.tile_size
        
        if tile == '#':
            # Ground block with gradient
            gradient = QLinearGradient(x, y, x, y + ts)
            gradient.setColorAt(0.0, QColor(120, 80, 40))
            gradient.setColorAt(1.0, QColor(80, 50, 20))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(60, 40, 20), 2))
            painter.drawRect(x, y, ts, ts)
            
            # Grass on top
            grass_color = QColor(50, 150, 50)
            painter.setBrush(QBrush(grass_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(x, y, ts, 6)
            
            # Texture details
            painter.setPen(QPen(QColor(60, 40, 20), 1))
            for i in range(3):
                offset = i * 16
                painter.drawLine(x + offset, y + 10, x + offset + 8, y + ts)
                
        elif tile == '=':
            # Platform (semi-transparent)
            platform_color = QColor(100, 100, 100, 200)
            painter.setBrush(QBrush(platform_color))
            painter.setPen(QPen(QColor(70, 70, 70), 2))
            painter.drawRect(x, y, ts, 12)
            
            # Support beams
            painter.drawRect(x + 4, y + 12, 4, ts - 12)
            painter.drawRect(x + ts - 8, y + 12, 4, ts - 12)
            
        elif tile == '|':
            # Wall
            gradient = QLinearGradient(x, y, x + ts, y)
            gradient.setColorAt(0.0, QColor(130, 70, 30))
            gradient.setColorAt(0.5, QColor(110, 60, 25))
            gradient.setColorAt(1.0, QColor(90, 50, 20))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(70, 40, 15), 2))
            painter.drawRect(x, y, ts, ts)
            
            # Brick pattern
            painter.setPen(QPen(QColor(50, 30, 10), 1))
            painter.drawLine(x, y + ts/2, x + ts, y + ts/2)
            painter.drawLine(x + ts/2, y, x + ts/2, y + ts/2)
            painter.drawLine(x + ts/4, y + ts/2, x + ts/4, y + ts)
            painter.drawLine(x + ts*3/4, y + ts/2, x + ts*3/4, y + ts)