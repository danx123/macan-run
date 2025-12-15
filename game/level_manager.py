"""
Level Manager - Load levels, spawn entities, coordinate rendering
UPDATED: Support for new enemy types (J, C, B, T markers)
"""
from pathlib import Path
from typing import List, Optional
from PySide6.QtGui import QPainter

from game.tilemap import TileMap
from game.player import Player
from game.enemy import Enemy, FlyingEnemy, JumperEnemy, ChargerEnemy, BomberEnemy, SpinEnemy
from game.coin import Coin, Spike, Finish
from game.powerup import PowerUp, PowerUpType


class LevelManager:
    """Manages level loading and entity spawning."""
    
    def __init__(self, physics_engine):
        self.physics = physics_engine
        self.tilemap: Optional[TileMap] = None
        self.player: Optional[Player] = None
        self.enemies: List = []
        self.coins: List[Coin] = []
        self.spikes: List[Spike] = []
        self.powerups: List[PowerUp] = []
        self.finish: Optional[Finish] = None
        
    def load_level(self, level_name: str):
        """Load level from file."""
        # Clear existing entities
        self.enemies.clear()
        self.coins.clear()
        self.spikes.clear()
        self.powerups.clear()
        self.finish = None
        
        # Load level file
        level_path = Path("levels") / f"{level_name}.txt"
        
        # Fallback to default level if file not found
        if not level_path.exists():
            print(f"⚠️  Level file not found: {level_path}, using default level")
            map_data = self._get_default_level()
        else:
            with open(level_path, 'r') as f:
                map_data = f.read()
                
        # Create tilemap
        self.tilemap = TileMap(tile_size=48)
        self.tilemap.load_from_string(map_data)
        
        # Spawn entities from tilemap
        self._spawn_entities()
        
        print(f"✅ Level loaded: {level_name}")
        print(f"  - Enemies: {len(self.enemies)}")
        print(f"  - Coins: {len(self.coins)}")
        print(f"  - Power-ups: {len(self.powerups)}")
        print(f"  - Finish flag: {'YES' if self.finish else 'NO'}")
        
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
                    # Ground enemy spawn (basic red spiky)
                    self.enemies.append(Enemy(x, y))
                    
                elif tile == 'F':
                    # Flying enemy (NOT finish flag!)
                    self.enemies.append(FlyingEnemy(x, y))
                    
                elif tile == 'J':
                    # NEW: Jumper enemy (orange spring)
                    self.enemies.append(JumperEnemy(x, y))
                    
                elif tile == 'K':
                    # NEW: Charger enemy (purple bull)
                    self.enemies.append(ChargerEnemy(x, y))
                    
                elif tile == 'B':
                    # NEW: Bomber enemy (black bomb)
                    self.enemies.append(BomberEnemy(x, y))
                    
                elif tile == 'T':
                    # Spin enemy (purple spinner)
                    self.enemies.append(SpinEnemy(x, y))
                    
                elif tile == 'C':
                    # Coin spawn
                    self.coins.append(Coin(x, y))
                    
                elif tile == '^':
                    # Spike spawn
                    self.spikes.append(Spike(x, y))
                    
                elif tile == 'G':
                    # Finish flag (G = Goal)
                    self.finish = Finish(x, y)
                    print(f"  - Finish spawned at ({x}, {y})")
                    
                # Power-up spawns
                elif tile == 'S':
                    # Speed power-up
                    self.powerups.append(PowerUp(x, y, PowerUpType.SPEED))
                    
                elif tile == 'H':
                    # Health power-up
                    self.powerups.append(PowerUp(x, y, PowerUpType.HEALTH))
                    
                elif tile == 'U':
                    # Triple Jump power-up (changed from J to U to avoid conflict)
                    self.powerups.append(PowerUp(x, y, PowerUpType.TRIPLE_JUMP))
                    
                elif tile == 'D':
                    # Shield power-up
                    self.powerups.append(PowerUp(x, y, PowerUpType.SHIELD))
                    
    def update_enemies(self, delta_time: float):
        """Update all enemies with player context."""
        player_x = self.player.x if self.player else None
        player_y = self.player.y if self.player else None
        
        for enemy in self.enemies:
            # Special update for enemies that need player position
            if isinstance(enemy, ChargerEnemy):
                enemy.update(delta_time, player_x)
            elif isinstance(enemy, BomberEnemy):
                enemy.update(delta_time, player_x, player_y)
            else:
                enemy.update(delta_time)
    
    def update_coins(self, delta_time: float):
        """Update only visible coins for performance."""
        # Simple update for all coins (animation is lightweight)
        for coin in self.coins:
            coin.update(delta_time)
                    
    def render(self, painter: QPainter, camera_x: float, camera_y: float):
        """Render all level elements with optimized culling."""
        screen_width = painter.device().width()
        screen_height = painter.device().height()
        
        # Calculate visible range (with buffer for smooth entry/exit)
        visible_left = camera_x - 100
        visible_right = camera_x + screen_width + 100
        visible_top = camera_y - 100
        visible_bottom = camera_y + screen_height + 100
        
        # Render tilemap (has its own culling)
        if self.tilemap:
            self.tilemap.render(painter, camera_x, camera_y, screen_width)
        
        # Render only visible spikes
        for spike in self.spikes:
            if visible_left <= spike.x <= visible_right:
                spike.render(painter, camera_x, camera_y)
        
        # Render only visible coins
        for coin in self.coins:
            if visible_left <= coin.x <= visible_right:
                coin.render(painter, camera_x, camera_y)
        
        # Render only visible power-ups
        for powerup in self.powerups:
            if visible_left <= powerup.x <= visible_right:
                powerup.render(painter, camera_x, camera_y)
        
        # Render only visible enemies
        for enemy in self.enemies:
            if visible_left <= enemy.x <= visible_right:
                enemy.render(painter, camera_x, camera_y)
        
        # Render finish flag (always render if exists - important!)
        if self.finish:
            if visible_left <= self.finish.x <= visible_right:
                self.finish.render(painter, camera_x, camera_y)
        
        # Render player (always visible in camera)
        if self.player:
            self.player.render(painter, camera_x, camera_y)
            
    def _get_default_level(self) -> str:
        """Return default level layout if file not found."""
        return """
.........................................
.........................................
........S.......H.......U................
.......###.....###.....###...............
P.........E.............................D
########....################.........####
........C...C...C........................
....#################....................
................................^........
##############################...........
..........................C.............G
##############################.###########
"""
