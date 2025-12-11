"""
Game Engine - Main loop and game state management
Handles timing, updates, and coordinates all game systems
"""
import time
from enum import Enum
from PySide6.QtCore import QTimer, QSize
from PySide6.QtGui import QPainter

from core.renderer import Renderer
from core.physics import PhysicsEngine
from core.input_manager import InputManager
from game.level_manager import LevelManager
from ui.hud import HUD
from services.save_manager import SaveManager


class GameState(Enum):
    """Game state enumeration."""
    MENU = "menu"
    RUNNING = "running"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    LEVEL_COMPLETE = "level_complete"


class GameEngine:
    """Main game engine coordinating all systems."""
    
    def __init__(self, widget):
        self.widget = widget
        self.state = GameState.MENU
        
        # Target 60 FPS
        self.target_fps = 60
        self.frame_time = 1000 // self.target_fps  # ~16ms
        
        # Delta time tracking
        self.last_time = time.perf_counter()
        self.delta_time = 0.0
        self.accumulated_time = 0.0
        
        # Initialize systems
        self.renderer = Renderer(widget.size())
        self.physics = PhysicsEngine()
        self.input = InputManager()
        self.level_manager = LevelManager(self.physics)
        self.hud = HUD()
        self.save_manager = SaveManager()
        
        # Game state
        self.score = 0
        self.total_coins = 0
        self.current_level = "level1"
        
        # Setup timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
    def start(self):
        """Start the game engine."""
        # Load level
        self.level_manager.load_level(self.current_level)
        self.state = GameState.RUNNING
        
        # Start game loop
        self.last_time = time.perf_counter()
        self.timer.start(self.frame_time)
        
    def tick(self):
        """Main game loop tick."""
        # Calculate delta time
        current_time = time.perf_counter()
        self.delta_time = current_time - self.last_time
        self.last_time = current_time
        
        # Clamp delta time to prevent spiral of death
        if self.delta_time > 0.1:
            self.delta_time = 0.1
            
        # FIX 1: Handle input ALWAYS, regardless of state
        self._handle_input()
            
        # Update based on state
        if self.state == GameState.RUNNING:
            self.update()
        
        # Always render
        self.widget.update()
        
    def update(self):
        """Update game logic."""
        # FIX 2: Removed _handle_input() from here, moved to tick()
        
        # Update player
        if self.level_manager.player:
            self.level_manager.player.update(self.delta_time, self.input)
            
        # Update physics
        self.physics.update(self.delta_time, self.level_manager)
        
        # Update enemies
        for enemy in self.level_manager.enemies:
            enemy.update(self.delta_time)
            
        # Check collisions
        self._check_collisions()
        
        # Update camera
        self._update_camera()
        
        # Check game over conditions
        self._check_game_state()
        
    def render(self, event):
        """Render game frame."""
        painter = QPainter(self.widget)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.state == GameState.MENU:
            self.renderer.render_menu(painter, self.widget.size())
        elif self.state in [GameState.RUNNING, GameState.PAUSED]:
            # Render game
            self.renderer.render_background(painter, self.camera_x)
            
            # Render level with camera offset
            self.level_manager.render(painter, self.camera_x, self.camera_y)
            
            # Render HUD
            player = self.level_manager.player
            if player:
                self.hud.render(
                    painter,
                    score=self.score,
                    coins=self.total_coins,
                    health=player.health,
                    distance=int(player.x / 48)
                )
                
            # Render pause overlay
            if self.state == GameState.PAUSED:
                self.renderer.render_pause(painter, self.widget.size())
                
        elif self.state == GameState.GAME_OVER:
            self.renderer.render_game_over(painter, self.widget.size(), self.score)
        elif self.state == GameState.LEVEL_COMPLETE:
            self.renderer.render_level_complete(painter, self.widget.size(), self.score)
            
        painter.end()
        
    def _handle_input(self):
        """Process input for game control."""
        # Global controls
        if self.input.is_key_pressed('P'):
            self.toggle_pause()
            self.input.clear_key('P')
            
        if self.input.is_key_pressed('Escape'):
            if self.state == GameState.PAUSED:
                self.state = GameState.MENU
            else:
                self.toggle_pause()
            self.input.clear_key('Escape')
            
        # Menu state controls
        if self.state == GameState.MENU:
            if self.input.is_key_pressed('Space') or self.input.is_key_pressed('Return'):
                self.start_game()
        
        # FIX 3: Add logic for Game Over and Level Complete
        elif self.state in [GameState.GAME_OVER, GameState.LEVEL_COMPLETE]:
            if self.input.is_key_pressed('Space') or self.input.is_key_pressed('Return'):
                # Restart the game / level
                self.start_game()
                # Clear key to prevent immediate jump if restart is instant
                self.input.clear_key('Space')
                
    def _update_camera(self):
        """Update camera to follow player smoothly."""
        if not self.level_manager.player:
            return
            
        player = self.level_manager.player
        
        # Target camera position (player centered with offset)
        target_x = player.x - self.widget.width() / 3
        target_y = player.y - self.widget.height() / 2
        
        # Smooth follow (lerp)
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.08
        
        # Clamp camera to level bounds
        self.camera_x = max(0, self.camera_x)
        self.camera_y = max(0, min(self.camera_y, 100))
        
    def _check_collisions(self):
        """Check all game collisions."""
        if not self.level_manager.player:
            return
            
        player = self.level_manager.player
        
        # Coin collection
        for coin in self.level_manager.coins[:]:
            if self.physics.check_collision(player, coin):
                self.level_manager.coins.remove(coin)
                self.score += 100
                self.total_coins += 1
                self._play_sfx("coin")
                
        # Enemy collision
        for enemy in self.level_manager.enemies:
            if self.physics.check_collision(player, enemy):
                if player.vy > 0 and player.y < enemy.y:
                    # Bounce on enemy
                    enemy.health -= 1
                    player.vy = -300
                    self.score += 50
                    self._play_sfx("enemy_hit")
                    if enemy.health <= 0:
                        self.level_manager.enemies.remove(enemy)
                else:
                    # Take damage
                    player.take_damage()
                    self._play_sfx("hurt")
                    
        # Check spikes
        for spike in self.level_manager.spikes:
            if self.physics.check_collision(player, spike):
                player.take_damage()
                
        # Check finish
        if self.level_manager.finish:
            if self.physics.check_collision(player, self.level_manager.finish):
                self.state = GameState.LEVEL_COMPLETE
                self._play_sfx("win")
                
    def _check_game_state(self):
        """Check for game over conditions."""
        if not self.level_manager.player:
            return
            
        player = self.level_manager.player
        
        # Fall off world
        if player.y > 1000:
            player.health = 0
            
        # Health depleted
        if player.health <= 0:
            self.state = GameState.GAME_OVER
            self._play_sfx("game_over")
            
    def toggle_pause(self):
        """Toggle pause state."""
        if self.state == GameState.RUNNING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.RUNNING
            
    def start_game(self):
        """Start or restart game."""
        self.score = 0
        self.total_coins = 0
        self.level_manager.load_level(self.current_level)
        self.state = GameState.RUNNING
        self._play_bgm("main_theme")
        
    def on_key_press(self, event):
        """Handle key press event."""
        self.input.on_key_press(event)
        
    def on_key_release(self, event):
        """Handle key release event."""
        self.input.on_key_release(event)
        
    def on_resize(self, size: QSize):
        """Handle window resize."""
        self.renderer.on_resize(size)
        
    def shutdown(self):
        """Cleanup and save before exit."""
        self.timer.stop()
        
        # Save game state
        if self.level_manager.player:
            self.save_manager.save_game({
                "level": self.current_level,
                "player": {
                    "x": self.level_manager.player.x,
                    "y": self.level_manager.player.y,
                    "health": self.level_manager.player.health
                },
                "score": self.score,
                "coins": self.total_coins
            })
            
    def _play_sfx(self, name: str):
        """Play sound effect (stub with fallback)."""
        try:
            from PySide6.QtMultimedia import QSoundEffect
            pass
        except ImportError:
            pass
        
    def _play_bgm(self, track: str):
        """Play background music (stub with fallback)."""
        try:
            from PySide6.QtMultimedia import QMediaPlayer
            pass
        except ImportError:
            pass