"""
Physics Engine - Gravity, velocity integration, AABB collision
All physics calculations using basic math (no external physics library)
"""
import math
from typing import List, Tuple, Optional


class PhysicsEngine:
    """Handles physics simulation and collision detection."""
    
    def __init__(self):
        # Physics constants
        self.gravity = 980.0  # pixels/s^2 (realistic gravity)
        self.max_fall_speed = 600.0  # Terminal velocity
        self.ground_friction = 0.85  # Ground friction coefficient
        self.air_resistance = 0.98  # Air resistance
        
    def update(self, delta_time: float, level_manager):
        """Update physics for all entities."""
        if not level_manager.player:
            return
            
        player = level_manager.player
        
        # Apply gravity
        if not player.on_ground:
            player.vy += self.gravity * delta_time
            # Clamp to terminal velocity
            player.vy = min(player.vy, self.max_fall_speed)
        
        # Apply air resistance to horizontal movement
        if not player.on_ground:
            player.vx *= self.air_resistance
        else:
            player.vx *= self.ground_friction
            
        # Integrate velocity (Euler integration)
        player.x += player.vx * delta_time
        player.y += player.vy * delta_time
        
        # Reset ground state
        player.on_ground = False
        
        # Tile collision
        self._resolve_tile_collisions(player, level_manager.tilemap)
        
    def _resolve_tile_collisions(self, player, tilemap):
        """Resolve collisions between player and tilemap using AABB."""
        if not tilemap:
            return
            
        tile_size = tilemap.tile_size
        
        # Get player bounding box
        px1 = player.x
        py1 = player.y
        px2 = player.x + player.width
        py2 = player.y + player.height
        
        # Check tiles around player
        start_col = max(0, int(px1 // tile_size) - 1)
        end_col = min(tilemap.width, int(px2 // tile_size) + 2)
        start_row = max(0, int(py1 // tile_size) - 1)
        end_row = min(tilemap.height, int(py2 // tile_size) + 2)
        
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile = tilemap.get_tile(col, row)
                
                # Skip empty tiles
                if tile == '.' or tile == ' ':
                    continue
                    
                # Skip non-solid tiles
                if tile in ['C', 'P', 'E', 'F']:
                    continue
                    
                # Tile bounding box
                tx1 = col * tile_size
                ty1 = row * tile_size
                tx2 = tx1 + tile_size
                ty2 = ty1 + tile_size
                
                # AABB collision check
                if self._aabb_intersect(px1, py1, px2, py2, tx1, ty1, tx2, ty2):
                    # Resolve collision
                    self._resolve_aabb_collision(player, tx1, ty1, tx2, ty2)
                    
    def _aabb_intersect(self, x1: float, y1: float, x2: float, y2: float,
                        bx1: float, by1: float, bx2: float, by2: float) -> bool:
        """Check if two axis-aligned bounding boxes intersect."""
        return (x1 < bx2 and x2 > bx1 and y1 < by2 and y2 > by1)
        
    def _resolve_aabb_collision(self, player, tx1: float, ty1: float, tx2: float, ty2: float):
        """Resolve AABB collision by pushing player out of tile."""
        # Calculate overlap on each axis
        px1 = player.x
        py1 = player.y
        px2 = player.x + player.width
        py2 = player.y + player.height
        
        overlap_left = px2 - tx1
        overlap_right = tx2 - px1
        overlap_top = py2 - ty1
        overlap_bottom = ty2 - py1
        
        # Find minimum overlap
        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
        
        # Resolve based on minimum overlap direction
        if min_overlap == overlap_top and player.vy > 0:
            # Collision from top (player falling onto tile)
            player.y = ty1 - player.height
            player.vy = 0
            player.on_ground = True
            player.jumps_remaining = player.max_jumps
        elif min_overlap == overlap_bottom and player.vy < 0:
            # Collision from bottom (player hitting ceiling)
            player.y = ty2
            player.vy = 0
        elif min_overlap == overlap_left and player.vx > 0:
            # Collision from left
            player.x = tx1 - player.width
            player.vx = 0
        elif min_overlap == overlap_right and player.vx < 0:
            # Collision from right
            player.x = tx2
            player.vx = 0
            
    def check_collision(self, entity1, entity2) -> bool:
        """Check collision between two entities using AABB."""
        return self._aabb_intersect(
            entity1.x, entity1.y, entity1.x + entity1.width, entity1.y + entity1.height,
            entity2.x, entity2.y, entity2.x + entity2.width, entity2.y + entity2.height
        )
        
    def apply_jump_force(self, player, force: float):
        """Apply jump force to player."""
        if player.jumps_remaining > 0:
            player.vy = -force
            player.jumps_remaining -= 1
            player.on_ground = False
            
    def calculate_distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate Euclidean distance between two points."""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
    def normalize_vector(self, x: float, y: float) -> Tuple[float, float]:
        """Normalize a 2D vector."""
        length = math.sqrt(x * x + y * y)
        if length == 0:
            return 0.0, 0.0
        return x / length, y / length