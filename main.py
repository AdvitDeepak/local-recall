"""Main entry point for Local Recall system."""
import logging
import asyncio
import argparse
from pathlib import Path

from config import settings, ensure_directories
from capture import capture_service
from database import db

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_system():
    """Initialize the Local Recall system."""
    logger.info("Initializing Local Recall...")

    # Ensure directories exist
    ensure_directories()

    # Add default keybinds if needed
    capture_service.add_default_keybinds()

    logger.info("System initialized")


def run_capture_service():
    """Run the capture service."""
    logger.info("Starting Local Recall capture service...")

    try:
        # Initialize system
        init_system()

        # Start capture service
        capture_service.start()

        logger.info("Capture service is running. Press Ctrl+C to stop.")
        logger.info(f"Default keybinds:")
        logger.info("  Windows/Linux:")
        logger.info("    - Ctrl+Alt+R: Capture selected text")
        logger.info("    - Ctrl+Alt+T: Capture screenshot text")
        logger.info("  Mac:")
        logger.info("    - Cmd+Ctrl+R: Capture selected text")
        logger.info("    - Cmd+Ctrl+T: Capture screenshot text")

        # Keep running
        while True:
            import time
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("\nStopping capture service...")
        capture_service.stop()
        logger.info("Capture service stopped")
    except Exception as e:
        logger.error(f"Error running capture service: {e}")
        capture_service.stop()


def run_backend():
    """Run the FastAPI backend."""
    import uvicorn
    from backend.api import app

    logger.info("Starting Local Recall backend...")
    init_system()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )


def run_frontend():
    """Run the Streamlit frontend."""
    import subprocess

    logger.info("Starting Local Recall frontend...")
    init_system()

    subprocess.run([
        "streamlit",
        "run",
        "frontend/app.py",
        "--server.port", str(settings.FRONTEND_PORT),
        "--server.address", "localhost"
    ])


def run_all():
    """Run all components (backend, frontend, capture)."""
    import subprocess
    import sys

    logger.info("Starting all Local Recall components...")
    init_system()

    # Start backend
    backend_process = subprocess.Popen(
        [sys.executable, "main.py", "backend"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait a bit for backend to start
    import time
    time.sleep(2)

    # Start frontend
    frontend_process = subprocess.Popen(
        [sys.executable, "main.py", "frontend"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Start capture service
    try:
        run_capture_service()
    except KeyboardInterrupt:
        logger.info("\nStopping all components...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        logger.info("All components stopped")


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(description="Local Recall - Privacy-preserving text capture and RAG")

    parser.add_argument(
        'command',
        choices=['backend', 'frontend', 'capture', 'all', 'init'],
        help='Component to run'
    )

    args = parser.parse_args()

    if args.command == 'backend':
        run_backend()
    elif args.command == 'frontend':
        run_frontend()
    elif args.command == 'capture':
        run_capture_service()
    elif args.command == 'all':
        run_all()
    elif args.command == 'init':
        init_system()
        logger.info("System initialized successfully")


if __name__ == "__main__":
    main()
