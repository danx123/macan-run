"""
Input Manager - Keyboard + Xbox controller input handling
Tracks key states for smooth input processing

ADDED: Xbox controller support via XInput (ctypes, no external deps).
Runs alongside keyboard input - gamepad and keyboard both feed the same
logical key names ('Left', 'Space', 'P', etc.), so is_move_left(),
is_jump(), and all existing state-handling code in engine.py work
unchanged regardless of input source.

Degrades gracefully: if no controller is connected, or the game isn't
running on Windows, gamepad polling silently no-ops and keyboard input
is unaffected.
"""
import sys
import math
from PySide6.QtCore import Qt
from typing import Dict, Set

# ---------------------------------------------------------------------------
# XInput bindings (Windows only). Wrapped in try/except so the whole module
# still imports cleanly on non-Windows platforms or if XInput is missing.
# ---------------------------------------------------------------------------
try:
    import ctypes
    from ctypes import wintypes

    class _XInputGamepad(ctypes.Structure):
        _fields_ = [
            ("wButtons", wintypes.WORD),
            ("bLeftTrigger", ctypes.c_ubyte),
            ("bRightTrigger", ctypes.c_ubyte),
            ("sThumbLX", ctypes.c_short),
            ("sThumbLY", ctypes.c_short),
            ("sThumbRX", ctypes.c_short),
            ("sThumbRY", ctypes.c_short),
        ]

    class _XInputState(ctypes.Structure):
        _fields_ = [
            ("dwPacketNumber", wintypes.DWORD),
            ("Gamepad", _XInputGamepad),
        ]

    _xinput_dll = None
    if sys.platform == "win32":
        # Try newest to oldest - xinput1_4 ships with Windows 8+,
        # xinput9_1_0 is the widest-compatibility fallback (Vista+).
        for _dll_name in ("xinput1_4.dll", "xinput1_3.dll", "xinput9_1_0.dll"):
            try:
                _xinput_dll = ctypes.windll.LoadLibrary(_dll_name)
                break
            except OSError:
                continue

    if _xinput_dll is not None:
        _xinput_dll.XInputGetState.argtypes = [wintypes.DWORD, ctypes.POINTER(_XInputState)]
        _xinput_dll.XInputGetState.restype = wintypes.DWORD

    _XINPUT_AVAILABLE = _xinput_dll is not None
except (ImportError, AttributeError, OSError):
    _xinput_dll = None
    _XINPUT_AVAILABLE = False


# XInput button bitmask constants (only the ones we map)
_XINPUT_GAMEPAD_DPAD_UP = 0x0001
_XINPUT_GAMEPAD_DPAD_DOWN = 0x0002
_XINPUT_GAMEPAD_DPAD_LEFT = 0x0004
_XINPUT_GAMEPAD_DPAD_RIGHT = 0x0008
_XINPUT_GAMEPAD_START = 0x0010
_XINPUT_GAMEPAD_BACK = 0x0020
_XINPUT_GAMEPAD_A = 0x1000
_XINPUT_GAMEPAD_B = 0x2000
_XINPUT_GAMEPAD_X = 0x4000
_XINPUT_GAMEPAD_Y = 0x8000

_STICK_DEADZONE = 0.28  # fraction of full stick travel (0..1)
_MAX_CONTROLLERS = 4    # XInput supports up to 4 slots


class GamepadManager:
    """
    Polls a single Xbox (XInput) controller and exposes its state using
    the same logical key-name strings as the keyboard mapping, so it can
    be merged transparently into InputManager.

    Button mapping:
        D-Pad / Left stick -> Left, Right, Up, Down
        A                  -> Space (jump), Return (menu confirm)
        B                  -> Escape (back/pause), N (quit-confirm: No)
        X                  -> Y (quit-confirm: Yes)
        Y                  -> L (load saved game)
        Start              -> P (pause)
        Back/View          -> Q (quit)
    """

    def __init__(self):
        self.available = _XINPUT_AVAILABLE
        self.player_index = None  # which XInput slot (0-3) is active, if any
        self.buttons_pressed: Set[str] = set()
        self.buttons_just_pressed: Set[str] = set()
        self._prev_buttons_pressed: Set[str] = set()

    @property
    def is_connected(self) -> bool:
        """True if a controller is actively responding on some slot."""
        return self.available and self.player_index is not None

    def poll(self):
        """Poll the controller. Call once per game tick, before reading state."""
        self._prev_buttons_pressed = self.buttons_pressed

        if not self.available:
            self.buttons_pressed = set()
            self.buttons_just_pressed = set()
            return

        state = _XInputState()

        # Stick with the last known-good slot if we have one (cheaper,
        # avoids scanning every frame); fall back to scanning for the
        # first connected controller if it disconnects.
        indices = [self.player_index] if self.player_index is not None else range(_MAX_CONTROLLERS)

        found_index = None
        for index in indices:
            result = _xinput_dll.XInputGetState(index, ctypes.byref(state))
            if result == 0:  # ERROR_SUCCESS
                found_index = index
                break

        if found_index is None:
            self.player_index = None
            self.buttons_pressed = set()
            self.buttons_just_pressed = set()
            return

        self.player_index = found_index
        pad = state.Gamepad
        wbuttons = pad.wButtons

        pressed: Set[str] = set()

        # D-Pad
        if wbuttons & _XINPUT_GAMEPAD_DPAD_LEFT:
            pressed.add('Left')
        if wbuttons & _XINPUT_GAMEPAD_DPAD_RIGHT:
            pressed.add('Right')
        if wbuttons & _XINPUT_GAMEPAD_DPAD_UP:
            pressed.add('Up')
        if wbuttons & _XINPUT_GAMEPAD_DPAD_DOWN:
            pressed.add('Down')

        # Left analog stick -> same digital directions, with deadzone
        stick_x = pad.sThumbLX / 32767.0
        stick_y = pad.sThumbLY / 32767.0
        if stick_x > _STICK_DEADZONE:
            pressed.add('Right')
        elif stick_x < -_STICK_DEADZONE:
            pressed.add('Left')
        if stick_y > _STICK_DEADZONE:
            pressed.add('Up')
        elif stick_y < -_STICK_DEADZONE:
            pressed.add('Down')

        # Face buttons
        if wbuttons & _XINPUT_GAMEPAD_A:
            pressed.add('Space')
            pressed.add('Return')
        if wbuttons & _XINPUT_GAMEPAD_B:
            pressed.add('Escape')
            pressed.add('N')
        if wbuttons & _XINPUT_GAMEPAD_X:
            pressed.add('Y')
        if wbuttons & _XINPUT_GAMEPAD_Y:
            pressed.add('L')
        if wbuttons & _XINPUT_GAMEPAD_START:
            pressed.add('P')
        if wbuttons & _XINPUT_GAMEPAD_BACK:
            pressed.add('Q')

        self.buttons_pressed = pressed
        self.buttons_just_pressed = pressed - self._prev_buttons_pressed

    def clear_just_pressed(self, key_name: str):
        self.buttons_just_pressed.discard(key_name)

    def clear_all_just_pressed(self):
        self.buttons_just_pressed.clear()


class InputManager:
    """Manages keyboard + gamepad input state."""
    
    def __init__(self):
        self.keys_pressed: Set[str] = set()
        self.keys_just_pressed: Set[str] = set()

        # Xbox controller support (gracefully no-ops if unavailable)
        self.gamepad = GamepadManager()
        
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
            Qt.Key.Key_Q: 'Q',  # Quit
            Qt.Key.Key_Y: 'Y',  # Yes
            Qt.Key.Key_N: 'N',  # No
            Qt.Key.Key_R: 'R',  # Restart
            Qt.Key.Key_L: 'L',  # Load
            Qt.Key.Key_Escape: 'Escape',
            Qt.Key.Key_Return: 'Return',
            Qt.Key.Key_Enter: 'Return',
        }

    def update(self):
        """
        Poll non-keyboard input sources (currently: gamepad).
        Call this once per game tick, BEFORE reading any input state
        (is_key_pressed, is_move_left, is_jump, etc.) - e.g. at the top
        of GameEngine.tick(), right before _handle_input().
        """
        self.gamepad.poll()
        
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
        """Check if a key is currently pressed (keyboard OR gamepad)."""
        return key_name in self.keys_pressed or key_name in self.gamepad.buttons_pressed
        
    def is_key_just_pressed(self, key_name: str) -> bool:
        """Check if a key was just pressed this frame (keyboard OR gamepad)."""
        return key_name in self.keys_just_pressed or key_name in self.gamepad.buttons_just_pressed
        
    def clear_key(self, key_name: str):
        """Clear a key from just-pressed state, on both input sources."""
        self.keys_just_pressed.discard(key_name)
        self.gamepad.clear_just_pressed(key_name)
        
    def clear_all_just_pressed(self):
        """Clear all just-pressed keys (call at end of frame)."""
        self.keys_just_pressed.clear()
        self.gamepad.clear_all_just_pressed()

    @property
    def gamepad_connected(self) -> bool:
        """True if an Xbox controller is currently connected and responding."""
        return self.gamepad.is_connected
        
    def is_move_left(self) -> bool:
        """Check if moving left."""
        return self.is_key_pressed('Left') or self.is_key_pressed('A')
        
    def is_move_right(self) -> bool:
        """Check if moving right."""
        return self.is_key_pressed('Right') or self.is_key_pressed('D')
        
    def is_jump(self) -> bool:
        """Check if jump button is pressed."""
        return self.is_key_just_pressed('Space') or self.is_key_just_pressed('W')
