"""
File Watcher Module
Monitors directory for new markdown files
"""

import logging
import time
from pathlib import Path
from typing import Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

logger = logging.getLogger(__name__)


class MarkdownFileHandler(FileSystemEventHandler):
    """Handles new markdown file events"""

    def __init__(self, callback: Callable[[Path], None]):
        """
        Initialize handler

        Args:
            callback: Function to call when new markdown file is detected
        """
        self.callback = callback
        self.processing = set()

    def on_created(self, event: FileCreatedEvent):
        """Handle file creation event"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process markdown files
        if file_path.suffix != '.md':
            return

        # Avoid duplicate processing
        if file_path in self.processing:
            return

        self.processing.add(file_path)
        logger.info(f"New markdown file detected: {file_path.name}")

        try:
            self.callback(file_path)
        finally:
            self.processing.discard(file_path)


class FileWatcher:
    """Watches directory for new markdown files"""

    def __init__(self, watch_dir: Path, callback: Callable[[Path], None]):
        """
        Initialize file watcher

        Args:
            watch_dir: Directory to watch
            callback: Function to call when new file is detected
        """
        self.watch_dir = watch_dir
        self.callback = callback
        self.observer = Observer()
        self.handler = MarkdownFileHandler(callback)

    def start(self):
        """Start watching directory"""
        self.observer.schedule(self.handler, str(self.watch_dir), recursive=False)
        self.observer.start()
        logger.info(f"Started watching directory: {self.watch_dir}")

    def stop(self):
        """Stop watching directory"""
        self.observer.stop()
        self.observer.join()
        logger.info("Stopped file watcher")

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
