"""
Input Manager - Keyboard input handling
Tracks key states for smooth input processing
"""
from PySide6.QtCore import Qt
from typing import Dict, Set


class InputManager:
    """Manages keyboard input state."""
    
    def __init__(self):
        self.keys_pressed: Set[str] = set()
        self.keys_just_pressed: Set[str] = set()
        
        # Key mapping
        self.key_map = {
            Qt.Key.Key_Left: 'Left',
            Qt.Key.Key_Right: 'Right',
            Qt.Key.Key_Up: 'Up',
            Qt.Key.Key_Down: 'Down',
            Qt.Key.Key_Space: 'Space',
            Qt.Key.Key_A: 'A',
            Qt.Key.Key_D: 'D',
            Qt.Key.Key_W: 'W',
            Qt.Key.Key_S: 'S',
            Qt.Key.Key_P: 'P',
            Qt.Key.Key_R: 'R',  # Restart
            Qt.Key.Key_L: 'L',  # Load
            Qt.Key.Key_Escape: 'Escape',
            Qt.Key.Key_Return: 'Return',
            Qt.Key.Key_Enter: 'Return',
        }
        
    def on_key_press(self, event):
        """Handle key press event."""
        key = event.key()
        if key in self.key_map:
            key_name = self.key_map[key]
            if key_name not in self.keys_pressed:
                self.keys_just_pressed.add(key_name)
            self.keys_pressed.add(key_name)
            
    def on_key_release(self, event):
        """Handle key release event."""
        key = event.key()
        if key in self.key_map:
            key_name = self.key_map[key]
            self.keys_pressed.discard(key_name)
            self.keys_just_pressed.discard(key_name)
            
    def is_key_pressed(self, key_name: str) -> bool:
        """Check if a key is currently pressed."""
        return key_name in self.keys_pressed
        
    def is_key_just_pressed(self, key_name: str) -> bool:
        """Check if a key was just pressed this frame."""
        return key_name in self.keys_just_pressed
        
    def clear_key(self, key_name: str):
        """Clear a key from just pressed state."""
        self.keys_just_pressed.discard(key_name)
        
    def clear_all_just_pressed(self):
        """Clear all just pressed keys (call at end of frame)."""
        self.keys_just_pressed.clear()
        
    def is_move_left(self) -> bool:
        """Check if moving left."""
        return self.is_key_pressed('Left') or self.is_key_pressed('A')
        
    def is_move_right(self) -> bool:
        """Check if moving right."""
        return self.is_key_pressed('Right') or self.is_key_pressed('D')
        
    def is_jump(self) -> bool:
        """Check if jump button is pressed."""
        return self.is_key_just_pressed('Space') or self.is_key_just_pressed('W')
