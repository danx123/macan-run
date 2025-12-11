"""
Save Manager - Save and load game state to JSON
OS-appropriate save locations
"""
import json
from pathlib import Path
from datetime import datetime
import sys


class SaveManager:
    """Manages game save/load operations."""
    
    def __init__(self):
        self.save_path = self._get_save_path()
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        
    def _get_save_path(self) -> Path:
        """Get OS-appropriate save file path."""
        app_name = "MacanRun"
        
        if sys.platform == "win32":
            # Windows: %LOCALAPPDATA%/MacanRun/save.json
            base = Path.home() / "AppData" / "Local"
        elif sys.platform == "darwin":
            # macOS: ~/Library/Application Support/MacanRun/save.json
            base = Path.home() / "Library" / "Application Support"
        else:
            # Linux: ~/.local/share/MacanRun/save.json
            base = Path.home() / ".local" / "share"
            
        return base / app_name / "save.json"
        
    def save_game(self, game_state: dict):
        """Save game state to JSON file."""
        try:
            # Add timestamp
            game_state["timestamp"] = datetime.now().isoformat()
            
            # Write to file
            with open(self.save_path, 'w') as f:
                json.dump(game_state, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
            
    def load_game(self) -> dict:
        """Load game state from JSON file."""
        try:
            if not self.save_path.exists():
                return {}
                
            with open(self.save_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading game: {e}")
            return {}
            
    def delete_save(self):
        """Delete save file."""
        try:
            if self.save_path.exists():
                self.save_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False
            
    def get_save_info(self) -> dict:
        """Get information about save file."""
        if not self.save_path.exists():
            return {"exists": False}
            
        stat = self.save_path.stat()
        return {
            "exists": True,
            "path": str(self.save_path),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }