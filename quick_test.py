"""
Quick Test - Verify fixes are working
Run this before starting the game
"""
import sys
import inspect

def test_renderer():
    """Test renderer.py has correct signature."""
    print("\n🔍 Testing renderer.py...")
    
    try:
        from core.renderer import Renderer
        from PySide6.QtCore import QSize
        
        # Check render_menu signature
        sig = inspect.signature(Renderer.render_menu)
        params = list(sig.parameters.keys())
        
        print(f"   render_menu parameters: {params}")
        
        if 'has_save' in params:
            print("   ✅ has_save parameter exists")
            return True
        else:
            print("   ❌ has_save parameter MISSING!")
            print("   Expected: ['self', 'painter', 'size', 'has_save']")
            print(f"   Got: {params}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_game_window():
    """Test game_window.py doesn't auto-start."""
    print("\n🔍 Testing game_window.py...")
    
    try:
        # Read the file
        with open('core/game_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it calls engine.start()
        if 'self.engine.start()' in content:
            # Check if it's in GameWidget.__init__
            lines = content.split('\n')
            in_init = False
            for i, line in enumerate(lines):
                if 'class GameWidget' in line:
                    in_init = True
                if in_init and 'self.engine.start()' in line:
                    print(f"   ⚠️ Found engine.start() at line {i+1}")
                    print("   This will skip menu!")
                    return False
                if in_init and 'class ' in line and 'GameWidget' not in line:
                    in_init = False
        
        print("   ✅ No auto-start found")
        
        # Check for timer.start()
        if 'self.engine.timer.start' in content:
            print("   ✅ Timer started correctly")
            return True
        else:
            print("   ⚠️ Timer not started - game might not run")
            return False
            
    except FileNotFoundError:
        print("   ❌ File not found: core/game_window.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_engine():
    """Test engine.py has save/load."""
    print("\n🔍 Testing engine.py...")
    
    try:
        from core.engine import GameEngine
        
        # Check methods exist
        methods = ['save_game', 'load_game', '_check_save_exists']
        
        for method in methods:
            if hasattr(GameEngine, method):
                print(f"   ✅ {method} exists")
            else:
                print(f"   ❌ {method} MISSING!")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_input_manager():
    """Test input manager has L key."""
    print("\n🔍 Testing input_manager.py...")
    
    try:
        from core.input_manager import InputManager
        from PySide6.QtCore import Qt
        
        input_mgr = InputManager()
        
        if Qt.Key.Key_L in input_mgr.key_map:
            print(f"   ✅ L key mapped to: {input_mgr.key_map[Qt.Key.Key_L]}")
            return True
        else:
            print("   ❌ L key NOT mapped")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_save_manager():
    """Test save manager exists."""
    print("\n🔍 Testing save_manager.py...")
    
    try:
        from services.save_manager import SaveManager
        
        save_mgr = SaveManager()
        
        # Check methods
        methods = ['save_game', 'load_game', 'get_save_info', '_validate_save_data']
        
        for method in methods:
            if hasattr(save_mgr, method):
                print(f"   ✅ {method} exists")
            else:
                print(f"   ❌ {method} MISSING!")
                return False
        
        print(f"   📁 Save location: {save_mgr.save_path}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all quick tests."""
    print("="*60)
    print("🚀 QUICK TEST - Verify All Fixes")
    print("="*60)
    
    tests = {
        "renderer.py": test_renderer(),
        "game_window.py": test_game_window(),
        "engine.py": test_engine(),
        "input_manager.py": test_input_manager(),
        "save_manager.py": test_save_manager()
    }
    
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    
    for name, result in tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:25} {status}")
    
    all_passed = all(tests.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("You can now run: python main.py")
    else:
        print("⚠️ SOME TESTS FAILED!")
        print("Please check the error messages above.")
        print("\nFiles to update:")
        for name, result in tests.items():
            if not result:
                print(f"  ❌ {name}")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)