"""Text capture utilities."""
import logging
import pyperclip
import pytesseract
from PIL import Image
import mss
import tempfile
from pathlib import Path
from pynput.mouse import Controller
from pynput.keyboard import Controller as KeyboardController, Key
import time
import ctypes
import threading

logger = logging.getLogger(__name__)

# Windows API for sending keystrokes more reliably
if hasattr(ctypes, 'windll'):
    user32 = ctypes.windll.user32

    # Virtual key codes
    VK_CONTROL = 0x11
    VK_C = 0x43

    # Key event flags
    KEYEVENTF_KEYUP = 0x0002

    def send_ctrl_c_windows():
        """Send Ctrl+C using Windows API directly."""
        print("    [DEBUG] Sending Ctrl+C via Windows API...")
        # Press Ctrl
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        time.sleep(0.05)
        # Press C
        user32.keybd_event(VK_C, 0, 0, 0)
        time.sleep(0.05)
        # Release C
        user32.keybd_event(VK_C, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        # Release Ctrl
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        print("    [DEBUG] Ctrl+C sent via Windows API")
else:
    send_ctrl_c_windows = None


class TextCapture:
    """Utilities for capturing text from various sources."""

    @staticmethod
    def capture_selected() -> str:
        """Capture currently selected text by programmatically copying it to clipboard."""
        print("\n    [DEBUG] === capture_selected() called ===")
        try:
            # Check clipboard before clearing
            try:
                before_clear = pyperclip.paste()
                print(f"    [DEBUG] Clipboard before clear: {repr(before_clear[:50] if before_clear else 'EMPTY')}...")
            except Exception as e:
                print(f"    [DEBUG] Error reading clipboard before clear: {e}")
                before_clear = ""

            # Clear clipboard first to detect if copy actually happened
            try:
                pyperclip.copy("")
                print("    [DEBUG] Clipboard cleared")
            except Exception as e:
                print(f"    [DEBUG] Error clearing clipboard: {e}")

            # Verify clipboard is cleared
            try:
                after_clear = pyperclip.paste()
                print(f"    [DEBUG] Clipboard after clear: {repr(after_clear) if after_clear else 'EMPTY'}")
            except Exception as e:
                print(f"    [DEBUG] Error verifying clipboard clear: {e}")

            # Wait for user to release the hotkey (Ctrl+Alt+R)
            print("    [DEBUG] Waiting 0.5s for hotkey release...")
            time.sleep(0.5)

            # Use Windows API if available (more reliable)
            if send_ctrl_c_windows:
                print("    [DEBUG] Using Windows API method")
                send_ctrl_c_windows()
            else:
                print("    [DEBUG] Using pynput method (Windows API not available)")
                keyboard = KeyboardController()

                # Release any potentially stuck modifier keys first
                try:
                    keyboard.release(Key.ctrl)
                    keyboard.release(Key.alt)
                    keyboard.release(Key.ctrl_l)
                    keyboard.release(Key.ctrl_r)
                    keyboard.release(Key.alt_l)
                    keyboard.release(Key.alt_r)
                    print("    [DEBUG] Released modifier keys")
                except Exception as e:
                    print(f"    [DEBUG] Error releasing modifiers: {e}")

                time.sleep(0.1)

                # Press and release Ctrl+C
                print("    [DEBUG] Sending Ctrl+C via pynput...")
                keyboard.press(Key.ctrl)
                time.sleep(0.05)
                keyboard.press('c')
                time.sleep(0.05)
                keyboard.release('c')
                time.sleep(0.05)
                keyboard.release(Key.ctrl)
                print("    [DEBUG] Ctrl+C sent via pynput")

            # Wait for clipboard to update
            print("    [DEBUG] Waiting 0.5s for clipboard update...")
            time.sleep(0.5)

            # Get the newly copied text
            try:
                text = pyperclip.paste()
                print(f"    [DEBUG] Clipboard after Ctrl+C: {repr(text[:100] if text else 'EMPTY')}...")
            except Exception as e:
                print(f"    [DEBUG] Error reading clipboard after Ctrl+C: {e}")
                text = ""

            if text and isinstance(text, str) and text.strip():
                print(f"    [DEBUG] SUCCESS! Captured {len(text)} characters")
                logger.info(f"Captured {len(text)} characters from selection")
                return text.strip()

            # If clipboard is empty, nothing was selected
            print("    [DEBUG] FAILED - No text in clipboard after Ctrl+C")
            logger.debug("No text captured - nothing was selected")
            return ""
        except Exception as e:
            print(f"    [DEBUG] EXCEPTION: {e}")
            logger.error(f"Error capturing selected text: {e}")
            return ""

    @staticmethod
    def capture_screenshot() -> str:
        """Capture text from screenshot using OCR."""
        try:
            # Get cursor position to determine which monitor to capture
            mouse = Controller()
            cursor_x, cursor_y = mouse.position

            # Take screenshot
            with mss.mss() as sct:
                # Find which monitor contains the cursor
                target_monitor = sct.monitors[1]  # Default to primary
                for monitor in sct.monitors[1:]:  # Skip monitor[0] (all monitors combined)
                    if (monitor['left'] <= cursor_x < monitor['left'] + monitor['width'] and
                        monitor['top'] <= cursor_y < monitor['top'] + monitor['height']):
                        target_monitor = monitor
                        logger.info(f"Capturing monitor at ({monitor['left']}, {monitor['top']}) where cursor is located")
                        break

                screenshot = sct.grab(target_monitor)

                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    tmp_path = tmp.name
                    mss.tools.to_png(screenshot.rgb, screenshot.size, output=tmp_path)

            # Perform OCR
            image = Image.open(tmp_path)
            text = pytesseract.image_to_string(image)

            # Clean up
            Path(tmp_path).unlink()

            if text:
                logger.info(f"Captured {len(text)} characters from screenshot")
                return text.strip()
            return ""

        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return ""

    @staticmethod
    def capture_clipboard_change() -> str:
        """Monitor clipboard for changes and capture new content."""
        # For alpha version, this is simplified
        # In production, would implement clipboard monitoring
        return TextCapture.capture_selected()


# Global text capture instance
text_capture = TextCapture()
