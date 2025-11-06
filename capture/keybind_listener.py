"""Keybind listener for capturing user input."""
import logging
from typing import Callable, Dict
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
import threading

logger = logging.getLogger(__name__)


class KeybindListener:
    """Listen for and handle keybind events."""

    def __init__(self):
        """Initialize keybind listener."""
        self.keybinds: Dict[str, Callable] = {}
        self.current_keys = set()
        self.listener = None
        self.is_running = False
        # Track modifier keys
        self.ctrl_pressed = False
        self.alt_pressed = False
        # Map control characters and key codes to keybind sequences
        # On Windows, Ctrl+Alt+R/T produce these instead of key combos
        self.control_char_map = {
            '\x12': '<ctrl>+<alt>+r',  # Ctrl+Alt+R
        }
        self.key_code_map = {
            82: '<ctrl>+<alt>+r',  # Ctrl+Alt+R (vk=82)
            84: '<ctrl>+<alt>+t',  # Ctrl+Alt+T (vk=84)
        }

    def parse_key_sequence(self, key_sequence: str) -> set:
        """Parse key sequence string into set of keys."""
        # Parse strings like '<ctrl>+<alt>+r'
        keys = set()
        parts = key_sequence.lower().replace(' ', '').split('+')

        for part in parts:
            part = part.strip('<>')
            if part == 'ctrl':
                keys.add(Key.ctrl_l)
            elif part == 'alt':
                keys.add(Key.alt_l)
            elif part == 'shift':
                keys.add(Key.shift_l)
            elif part == 'cmd' or part == 'win':
                keys.add(Key.cmd)
            elif len(part) == 1:
                keys.add(KeyCode.from_char(part))
            else:
                # Try to get special key
                try:
                    keys.add(getattr(Key, part))
                except AttributeError:
                    logger.warning(f"Unknown key: {part}")

        return keys

    def register_keybind(self, key_sequence: str, callback: Callable):
        """Register a keybind with a callback."""
        self.keybinds[key_sequence] = callback
        logger.info(f"Registered keybind: {key_sequence}")

    def unregister_keybind(self, key_sequence: str):
        """Unregister a keybind."""
        if key_sequence in self.keybinds:
            del self.keybinds[key_sequence]
            logger.info(f"Unregistered keybind: {key_sequence}")

    def _on_press(self, key):
        """Handle key press events."""
        try:
            # Track modifier keys
            if key in (Key.ctrl_l, Key.ctrl_r):
                self.ctrl_pressed = True
            if key in (Key.alt_l, Key.alt_r, Key.alt_gr):
                self.alt_pressed = True

            # Debug: print raw key info
            if hasattr(key, 'char'):
                print(f"Key pressed - char: {repr(key.char)}, key: {key}, ctrl={self.ctrl_pressed}, alt={self.alt_pressed}")
            else:
                print(f"Key pressed - key: {key}, ctrl={self.ctrl_pressed}, alt={self.alt_pressed}")

            # Check for control characters first (Windows Ctrl+Alt+key handling)
            if hasattr(key, 'char') and key.char and key.char in self.control_char_map:
                key_sequence = self.control_char_map[key.char]
                print(f"🎯 Control char detected: {repr(key.char)} -> {key_sequence}")
                if key_sequence in self.keybinds:
                    logger.debug(f"Keybind triggered via control char: {key_sequence}")
                    self.keybinds[key_sequence]()
                return

            # Check for special key codes ONLY if modifiers are pressed
            if hasattr(key, 'vk') and key.vk in self.key_code_map and self.ctrl_pressed and self.alt_pressed:
                key_sequence = self.key_code_map[key.vk]
                print(f"🎯 Key code detected: vk={key.vk} -> {key_sequence}")
                if key_sequence in self.keybinds:
                    logger.debug(f"Keybind triggered via key code: {key_sequence}")
                    self.keybinds[key_sequence]()
                return

            # Normalize key
            if hasattr(key, 'char') and key.char:
                normalized_key = KeyCode.from_char(key.char.lower())
            else:
                normalized_key = key

            self.current_keys.add(normalized_key)

            # Check if any keybind matches
            for key_sequence, callback in self.keybinds.items():
                expected_keys = self.parse_key_sequence(key_sequence)
                if expected_keys.issubset(self.current_keys):
                    logger.debug(f"Keybind triggered: {key_sequence}")
                    callback()

        except Exception as e:
            logger.error(f"Error in key press handler: {e}")

    def _on_release(self, key):
        """Handle key release events."""
        try:
            # Track modifier key releases
            if key in (Key.ctrl_l, Key.ctrl_r):
                self.ctrl_pressed = False
            if key in (Key.alt_l, Key.alt_r, Key.alt_gr):
                self.alt_pressed = False

            # Normalize key
            if hasattr(key, 'char') and key.char:
                normalized_key = KeyCode.from_char(key.char.lower())
            else:
                normalized_key = key

            if normalized_key in self.current_keys:
                self.current_keys.remove(normalized_key)

        except Exception as e:
            logger.error(f"Error in key release handler: {e}")

    def start(self):
        """Start listening for keybinds."""
        if self.is_running:
            logger.warning("Keybind listener already running")
            return

        self.is_running = True
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        logger.info("Keybind listener started")

    def stop(self):
        """Stop listening for keybinds."""
        if not self.is_running:
            return

        self.is_running = False
        if self.listener:
            self.listener.stop()
        self.current_keys.clear()
        self.ctrl_pressed = False
        self.alt_pressed = False
        logger.info("Keybind listener stopped")


# Global listener instance
keybind_listener = KeybindListener()
