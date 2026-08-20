"""
Game Engine - Main loop and game state management
FIXED: Auto-advance to next level after 2 seconds
UPDATED: Support for new enemy types with special behaviors
"""
import os
os.environ["QT_OPENGL"] = "desktop"
import time
import math
from enum import Enum
from PySide6.QtCore import QTimer, QSize
from PySide6.QtGui import QPainter, QColor

from core.renderer import Renderer
from core.physics import PhysicsEngine
from core.input_manager import InputManager
from game.level_manager import LevelManager
from ui.hud import HUD
from services.save_manager import SaveManager
from run_sfx import SoundManager
from game.particles import ParticleSystem
from game.powerup import PowerUpManager


class GameState(Enum):
    """Game state enumeration."""
    MENU = "menu"
    RUNNING = "running"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    LEVEL_COMPLETE = "level_complete"
    QUIT_CONFIRM = "quit_confirm"  # NEW: Quit confirmation


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

        # Sound Manager
        self.sound = SoundManager("run_sound")
        
        # Particle System
        self.particles = ParticleSystem()
        
        # Power-up Manager (initialized after player exists)
        self.powerup_manager = None
        
        # Game state
        self.score = 0
        self.total_coins = 0
        self.current_level = "level1"
        
        # Quit confirmation state
        self.quit_from_state = None  # Track where quit was called from
        
        # Level complete timer for auto-advance
        self.level_complete_timer = 0.0
        self.level_complete_delay = 2.0  # 2 seconds delay
        
        # Setup timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Try to load saved game
        self.has_save = self._check_save_exists()
        
    def _check_save_exists(self) -> bool:
        """Check if save file exists."""
        save_data = self.save_manager.load_game()
        return bool(save_data)
        
    def start(self):
        """Start the game engine."""
        # Load level
        self.level_manager.load_level(self.current_level)
        
        # Initialize power-up manager after player is created
        if self.level_manager.player:
            self.powerup_manager = PowerUpManager(self.level_manager.player)
            
        self.state = GameState.RUNNING
        
        # Play BGM automatically
        self._play_bgm("run_bgm.mp3")
        
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

        # Poll non-keyboard input sources (Xbox controller via XInput).
        # MUST run before _handle_input()/player update, otherwise
        # gamepad state is always one frame stale (or never read at all).
        self.input.update()

        # Handle input regardless of state
        self._handle_input()
            
        # Update based on state
        if self.state == GameState.RUNNING:
            self.update()
        elif self.state == GameState.LEVEL_COMPLETE:
            # Auto-advance timer
            self.level_complete_timer += self.delta_time
            if self.level_complete_timer >= self.level_complete_delay:
                self.next_level()
        elif self.state == GameState.QUIT_CONFIRM:
            # Pause everything during quit confirmation
            pass
        
        # Always render (including menu)
        self.widget.update()
        
    def update(self):
        """Update game logic."""
        # Update player
        if self.level_manager.player:
            self.level_manager.player.update(self.delta_time, self.input, self.sound)
            
        # Update physics
        self.physics.update(self.delta_time, self.level_manager)

        # Update power-ups (animation only)
        for powerup in self.level_manager.powerups:
            powerup.update(self.delta_time)

        # Update power-up effects on player
        if self.powerup_manager:
            self.powerup_manager.update(self.delta_time)

        # Update particle system
        self.particles.update(self.delta_time)
        
        # Update enemies (with player context for special enemies)
        self.level_manager.update_enemies(self.delta_time)
        
        # Check bomber explosions
        self._check_bomber_explosions()
            
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
            self.renderer.render_menu(painter, self.widget.size(), self.has_save)
        elif self.state in [GameState.RUNNING, GameState.PAUSED]:
            # Render game
            self.renderer.render_background(painter, self.camera_x)
            
            # Render foreground grass (parallax layer)
            if self.level_manager.tilemap:
                level_width = self.level_manager.tilemap.width * self.level_manager.tilemap.tile_size
                self.renderer.render_foreground_grass(painter, self.camera_x, level_width)
            
            # Render level with camera offset
            self.level_manager.render(painter, self.camera_x, self.camera_y)

            # Render particles (after level, before HUD)
            self.particles.render(painter, self.camera_x, self.camera_y)
            
            # Render HUD
            player = self.level_manager.player
            if player:
                self.hud.render(
                    painter,
                    score=self.score,
                    coins=self.total_coins,
                    health=player.health,
                    distance=int(player.x / 48),
                    level=self.current_level,
                    power_up_effects=player.power_up_effects if hasattr(player, 'power_up_effects') else None
                )
                
            # Render pause overlay
            if self.state == GameState.PAUSED:
                self.renderer.render_pause(painter, self.widget.size())
                
        elif self.state == GameState.GAME_OVER:
            self.renderer.render_game_over(painter, self.widget.size(), self.score)
            # Render continue prompt
            self.hud.render_continue_prompt(painter, self.widget.size())
        elif self.state == GameState.LEVEL_COMPLETE:
            # Calculate remaining time for countdown
            remaining_time = max(0, self.level_complete_delay - self.level_complete_timer)
            self.renderer.render_level_complete(
                painter, 
                self.widget.size(), 
                self.score,
                countdown=remaining_time
            )
        elif self.state == GameState.QUIT_CONFIRM:
            # Render quit confirmation dialog
            self.renderer.render_quit_confirm(painter, self.widget.size())
            
        painter.end()
        
    def _handle_input(self):
        """Process input for game control."""
        # Quit confirmation state
        if self.state == GameState.QUIT_CONFIRM:
            if self.input.is_key_pressed('Y') or self.input.is_key_pressed('Return'):
                # Yes - Quit game
                self.quit_game()
                self.input.clear_key('Y')
                self.input.clear_key('Return')
            elif self.input.is_key_pressed('N') or self.input.is_key_pressed('Escape'):
                # No - Return to previous state
                if self.quit_from_state:
                    self.state = self.quit_from_state
                    self.quit_from_state = None
                self.input.clear_key('N')
                self.input.clear_key('Escape')
            return
        
        # Global controls
        if self.input.is_key_pressed('P'):
            self.toggle_pause()
            self.input.clear_key('P')
            
        if self.input.is_key_pressed('Escape'):
            if self.state == GameState.PAUSED:
                self.state = GameState.MENU
                self.save_game()  # Auto-save on exit to menu
            else:
                self.toggle_pause()
            self.input.clear_key('Escape')
            
        # Menu state controls
        if self.state == GameState.MENU:
            if self.input.is_key_pressed('Space') or self.input.is_key_pressed('Return'):
                self.start_game()
            elif self.input.is_key_pressed('L') and self.has_save:
                self.load_game()
                self.input.clear_key('L')
            elif self.input.is_key_pressed('Q'):
                # Quit from menu
                self.show_quit_confirm()
                self.input.clear_key('Q')
        
        # Paused state controls
        elif self.state == GameState.PAUSED:
            if self.input.is_key_pressed('Q'):
                # Quit from pause
                self.show_quit_confirm()
                self.input.clear_key('Q')
        
        # Game Over controls
        elif self.state == GameState.GAME_OVER:
            # Continue from current level
            if self.input.is_key_pressed('Space') or self.input.is_key_pressed('Return'):
                self.continue_game()
                self.input.clear_key('Space')
                self.input.clear_key('Return')
            # Restart from level 1
            elif self.input.is_key_pressed('R'):
                self.start_game()
                self.input.clear_key('R')
            # Quit
            elif self.input.is_key_pressed('Q'):
                self.show_quit_confirm()
                self.input.clear_key('Q')

        # Level Complete controls (Optional manual skip)
        elif self.state == GameState.LEVEL_COMPLETE:
            if self.input.is_key_pressed('Space') or self.input.is_key_pressed('Return'):
                # Allow manual skip before timer
                self.next_level()
                self.input.clear_key('Space')
                self.input.clear_key('Return')
                
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
                
                # Particle sparkle effect
                self.particles.emit_coin_sparkle(
                    coin.x + coin.width/2,
                    coin.y + coin.height/2
                )

        # Power-up collection (IMPROVED - same as coins)
        for powerup in self.level_manager.powerups[:]:
            # Check collision with generous hitbox
            if self.physics.check_collision(player, powerup):
                # Apply effect immediately
                success = powerup.apply_to_player(player)
                
                if success:
                    # Remove from list
                    self.level_manager.powerups.remove(powerup)
                    self._play_sfx("coin")  # Satisfying collection sound
                    
                    # BIG particle burst effect for feedback
                    self.particles.emit_burst(
                        powerup.x + powerup.width/2,
                        powerup.y + powerup.height/2,
                        count=25,  # More particles
                        color=powerup.properties[powerup.type]['color']
                    )
                    
                    # Sparkle effect too
                    self.particles.emit_coin_sparkle(
                        powerup.x + powerup.width/2,
                        powerup.y + powerup.height/2
                    )
                
        # Enemy collision
        for enemy in self.level_manager.enemies[:]:
            if self.physics.check_collision(player, enemy):
                if player.vy > 0 and player.y < enemy.y:
                    # Bounce on enemy
                    if enemy.take_damage(1):
                        # Enemy died
                        self.level_manager.enemies.remove(enemy)
                        self.score += 50
                        self._play_sfx("hit")
                        
                        # Death explosion particles
                        self.particles.emit_enemy_death(
                            enemy.x + enemy.width/2,
                            enemy.y + enemy.height/2
                        )
                    else:
                        # Enemy damaged but alive
                        self.score += 25
                        self._play_sfx("hit")
                        
                    # Bounce player
                    player.vy = -300
                    
                else:
                    # Take damage
                    player.take_damage()
                    self._play_sfx("hit")
                    
                    # Damage particles
                    self.particles.emit_damage_effect(
                        player.x + player.width/2,
                        player.y + player.height/2
                    )
                    
        # Check spikes
        for spike in self.level_manager.spikes:
            if self.physics.check_collision(player, spike):
                player.take_damage()
                self._play_sfx("hit")
                
                # Damage particles
                self.particles.emit_damage_effect(
                    player.x + player.width/2,
                    player.y + player.height/2
                )
                
        # Check finish
        if self.level_manager.finish:
            if self.physics.check_collision(player, self.level_manager.finish):
                print(f"🏁 FINISH LINE REACHED! Level {self.current_level} complete!")
                self.state = GameState.LEVEL_COMPLETE
                self.level_complete_timer = 0.0  # Reset timer
                self._play_sfx("coin")  # Victory sound
                self.sound.stop_bgm()
                
                # Auto-save progress
                self.save_game()
                
                # Victory particles
                self.particles.emit_burst(
                    player.x + player.width/2,
                    player.y + player.height/2,
                    count=30,
                    color=QColor(255, 215, 0)
                )
                
    def _check_bomber_explosions(self):
        """Check and handle bomber enemy explosions."""
        from game.enemy import BomberEnemy
        
        if not self.level_manager.player:
            return
            
        player = self.level_manager.player
        
        for enemy in self.level_manager.enemies[:]:
            if isinstance(enemy, BomberEnemy) and enemy.should_explode():
                # Bomber exploded!
                explosion_x = enemy.x + enemy.width / 2
                explosion_y = enemy.y + enemy.height / 2
                
                # Big explosion particles
                self.particles.emit_burst(
                    explosion_x, explosion_y,
                    count=40,
                    color=QColor(255, 100, 0),
                    speed_range=(100, 300)
                )
                
                # Check if player is in explosion range
                distance = math.sqrt(
                    (player.x - enemy.x) ** 2 + 
                    (player.y - enemy.y) ** 2
                )
                
                if distance < enemy.get_explosion_radius():
                    # Player hit by explosion!
                    player.take_damage(2)  # Heavy damage
                    self._play_sfx("hit")
                    
                    # Damage particles
                    self.particles.emit_damage_effect(
                        player.x + player.width/2,
                        player.y + player.height/2
                    )
                
                # Remove bomber
                self.level_manager.enemies.remove(enemy)
                self._play_sfx("death")
                self.score += 75  # Bonus for triggering explosion
                
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
            self._play_sfx("death")
            self.sound.stop_bgm()
            
    def toggle_pause(self):
        """Toggle pause state."""
        if self.state == GameState.RUNNING:
            self.state = GameState.PAUSED
            self.sound.pause_bgm()
        elif self.state == GameState.PAUSED:
            self.state = GameState.RUNNING
            self.sound.resume_bgm()
            
    def start_game(self):
        """Start or restart game from Level 1."""
        self.score = 0
        self.total_coins = 0
        self.current_level = "level1"
        self.sound.reset()
        
        # Clear particles
        self.particles.clear()
        
        # Load level
        self.level_manager.load_level(self.current_level)
        
        # Initialize power-up manager
        if self.level_manager.player:
            self.powerup_manager = PowerUpManager(self.level_manager.player)
            
        self.state = GameState.RUNNING
        self._play_bgm("run_bgm.mp3")
        
    def continue_game(self):
        """Continue from current level (after game over)."""
        # Don't reset score and coins, just reload current level
        self.sound.reset()
        
        # Clear particles
        self.particles.clear()
        
        # Reload current level
        self.level_manager.load_level(self.current_level)
        
        # Initialize power-up manager
        if self.level_manager.player:
            self.powerup_manager = PowerUpManager(self.level_manager.player)
            
        self.state = GameState.RUNNING
        self._play_bgm("run_bgm.mp3")

    def next_level(self):
        """Advance to the next level."""
        try:
            # Parse current level number and increment
            current_num = int(self.current_level.replace("level", ""))
            next_num = current_num + 1
        except ValueError:
            next_num = 1
            
        self.current_level = f"level{next_num}"
        print(f"Loading {self.current_level}...")
        
        # Clear particles
        self.particles.clear()
        
        # Reset level complete timer
        self.level_complete_timer = 0.0
        
        # Load the next level
        self.level_manager.load_level(self.current_level)
        
        # Re-initialize power-up manager for new player instance
        if self.level_manager.player:
            self.powerup_manager = PowerUpManager(self.level_manager.player)
            
        self.state = GameState.RUNNING
        self._play_bgm("run_bgm.mp3")
        
        # Auto-save progress
        self.save_game()
        
    def save_game(self):
        """Save current game state."""
        if not self.level_manager.player:
            return
            
        save_data = {
            "level": self.current_level,
            "score": self.score,
            "coins": self.total_coins,
            "player": {
                "x": self.level_manager.player.x,
                "y": self.level_manager.player.y,
                "health": self.level_manager.player.health
            }
        }
        
        if self.save_manager.save_game(save_data):
            print(f"💾 Game saved: {self.current_level}, Score: {self.score}")
            self.has_save = True
        
    def load_game(self):
        """Load saved game state."""
        save_data = self.save_manager.load_game()
        
        if not save_data:
            print("⚠️ No save data found")
            self.start_game()
            return
            
        # Restore game state
        self.current_level = save_data.get("level", "level1")
        self.score = save_data.get("score", 0)
        self.total_coins = save_data.get("coins", 0)
        
        print(f"📂 Loading saved game: {self.current_level}, Score: {self.score}")
        
        # Clear particles
        self.particles.clear()
        self.sound.reset()
        
        # Load level
        self.level_manager.load_level(self.current_level)
        
        # Restore player position and health
        if self.level_manager.player and "player" in save_data:
            player_data = save_data["player"]
            self.level_manager.player.x = player_data.get("x", self.level_manager.player.x)
            self.level_manager.player.y = player_data.get("y", self.level_manager.player.y)
            self.level_manager.player.health = player_data.get("health", 3)
        
        # Initialize power-up manager
        if self.level_manager.player:
            self.powerup_manager = PowerUpManager(self.level_manager.player)
            
        self.state = GameState.RUNNING
        self._play_bgm("run_bgm.mp3")
        
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
        self.sound.cleanup()
        
        # Clear particles
        self.particles.clear()
        
        # Auto-save on exit
        if self.state == GameState.RUNNING:
            self.save_game()
    
    def show_quit_confirm(self):
        """Show quit confirmation dialog."""
        self.quit_from_state = self.state
        self.state = GameState.QUIT_CONFIRM
        print("❓ Quit confirmation shown")
    
    def quit_game(self):
        """Quit the game (close window)."""
        print("👋 Quitting game...")
        self.shutdown()
        # Close the window
        self.widget.window().close()
            
    def _play_sfx(self, name: str):
        """Play sound effect."""
        self.sound.play_sfx(name)
    
    def _play_bgm(self, track: str = "run_bgm.mp3"):
        """Play background music."""
        self.sound.play_bgm(track, loop=True)
