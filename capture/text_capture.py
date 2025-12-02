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

logger = logging.getLogger(__name__)


class TextCapture:
    """Utilities for capturing text from various sources."""

    @staticmethod
    def capture_selected() -> str:
        """Capture currently selected text by programmatically copying it to clipboard."""
        try:
            # Save the current clipboard content to restore later
            original_clipboard = ""
            try:
                original_clipboard = pyperclip.paste()
            except Exception:
                pass  # Clipboard might be empty or contain non-text

            # Programmatically press Ctrl+C to copy selected text
            keyboard = KeyboardController()

            # Small delay to ensure the keybind release is processed
            time.sleep(0.05)

            # Press Ctrl+C
            keyboard.press(Key.ctrl)
            keyboard.press('c')
            keyboard.release('c')
            keyboard.release(Key.ctrl)

            # Wait for clipboard to update
            time.sleep(0.15)

            # Get the newly copied text
            text = pyperclip.paste()

            if text and isinstance(text, str) and text.strip():
                # Check if we actually got new text (not the same as before)
                if text.strip() != original_clipboard.strip() if original_clipboard else True:
                    logger.info(f"Captured {len(text)} characters from selection")
                    return text.strip()
                else:
                    # Text is same as before - might mean nothing was selected
                    logger.info(f"Captured {len(text)} characters from clipboard (no new selection)")
                    return text.strip()

            logger.debug("No text in clipboard after copy attempt")
            return ""
        except Exception as e:
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
