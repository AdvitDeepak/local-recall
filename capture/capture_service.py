"""Background capture service."""
import logging
import asyncio
from typing import Optional
import httpx

from capture.keybind_listener import keybind_listener
from capture.text_capture import text_capture
from database import db
from config import settings

logger = logging.getLogger(__name__)


class CaptureService:
    """Background service for capturing text based on keybinds."""

    def __init__(self):
        """Initialize capture service."""
        self.is_running = False
        self.api_base_url = f"http://localhost:{settings.BACKEND_PORT}"

    def _on_capture_selected(self):
        """Callback for capture selected text keybind."""
        try:
            print("\n" + "="*60)
            print("🔍 KEYBIND DETECTED: Ctrl+Alt+R - Capturing selected text...")
            print("="*60)
            logger.info("Keybind detected: Ctrl+Alt+R")

            # Check system state
            state = db.get_system_state()
            print(f"    [DEBUG] System state: is_capturing={state.is_capturing if state else 'NO STATE'}")

            if not state or not state.is_capturing:
                logger.debug("Capture is paused, ignoring keybind")
                print("⚠️  Capture is paused. Start capturing from dashboard first.")
                notif = db.add_notification(
                    type="capture_selected",
                    title="Capture Paused",
                    message="Capture is paused. Start capturing from the dashboard first.",
                    status="warning"
                )
                print(f"    [DEBUG] Created notification ID: {notif.id}")
                return

            print("    [DEBUG] Calling text_capture.capture_selected()...")
            text = text_capture.capture_selected()
            print(f"    [DEBUG] capture_selected() returned: {len(text) if text else 0} chars")

            if text:
                # Add to database
                print("    [DEBUG] Adding entry to database...")
                entry = db.add_entry(
                    content=text,
                    source="clipboard",
                    capture_method="selected"
                )
                print(f"✅ Captured selected text: entry {entry.id} ({len(text)} chars)")
                logger.info(f"Captured selected text: entry {entry.id}")
                # Add success notification to database (persistent)
                preview = text[:50] + "..." if len(text) > 50 else text
                print("    [DEBUG] Adding success notification to database...")
                notif = db.add_notification(
                    type="capture_selected",
                    title="Text Captured",
                    message=f"Entry #{entry.id}: {len(text)} chars captured. Preview: \"{preview}\"",
                    status="success"
                )
                print(f"    [DEBUG] Created notification ID: {notif.id}")
            else:
                print("⚠️  No text to capture - make sure text is selected")
                logger.debug("No text to capture")
                print("    [DEBUG] Adding warning notification to database...")
                notif = db.add_notification(
                    type="capture_selected",
                    title="No Text Found",
                    message="No text found. Make sure text is selected before pressing the keybind.",
                    status="warning"
                )
                print(f"    [DEBUG] Created notification ID: {notif.id}")
            print("="*60 + "\n")
        except Exception as e:
            print(f"❌ Error capturing text: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Error in capture_selected callback: {e}")
            db.add_notification(
                type="capture_selected",
                title="Capture Error",
                message=f"Error capturing text: {str(e)}",
                status="error"
            )

    def _on_capture_screenshot(self):
        """Callback for capture screenshot keybind."""
        try:
            print("\n📸 KEYBIND DETECTED: Ctrl+Alt+T - Capturing screenshot text...")
            logger.info("Keybind detected: Ctrl+Alt+T")

            if not db.get_system_state().is_capturing:
                logger.debug("Capture is paused, ignoring keybind")
                print("⚠️  Capture is paused. Start capturing from dashboard first.")
                db.add_notification(
                    type="capture_screenshot",
                    title="Capture Paused",
                    message="Capture is paused. Start capturing from the dashboard first.",
                    status="warning"
                )
                return

            text = text_capture.capture_screenshot()
            if text:
                # Add to database
                entry = db.add_entry(
                    content=text,
                    source="screenshot",
                    capture_method="screenshot"
                )
                print(f"✅ Captured screenshot text: entry {entry.id} ({len(text)} chars)")
                logger.info(f"Captured screenshot text: entry {entry.id}")
                # Add success notification to database (persistent)
                preview = text[:50] + "..." if len(text) > 50 else text
                db.add_notification(
                    type="capture_screenshot",
                    title="Screenshot Captured",
                    message=f"Entry #{entry.id}: {len(text)} chars captured via OCR. Preview: \"{preview}\"",
                    status="success"
                )
            else:
                print("⚠️  No text found in screenshot")
                logger.debug("No text found in screenshot")
                db.add_notification(
                    type="capture_screenshot",
                    title="No Text Found",
                    message="No text found in screenshot. Make sure there is visible text on screen.",
                    status="warning"
                )
        except Exception as e:
            print(f"❌ Error capturing screenshot: {e}")
            logger.error(f"Error in capture_screenshot callback: {e}")
            db.add_notification(
                type="capture_screenshot",
                title="Screenshot Error",
                message=f"Error capturing screenshot: {str(e)}",
                status="error"
            )

    def load_keybinds(self):
        """Load keybinds from database and register them."""
        try:
            keybinds = db.get_keybinds()
            for kb in keybinds:
                if kb.action == "capture_selected":
                    keybind_listener.register_keybind(
                        kb.key_sequence,
                        self._on_capture_selected
                    )
                    logger.info(f"Registered keybind: {kb.key_sequence} -> capture_selected")
                elif kb.action == "capture_screenshot":
                    keybind_listener.register_keybind(
                        kb.key_sequence,
                        self._on_capture_screenshot
                    )
                    logger.info(f"Registered keybind: {kb.key_sequence} -> capture_screenshot")
            logger.info(f"Loaded {len(keybinds)} keybinds")
        except Exception as e:
            logger.error(f"Error loading keybinds: {e}")

    def start(self):
        """Start the capture service."""
        if self.is_running:
            logger.warning("Capture service already running")
            return

        self.is_running = True

        # Load and register keybinds
        self.load_keybinds()

        # Start keybind listener
        keybind_listener.start()

        # Set capturing state
        db.set_capturing(True)

        logger.info("Capture service started")

    def stop(self):
        """Stop the capture service."""
        if not self.is_running:
            return

        self.is_running = False

        # Stop keybind listener
        keybind_listener.stop()

        # Set capturing state
        db.set_capturing(False)

        logger.info("Capture service stopped")

    def add_default_keybinds(self):
        """Add default keybinds, clearing old ones if they use outdated sequences."""
        existing = db.get_keybinds()

        # Check if existing keybinds use old sequences
        old_sequences = ["<ctrl>+<shift>+c", "<ctrl>+<shift>+s"]
        has_old_keybinds = any(kb.key_sequence in old_sequences for kb in existing)

        if has_old_keybinds:
            logger.info("Found old keybind sequences, clearing and updating...")
            db.clear_keybinds()
            existing = []

        if not existing:
            # Add default keybinds
            db.add_keybind("capture_selected", "<ctrl>+<alt>+r")
            db.add_keybind("capture_screenshot", "<ctrl>+<alt>+t")
            logger.info("Added default keybinds: Ctrl+Alt+R (selected) and Ctrl+Alt+T (screenshot)")


# Global capture service instance
capture_service = CaptureService()
