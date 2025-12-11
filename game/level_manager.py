"""
Level Manager - Load levels, spawn entities, coordinate rendering
"""
from pathlib import Path
from typing import List, Optional
from PySide6.QtGui import QPainter

from game.tilemap import TileMap
from game.player import Player
from game.enemy import Enemy
from game.coin import Coin, Spike, Finish


class LevelManager:
    """Manages level loading and entity spawning."""
    
    def __init__(self, physics_engine):
        self.physics = physics_engine
        self.tilemap: Optional[TileMap] = None
        self.player: Optional[Player] = None
        self.enemies: List[Enemy] = []
        self.coins: List[Coin] = []
        self.spikes: List[Spike] = []
        self.finish: Optional[Finish] = None
        
    def load_level(self, level_name: str):
        """Load level from file."""
        # Clear existing entities
        self.enemies.clear()
        self.coins.clear()
        self.spikes.clear()
        self.finish = None
        
        # Load level file
        level_path = Path("levels") / f"{level_name}.txt"
        
        # Fallback to default level if file not found
        if not level_path.exists():
            map_data = self._get_default_level()
        else:
            with open(level_path, 'r') as f:
                map_data = f.read()
                
        # Create tilemap
        self.tilemap = TileMap(tile_size=48)
        self.tilemap.load_from_string(map_data)
        
        # Spawn entities from tilemap
        self._spawn_entities()
        
    def _spawn_entities(self):
        """Spawn entities based on tilemap markers."""
        if not self.tilemap:
            return
            
        tile_size = self.tilemap.tile_size
        
        for row in range(self.tilemap.height):
            for col in range(self.tilemap.width):
                tile = self.tilemap.get_tile(col, row)
                x = col * tile_size
                y = row * tile_size
                
                if tile == 'P':
                    # Player spawn
                    self.player = Player(x, y)
                elif tile == 'E':
                    # Enemy spawn
                    self.enemies.append(Enemy(x, y))
                elif tile == 'C':
                    # Coin spawn
                    self.coins.append(Coin(x, y))
                elif tile == '^':
                    # Spike spawn
                    self.spikes.append(Spike(x, y))
                elif tile == 'F':
                    # Finish flag
                    self.finish = Finish(x, y)
                    
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render all level elements."""
        screen_width = 1024  # Default, should be passed from engine
        
        # Render tilemap
        if self.tilemap:
            self.tilemap.render(painter, camera_x, camera_y, screen_width)
            
        # Render spikes
        for spike in self.spikes:
            spike.render(painter, camera_x, camera_y)
            
        # Render coins
        for coin in self.coins:
            coin.render(painter, camera_x, camera_y)
            
        # Render enemies
        for enemy in self.enemies:
            enemy.render(painter, camera_x, camera_y)
            
        # Render finish flag
        if self.finish:
            self.finish.render(painter, camera_x, camera_y)
            
        # Render player
        if self.player:
            self.player.render(painter, camera_x, camera_y)
            
    def _get_default_level(self) -> str:
        """Return default level layout if file not found."""
        return """
.........................................
.........................................
.........................................
.........................................
......C.....C.....C......................
.....###...###...###.....................
P...............................E........
########............#####################
........C...C...C........................
....#################..........^.........
................................##########
..........................C.............F
##############################.###########
"""