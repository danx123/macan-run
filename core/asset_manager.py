"""
Asset Manager - Handles loading and caching of image assets.
Prevents loading the same image from disk multiple times.
"""
from pathlib import Path
from typing import Dict, Optional
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class AssetManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AssetManager, cls).__new__(cls)
            cls._instance.assets = {}
            cls._instance.assets_path = Path("assets")
            # Buat folder assets jika belum ada
            cls._instance.assets_path.mkdir(exist_ok=True)
        return cls._instance

    def get(self, filename: str) -> Optional[QPixmap]:
        """Get a cached pixmap, or load it if not exists."""
        if filename not in self.assets:
            return self._load(filename)
        return self.assets[filename]

    def _load(self, filename: str) -> Optional[QPixmap]:
        """Load image from disk."""
        path = self.assets_path / filename
        if not path.exists():
            print(f"⚠️ Warning: Asset missing: {path}")
            # Return placeholder (magenta square for visibility)
            pixmap = QPixmap(48, 48)
            pixmap.fill(Qt.GlobalColor.magenta)
            self.assets[filename] = pixmap
            return pixmap
            
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
             print(f"❌ Error: Failed to load asset: {path}")
             pixmap = QPixmap(48, 48)
             pixmap.fill(Qt.GlobalColor.red)
        
        self.assets[filename] = pixmap
        print(f"✅ Loaded asset: {filename}")
        return pixmap

# Global accessor
assets = AssetManager()