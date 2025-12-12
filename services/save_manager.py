"""
Save Manager - Save and load game state to JSON
Enhanced with backup and validation
OS-appropriate save locations
"""
import json
from pathlib import Path
from datetime import datetime
import sys
import shutil


class SaveManager:
    """Manages game save/load operations with backup."""
    
    def __init__(self):
        self.save_path = self._get_save_path()
        self.backup_path = self.save_path.parent / "save_backup.json"
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
        
    def save_game(self, game_state: dict) -> bool:
        """
        Save game state to JSON file with backup.
        
        Args:
            game_state: Dictionary containing game state
            
        Returns:
            bool: True if save successful
        """
        try:
            # Add metadata
            game_state["timestamp"] = datetime.now().isoformat()
            game_state["version"] = "1.0"
            
            # Create backup of existing save
            if self.save_path.exists():
                try:
                    shutil.copy2(self.save_path, self.backup_path)
                    print(f"💾 Backup created: {self.backup_path}")
                except Exception as e:
                    print(f"⚠️ Backup failed: {e}")
            
            # Write to file
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Game saved successfully to: {self.save_path}")
            print(f"   Level: {game_state.get('level', 'unknown')}")
            print(f"   Score: {game_state.get('score', 0)}")
            print(f"   Coins: {game_state.get('coins', 0)}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving game: {e}")
            return False
            
    def load_game(self) -> dict:
        """
        Load game state from JSON file.
        
        Returns:
            dict: Game state dictionary, empty if load fails
        """
        try:
            if not self.save_path.exists():
                print("ℹ️ No save file found")
                return {}
            
            with open(self.save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate save data
            if not self._validate_save_data(data):
                print("⚠️ Save data validation failed, attempting backup...")
                return self._load_backup()
            
            print(f"✅ Game loaded successfully from: {self.save_path}")
            print(f"   Level: {data.get('level', 'unknown')}")
            print(f"   Score: {data.get('score', 0)}")
            print(f"   Coins: {data.get('coins', 0)}")
            return data
            
        except json.JSONDecodeError as e:
            print(f"❌ Corrupted save file: {e}")
            print("   Attempting to load backup...")
            return self._load_backup()
            
        except Exception as e:
            print(f"❌ Error loading game: {e}")
            return {}
    
    def _load_backup(self) -> dict:
        """Load from backup file."""
        try:
            if not self.backup_path.exists():
                print("⚠️ No backup file found")
                return {}
            
            with open(self.backup_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if self._validate_save_data(data):
                print("✅ Backup loaded successfully")
                return data
            else:
                print("❌ Backup data invalid")
                return {}
                
        except Exception as e:
            print(f"❌ Error loading backup: {e}")
            return {}
    
    def _validate_save_data(self, data: dict) -> bool:
        """
        Validate save data structure.
        
        Args:
            data: Save data dictionary
            
        Returns:
            bool: True if valid
        """
        required_keys = ["level", "score", "coins", "player"]
        
        # Check required keys
        for key in required_keys:
            if key not in data:
                print(f"⚠️ Missing required key: {key}")
                return False
        
        # Validate player data
        if not isinstance(data["player"], dict):
            print("⚠️ Invalid player data format")
            return False
        
        player_keys = ["x", "y", "health"]
        for key in player_keys:
            if key not in data["player"]:
                print(f"⚠️ Missing player key: {key}")
                return False
        
        # Validate level format
        level = data["level"]
        if not isinstance(level, str) or not level.startswith("level"):
            print(f"⚠️ Invalid level format: {level}")
            return False
        
        return True
            
    def delete_save(self) -> bool:
        """
        Delete save file and backup.
        
        Returns:
            bool: True if successful
        """
        try:
            deleted = False
            
            if self.save_path.exists():
                self.save_path.unlink()
                print(f"🗑️ Deleted save file: {self.save_path}")
                deleted = True
            
            if self.backup_path.exists():
                self.backup_path.unlink()
                print(f"🗑️ Deleted backup file: {self.backup_path}")
                deleted = True
            
            if not deleted:
                print("ℹ️ No save files to delete")
            
            return True
            
        except Exception as e:
            print(f"❌ Error deleting save: {e}")
            return False
            
    def get_save_info(self) -> dict:
        """
        Get information about save file.
        
        Returns:
            dict: Save file information
        """
        if not self.save_path.exists():
            return {
                "exists": False,
                "message": "No save file found"
            }
        
        try:
            stat = self.save_path.stat()
            
            # Try to read save data
            with open(self.save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                "exists": True,
                "path": str(self.save_path),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "level": data.get("level", "unknown"),
                "score": data.get("score", 0),
                "coins": data.get("coins", 0),
                "timestamp": data.get("timestamp", "unknown")
            }
            
        except Exception as e:
            return {
                "exists": True,
                "path": str(self.save_path),
                "error": str(e),
                "message": "Save file exists but cannot be read"
            }
    
    def export_save(self, export_path: str) -> bool:
        """
        Export save to custom location.
        
        Args:
            export_path: Destination path
            
        Returns:
            bool: True if successful
        """
        try:
            if not self.save_path.exists():
                print("⚠️ No save file to export")
                return False
            
            shutil.copy2(self.save_path, export_path)
            print(f"📤 Save exported to: {export_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting save: {e}")
            return False
    
    def import_save(self, import_path: str) -> bool:
        """
        Import save from custom location.
        
        Args:
            import_path: Source path
            
        Returns:
            bool: True if successful
        """
        try:
            import_file = Path(import_path)
            
            if not import_file.exists():
                print(f"⚠️ Import file not found: {import_path}")
                return False
            
            # Validate imported data
            with open(import_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not self._validate_save_data(data):
                print("❌ Invalid save file format")
                return False
            
            # Create backup of current save
            if self.save_path.exists():
                shutil.copy2(self.save_path, self.backup_path)
            
            # Import new save
            shutil.copy2(import_file, self.save_path)
            print(f"📥 Save imported from: {import_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error importing save: {e}")
            return False
