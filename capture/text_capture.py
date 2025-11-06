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
        """Capture text from clipboard (user should copy with Ctrl+C first)."""
        try:
            # Get current clipboard content
            text = pyperclip.paste()

            if text and isinstance(text, str) and text.strip():
                logger.info(f"Captured {len(text)} characters from clipboard")
                return text.strip()

            logger.debug("No text in clipboard")
            return ""
        except Exception as e:
            logger.error(f"Error capturing clipboard text: {e}")
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
