"""
Test Features Script - Verify Power-Up and Save/Load functionality
Run this to test if all fixes are working correctly
"""
import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_save_manager():
    """Test save manager functionality."""
    print("\n" + "="*60)
    print("🧪 Testing Save Manager")
    print("="*60)
    
    try:
        from services.save_manager import SaveManager
        
        save_manager = SaveManager()
        
        # Test save path
        print(f"📁 Save location: {save_manager.save_path}")
        print(f"📁 Backup location: {save_manager.backup_path}")
        
        # Test save
        test_data = {
            "level": "level3",
            "score": 1500,
            "coins": 10,
            "player": {
                "x": 500.0,
                "y": 300.0,
                "health": 2
            }
        }
        
        print("\n💾 Testing save...")
        if save_manager.save_game(test_data):
            print("✅ Save test PASSED")
        else:
            print("❌ Save test FAILED")
            return False
        
        # Test load
        print("\n📂 Testing load...")
        loaded_data = save_manager.load_game()
        if loaded_data:
            print("✅ Load test PASSED")
            print(f"   Loaded level: {loaded_data.get('level')}")
            print(f"   Loaded score: {loaded_data.get('score')}")
        else:
            print("❌ Load test FAILED")
            return False
        
        # Test save info
        print("\n📊 Testing save info...")
        info = save_manager.get_save_info()
        if info.get("exists"):
            print("✅ Save info test PASSED")
            print(f"   Modified: {info.get('modified')}")
            print(f"   Size: {info.get('size')} bytes")
        else:
            print("❌ Save info test FAILED")
            return False
        
        # Test validation
        print("\n✅ Testing validation...")
        valid = save_manager._validate_save_data(test_data)
        if valid:
            print("✅ Validation test PASSED")
        else:
            print("❌ Validation test FAILED")
            return False
        
        print("\n" + "="*60)
        print("✅ ALL SAVE MANAGER TESTS PASSED!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ Save Manager Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_player_initialization():
    """Test player power-up initialization."""
    print("\n" + "="*60)
    print("🧪 Testing Player Initialization")
    print("="*60)
    
    try:
        from game.player import Player
        
        player = Player(0, 0)
        
        # Check power_up_effects
        print("\n🔍 Checking player attributes...")
        if hasattr(player, 'power_up_effects'):
            print("✅ player.power_up_effects exists")
            print(f"   Type: {type(player.power_up_effects)}")
        else:
            print("❌ player.power_up_effects MISSING!")
            return False
        
        # Check has_shield
        if hasattr(player, 'has_shield'):
            print("✅ player.has_shield exists")
            print(f"   Value: {player.has_shield}")
        else:
            print("❌ player.has_shield MISSING!")
            return False
        
        # Check base_move_speed
        if hasattr(player, 'base_move_speed'):
            print("✅ player.base_move_speed exists")
            print(f"   Value: {player.base_move_speed}")
        else:
            print("❌ player.base_move_speed MISSING!")
            return False
        
        # Check base_max_jumps
        if hasattr(player, 'base_max_jumps'):
            print("✅ player.base_max_jumps exists")
            print(f"   Value: {player.base_max_jumps}")
        else:
            print("❌ player.base_max_jumps MISSING!")
            return False
        
        print("\n" + "="*60)
        print("✅ ALL PLAYER INITIALIZATION TESTS PASSED!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ Player Initialization Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_powerup_logic():
    """Test power-up application logic."""
    print("\n" + "="*60)
    print("🧪 Testing Power-Up Logic")
    print("="*60)
    
    try:
        from game.player import Player
        from game.powerup import PowerUp, PowerUpType
        
        player = Player(0, 0)
        
        # Test Speed Power-Up
        print("\n⚡ Testing Speed Power-Up...")
        speed_powerup = PowerUp(50, 50, PowerUpType.SPEED)
        initial_speed = player.move_speed
        success = speed_powerup.apply_to_player(player)
        
        if success and player.move_speed == 400.0:
            print("✅ Speed power-up PASSED")
            print(f"   {initial_speed} → {player.move_speed}")
        else:
            print("❌ Speed power-up FAILED")
            return False
        
        # Test Health Power-Up
        print("\n❤️ Testing Health Power-Up...")
        player.health = 2  # Damage first
        health_powerup = PowerUp(100, 50, PowerUpType.HEALTH)
        success = health_powerup.apply_to_player(player)
        
        if success and player.health == 3:
            print("✅ Health power-up PASSED")
            print(f"   Health restored: {player.health}/{player.max_health}")
        else:
            print("❌ Health power-up FAILED")
            return False
        
        # Test Health when full
        print("\n❤️ Testing Health (already full)...")
        success = health_powerup.apply_to_player(player)
        if not success:
            print("✅ Health full detection PASSED")
            print("   Correctly refused collection when full")
        else:
            print("❌ Health full detection FAILED")
            return False
        
        # Test Shield Power-Up
        print("\n🛡️ Testing Shield Power-Up...")
        shield_powerup = PowerUp(150, 50, PowerUpType.SHIELD)
        success = shield_powerup.apply_to_player(player)
        
        if success and player.has_shield:
            print("✅ Shield power-up PASSED")
            print(f"   Shield active: {player.has_shield}")
        else:
            print("❌ Shield power-up FAILED")
            return False
        
        # Test Triple Jump Power-Up
        print("\n↑ Testing Triple Jump Power-Up...")
        jump_powerup = PowerUp(200, 50, PowerUpType.TRIPLE_JUMP)
        initial_jumps = player.max_jumps
        success = jump_powerup.apply_to_player(player)
        
        if success and player.max_jumps == 3:
            print("✅ Triple jump power-up PASSED")
            print(f"   {initial_jumps} → {player.max_jumps} jumps")
        else:
            print("❌ Triple jump power-up FAILED")
            return False
        
        print("\n" + "="*60)
        print("✅ ALL POWER-UP LOGIC TESTS PASSED!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ Power-Up Logic Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_powerup_manager():
    """Test PowerUpManager timer logic."""
    print("\n" + "="*60)
    print("🧪 Testing PowerUpManager")
    print("="*60)
    
    try:
        from game.player import Player
        from game.powerup import PowerUpManager, PowerUp, PowerUpType
        
        player = Player(0, 0)
        manager = PowerUpManager(player)
        
        # Apply speed boost
        print("\n⚡ Applying speed boost...")
        speed_powerup = PowerUp(50, 50, PowerUpType.SPEED)
        speed_powerup.apply_to_player(player)
        
        print(f"   Initial speed: {player.move_speed}")
        print(f"   Active effects: {player.power_up_effects}")
        
        # Simulate 5 seconds
        print("\n⏱️ Simulating 5 seconds...")
        manager.update(5.0)
        print(f"   Remaining time: {player.power_up_effects.get('speed', 0):.1f}s")
        
        if player.move_speed == 400.0:
            print("✅ Effect still active")
        else:
            print("❌ Effect expired too early")
            return False
        
        # Simulate 10 more seconds (should expire)
        print("\n⏱️ Simulating 10 more seconds...")
        manager.update(10.0)
        
        if 'speed' not in player.power_up_effects:
            print("✅ Effect expired correctly")
            print(f"   Speed restored: {player.move_speed}")
        else:
            print("❌ Effect did not expire")
            return False
        
        if player.move_speed == player.base_move_speed:
            print("✅ Speed reset to base value")
        else:
            print("❌ Speed not reset properly")
            return False
        
        print("\n" + "="*60)
        print("✅ ALL POWERUP MANAGER TESTS PASSED!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ PowerUpManager Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_input_manager():
    """Test input manager has Load key."""
    print("\n" + "="*60)
    print("🧪 Testing Input Manager")
    print("="*60)
    
    try:
        from core.input_manager import InputManager
        from PySide6.QtCore import Qt
        
        input_mgr = InputManager()
        
        # Check for L key
        print("\n🔍 Checking key mappings...")
        if Qt.Key.Key_L in input_mgr.key_map:
            print("✅ L key mapped")
            print(f"   Maps to: {input_mgr.key_map[Qt.Key.Key_L]}")
        else:
            print("❌ L key NOT mapped")
            return False
        
        print("\n" + "="*60)
        print("✅ INPUT MANAGER TEST PASSED!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ Input Manager Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🚀 MACAN RUN - FEATURE TEST SUITE")
    print("="*60)
    
    results = {
        "Save Manager": test_save_manager(),
        "Player Init": test_player_initialization(),
        "Power-Up Logic": test_powerup_logic(),
        "PowerUpManager": test_powerup_manager(),
        "Input Manager": test_input_manager()
    }
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! System is ready!")
    else:
        print("⚠️ SOME TESTS FAILED! Check output above.")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)