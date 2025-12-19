"""
TileMap - Optimized with Chunk Caching and Image Assets.
Renders map segments into images using PNG assets.
"""
from typing import List, Dict
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt, QRect
# IMPORT ASSET MANAGER SEBAGAI 'assets'
from core.asset_manager import assets

class TileMap:
    """Tile map loaded from ASCII grid with Chunk Caching optimization."""
    
    # Base tile size from original code
    def __init__(self, tile_size: int = 48):
        self.tile_size = tile_size
        self.tiles: List[List[str]] = []
        self.width = 0
        self.height = 0
        
        # CHUNK SYSTEM OPTIMIZATION
        # Split map into segments of N columns width
        self.chunk_width_tiles = 20  # 20 tiles * 48px = 960px width per chunk
        self.chunks: Dict[int, QPixmap] = {}
        
    def load_from_string(self, map_data: str):
        """Load tilemap and pre-render chunks immediately."""
        lines = map_data.strip().split('\n')
        self.tiles = [list(line) for line in lines]
        self.height = len(self.tiles)
        self.width = max(len(row) for row in self.tiles) if self.tiles else 0
        
        # Pad rows
        for row in self.tiles:
            while len(row) < self.width:
                row.append('.')
        
        # Generate cache images immediately to prevent lag during gameplay
        self._generate_all_chunks()
        
    def _generate_all_chunks(self):
        """Pre-render the entire map into chunks using assets."""
        self.chunks.clear()
        # Pastikan aset dasar termuat
        assets.get("tile_grass.png")
        assets.get("tile_platform.png")
        assets.get("tile_wall.png")
        assets.get("trap_spike.png")
        
        total_chunks = (self.width // self.chunk_width_tiles) + 1
        print(f"🔄 Pre-rendering map into {total_chunks} chunks using assets...")
        
        for i in range(total_chunks):
            self._render_single_chunk(i)
            
    def _render_single_chunk(self, chunk_index: int):
        """Render a specific segment of the map into a QPixmap."""
        # Calculate dimensions
        chunk_pixel_width = self.chunk_width_tiles * self.tile_size
        chunk_pixel_height = self.height * self.tile_size
        
        # Create transparent pixmap
        chunk_pixmap = QPixmap(chunk_pixel_width, chunk_pixel_height)
        chunk_pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(chunk_pixmap)
        # Use high quality for the cached image, though less critical with pre-made assets
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False) 
        
        start_col = chunk_index * self.chunk_width_tiles
        end_col = min(start_col + self.chunk_width_tiles, self.width)
        
        # Draw tiles onto the pixmap relative to (0,0) of this chunk
        for row in range(self.height):
            for col in range(start_col, end_col):
                tile = self.get_tile(col, row)
                
                # Skip air and markers that are entities
                if tile == '.' or tile == ' ' or tile in ['P', 'E', 'F', 'C', 'G', 'S', 'H', 'J', 'D', 'K', 'B', 'T']:
                    continue
                
                # Calculate x position relative to the chunk
                rel_x = (col - start_col) * self.tile_size
                rel_y = row * self.tile_size
                
                self._draw_tile_asset(painter, tile, rel_x, rel_y)
                
        painter.end()
        self.chunks[chunk_index] = chunk_pixmap
        
    def _draw_tile_asset(self, painter: QPainter, tile: str, x: int, y: int):
        """Helper to draw the correct asset for a tile."""
        pixmap = None
        
        if tile == '#':
            # Untuk saat ini, kita gunakan tile_grass untuk semua tanah
            pixmap = assets.get("tile_grass.png")
            
        elif tile == '=':
            pixmap = assets.get("tile_platform.png")
            
        elif tile == '|':
            pixmap = assets.get("tile_wall.png")
            
        elif tile == '^':
             pixmap = assets.get("trap_spike.png")

        # Draw the asset if found
        if pixmap:
            # Pastikan menggambar dengan ukuran tile yang benar jika resolusi aset berbeda
            target_rect = QRect(x, y, self.tile_size, self.tile_size)
            painter.drawPixmap(target_rect, pixmap)

    def get_tile(self, col: int, row: int) -> str:
        """Get tile at grid position."""
        if 0 <= row < self.height and 0 <= col < len(self.tiles[row]):
            return self.tiles[row][col]
        return '.'
        
    def render(self, painter: QPainter, camera_x: float, camera_y: float, screen_width: int):
        """
        Render visible chunks.
        Replacing thousands of draws with 2-3 image draws.
        """
        chunk_pixel_width = self.chunk_width_tiles * self.tile_size
        
        # Calculate which chunks are visible
        start_chunk = int(camera_x // chunk_pixel_width)
        end_chunk = int((camera_x + screen_width) // chunk_pixel_width) + 1
        
        for i in range(start_chunk, end_chunk + 1):
            if i in self.chunks:
                # Calculate where to draw this chunk on screen
                # Use int() for precise pixel positioning to prevent jitter
                chunk_x = int((i * chunk_pixel_width) - camera_x)
                chunk_y = -int(camera_y)
                
                # Only draw if within reasonable bounds (optimization)
                if chunk_x + chunk_pixel_width > -50 and chunk_x < screen_width + 50:
                    painter.drawPixmap(chunk_x, chunk_y, self.chunks[i])
