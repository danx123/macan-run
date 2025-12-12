"""
Sound Manager - Handles all audio playback (SFX and BGM)
Manages sound effects and background music with proper error handling
"""
import os
from pathlib import Path
from PySide6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl


class SoundManager:
    """Manages all game audio - sound effects and background music."""
    
    def __init__(self, sound_path="run_sound"):
        """
        Initialize sound manager.
        
        Args:
            sound_path: Directory containing sound files
        """
        self.sound_path = Path(sound_path)
        self.enabled = True
        self.sfx_volume = 0.7
        self.bgm_volume = 0.5
        
        # Sound effects dictionary
        self.sfx = {}
        
        # Background music player
        self.bgm_player = None
        self.audio_output = None
        
        # Initialize audio system
        self._initialize_audio()
        
    def _initialize_audio(self):
        """Initialize audio system and load sound files."""
        try:
            # Setup BGM player
            self.bgm_player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.bgm_player.setAudioOutput(self.audio_output)
            self.audio_output.setVolume(self.bgm_volume)
            
            # Load sound effects
            self._load_sfx("coin", "coin.wav")
            self._load_sfx("jump", "jump.wav")
            self._load_sfx("hit", "hit.wav")
            self._load_sfx("death", "death.wav")
            
            print("✓ Sound system initialized successfully")
            
        except Exception as e:
            print(f"⚠ Sound system initialization failed: {e}")
            self.enabled = False
            
    def _load_sfx(self, name, filename):
        """
        Load a sound effect file.
        
        Args:
            name: Internal name for the sound
            filename: Name of the sound file
        """
        try:
            sound_file = self.sound_path / filename
            
            if sound_file.exists():
                effect = QSoundEffect()
                effect.setSource(QUrl.fromLocalFile(str(sound_file.absolute())))
                effect.setVolume(self.sfx_volume)
                self.sfx[name] = effect
                print(f"  Loaded: {name} ({filename})")
            else:
                print(f"  ⚠ Missing: {filename}")
                
        except Exception as e:
            print(f"  ⚠ Failed to load {filename}: {e}")
            
    def play_sfx(self, name):
        """
        Play a sound effect.
        
        Args:
            name: Name of the sound effect to play
        """
        if not self.enabled:
            return
            
        if name in self.sfx:
            try:
                self.sfx[name].play()
            except Exception as e:
                print(f"⚠ Failed to play SFX '{name}': {e}")
        else:
            print(f"⚠ Sound effect '{name}' not found")
            
    def play_bgm(self, track_name="run_bgm.mp3", loop=True):
        """
        Play background music.
        
        Args:
            track_name: Name of the music file
            loop: Whether to loop the music
        """
        if not self.enabled or not self.bgm_player:
            return
            
        try:
            music_file = self.sound_path / track_name
            
            if music_file.exists():
                self.bgm_player.setSource(QUrl.fromLocalFile(str(music_file.absolute())))
                
                if loop:
                    from PySide6.QtMultimedia import QMediaPlayer
                    self.bgm_player.setLoops(QMediaPlayer.Loops.Infinite)
                    
                self.bgm_player.play()
                print(f"♪ Playing BGM: {track_name}")
            else:
                print(f"⚠ Music file not found: {track_name}")
                
        except Exception as e:
            print(f"⚠ Failed to play BGM: {e}")
            
    def stop_bgm(self):
        """Stop background music."""
        if self.bgm_player:
            try:
                self.bgm_player.stop()
            except Exception as e:
                print(f"⚠ Failed to stop BGM: {e}")
                
    def pause_bgm(self):
        """Pause background music."""
        if self.bgm_player:
            try:
                self.bgm_player.pause()
            except Exception as e:
                print(f"⚠ Failed to pause BGM: {e}")
                
    def resume_bgm(self):
        """Resume background music."""
        if self.bgm_player:
            try:
                self.bgm_player.play()
            except Exception as e:
                print(f"⚠ Failed to resume BGM: {e}")
                
    def set_sfx_volume(self, volume):
        """
        Set sound effects volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        
        for effect in self.sfx.values():
            effect.setVolume(self.sfx_volume)
            
    def set_bgm_volume(self, volume):
        """
        Set background music volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.bgm_volume = max(0.0, min(1.0, volume))
        
        if self.audio_output:
            self.audio_output.setVolume(self.bgm_volume)
            
    def toggle_sound(self):
        """Toggle all sound on/off."""
        self.enabled = not self.enabled
        
        if not self.enabled:
            self.stop_bgm()
            
        return self.enabled
        
    def reset(self):
        """Reset sound manager - stop all audio."""
        self.stop_bgm()
        
    def cleanup(self):
        """Cleanup audio resources."""
        self.stop_bgm()
        
        # Clear sound effects
        for effect in self.sfx.values():
            try:
                effect.stop()
            except:
                pass
                
        self.sfx.clear()
        
        print("✓ Sound system cleaned up")