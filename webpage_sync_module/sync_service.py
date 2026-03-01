"""
Webpage Sync Service
Receives webpage content from Chrome extension, converts to markdown, and syncs to remote server
"""

import os
import json
import logging
import time
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
import html2text
import yaml

from ssh_sync import SSHSync

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

# Configuration
CONFIG_FILE = 'config.yaml'
DATA_DIR = Path('data')
MARKDOWN_DIR = DATA_DIR / 'markdown'
METADATA_DIR = DATA_DIR / 'metadata'
SCREENSHOT_DIR = DATA_DIR / 'screenshots'

# Create directories
MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# HTML to markdown converter
html_converter = html2text.HTML2Text()
html_converter.ignore_links = False
html_converter.ignore_images = False
html_converter.ignore_emphasis = False
html_converter.body_width = 0  # Don't wrap lines
html_converter.unicode_snob = True
html_converter.ignore_tables = False

# SSH sync manager
ssh_sync = None


def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file"""
    if not os.path.exists(CONFIG_FILE):
        logger.warning(f"Config file {CONFIG_FILE} not found, using defaults")
        return {
            'server': {
                'host': '192.168.59.111',
                'port': 9911,
                'username': 'user',
                'remote_path': '/home/user/webpages'
            },
            'sync': {
                'enabled': True,
                'auto_sync': True
            },
            'storage': {
                'max_files': 100
            }
        }

    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    return config


def save_config(config: Dict[str, Any]):
    """Save configuration to YAML file"""
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def html_to_markdown(html: str) -> str:
    """Convert HTML to markdown format"""
    try:
        markdown = html_converter.handle(html)
        return markdown
    except Exception as e:
        logger.error(f"Error converting HTML to markdown: {e}")
        return f"# Error converting content\n\n{str(e)}"


def sanitize_filename(text: str, max_length: int = 100) -> str:
    """Create a safe filename from text"""
    # Remove invalid characters
    safe_chars = []
    for c in text:
        if c.isalnum() or c in (' ', '-', '_'):
            safe_chars.append(c)
        elif c in ('.', ',', '!', '?'):
            safe_chars.append('_')

    filename = ''.join(safe_chars).strip()
    filename = ' '.join(filename.split())  # Normalize whitespace
    filename = filename.replace(' ', '_')

    # Limit length
    if len(filename) > max_length:
        filename = filename[:max_length]

    return filename or 'untitled'


def save_screenshot(data_url: str, path: Path) -> bool:
    """
    Decode a PNG data URL and write it to disk.

    Args:
        data_url: String of the form "data:image/png;base64,<b64>"
        path:     Destination file path (should have .png extension)

    Returns:
        True on success, False on failure
    """
    try:
        # Strip the "data:image/...;base64," prefix
        header, encoded = data_url.split(',', 1)
        image_bytes = base64.b64decode(encoded)
        path.write_bytes(image_bytes)
        return True
    except Exception as e:
        logger.error(f"Error decoding/saving screenshot: {e}")
        return False


def cleanup_old_files(max_files: int):
    """Remove old files if exceeding max_files limit"""
    markdown_files = sorted(MARKDOWN_DIR.glob('*.md'), key=lambda p: p.stat().st_mtime)
    metadata_files = sorted(METADATA_DIR.glob('*.json'), key=lambda p: p.stat().st_mtime)
    screenshot_files = sorted(SCREENSHOT_DIR.glob('*.png'), key=lambda p: p.stat().st_mtime)

    # Remove oldest files
    while len(markdown_files) > max_files:
        oldest = markdown_files.pop(0)
        logger.info(f"Removing old file: {oldest}")
        oldest.unlink()

    while len(metadata_files) > max_files:
        oldest = metadata_files.pop(0)
        oldest.unlink()

    while len(screenshot_files) > max_files:
        oldest = screenshot_files.pop(0)
        oldest.unlink()


@app.route('/sync', methods=['POST'])
def sync_webpage():
    """
    Receive webpage content from Chrome extension and sync to remote server.

    Expected JSON format:
    {
        "id": "unique_id",
        "url": "https://example.com",
        "title": "Page Title",
        "html": "<html>...</html>",
        "text": "Page text...",
        "screenshot": "data:image/png;base64,...",  // optional, null when disabled
        "timestamp": 1234567890000
    }

    Saved files (using the same base filename):
        data/markdown/<filename>.md
        data/screenshots/<filename>.png   (only when screenshot is provided)
        data/metadata/<filename>.json

    Both .md and .png (when present) are uploaded to the remote server via SFTP
    into the same remote_path directory. The AI server identifies pairs by stem.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['id', 'url', 'title', 'html', 'timestamp']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Convert HTML to markdown
        logger.info(f"Processing: {data['title']} - {data['url']}")
        markdown = html_to_markdown(data['html'])

        # Create filename based on timestamp and title (shared by .md and .png)
        timestamp_str = datetime.fromtimestamp(data['timestamp'] / 1000).strftime('%Y%m%d_%H%M%S')
        safe_title = sanitize_filename(data['title'])
        filename = f"{timestamp_str}_{safe_title}"

        # Save markdown file
        markdown_path = MARKDOWN_DIR / f"{filename}.md"
        with open(markdown_path, 'w', encoding='utf-8') as f:
            # Add metadata header
            f.write(f"# {data['title']}\n\n")
            f.write(f"**URL:** {data['url']}\n\n")
            f.write(f"**Captured:** {datetime.fromtimestamp(data['timestamp'] / 1000).isoformat()}\n\n")
            f.write("---\n\n")
            f.write(markdown)

        # Save screenshot if provided by the Chrome extension
        screenshot_path: Optional[Path] = None
        screenshot_data_url = data.get('screenshot')
        if screenshot_data_url:
            screenshot_path = SCREENSHOT_DIR / f"{filename}.png"
            if save_screenshot(screenshot_data_url, screenshot_path):
                logger.info(f"Saved screenshot: {screenshot_path.name}")
            else:
                screenshot_path = None  # Don't attempt to sync a failed save

        # Save metadata
        metadata_path = METADATA_DIR / f"{filename}.json"
        metadata = {
            'id': data['id'],
            'url': data['url'],
            'title': data['title'],
            'timestamp': data['timestamp'],
            'markdown_file': str(markdown_path.name),
            'screenshot_file': str(screenshot_path.name) if screenshot_path else None,
            'processed_at': time.time()
        }
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Saved: {markdown_path.name}")

        # Cleanup old files
        config = load_config()
        max_files = config.get('storage', {}).get('max_files', 100)
        cleanup_old_files(max_files)

        # Sync to remote server if enabled: upload .md first, then .png if captured
        if ssh_sync and config.get('sync', {}).get('auto_sync', True):
            try:
                ssh_sync.sync_file(markdown_path)
                logger.info(f"Synced markdown to remote server: {markdown_path.name}")
            except Exception as e:
                logger.error(f"Error syncing markdown to remote server: {e}")

            if screenshot_path:
                try:
                    ssh_sync.sync_file(screenshot_path)
                    logger.info(f"Synced screenshot to remote server: {screenshot_path.name}")
                except Exception as e:
                    logger.error(f"Error syncing screenshot to remote server: {e}")

        return jsonify({
            'success': True,
            'filename': filename,
            'markdown_file': str(markdown_path.name),
            'screenshot_file': str(screenshot_path.name) if screenshot_path else None
        })

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    """Get service status"""
    config = load_config()
    markdown_count = len(list(MARKDOWN_DIR.glob('*.md')))

    return jsonify({
        'status': 'running',
        'markdown_count': markdown_count,
        'config': config,
        'ssh_connected': ssh_sync.is_connected() if ssh_sync else False
    })


@app.route('/config', methods=['GET', 'POST'])
def config_endpoint():
    """Get or update configuration"""
    if request.method == 'GET':
        config = load_config()
        return jsonify(config)
    else:
        try:
            new_config = request.get_json()
            save_config(new_config)

            # Reinitialize SSH sync if server config changed
            global ssh_sync
            if new_config.get('sync', {}).get('enabled', True):
                ssh_sync = SSHSync(new_config['server'])

            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/files', methods=['GET'])
def list_files():
    """List all stored markdown files"""
    files = []
    for md_file in sorted(MARKDOWN_DIR.glob('*.md'), key=lambda p: p.stat().st_mtime, reverse=True):
        metadata_file = METADATA_DIR / f"{md_file.stem}.json"
        metadata = {}
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

        files.append({
            'filename': md_file.name,
            'size': md_file.stat().st_size,
            'modified': md_file.stat().st_mtime,
            'metadata': metadata
        })

    return jsonify({'files': files})


def initialize_ssh_sync():
    """Initialize SSH sync connection"""
    global ssh_sync
    config = load_config()

    if config.get('sync', {}).get('enabled', True):
        try:
            ssh_sync = SSHSync(config['server'])
            logger.info("SSH sync initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SSH sync: {e}")
            ssh_sync = None


def main():
    """Main entry point"""
    logger.info("Starting Webpage Sync Service")

    # Initialize SSH sync
    initialize_ssh_sync()

    # Start Flask app
    app.run(host='0.0.0.0', port=8000, debug=False)


if __name__ == '__main__':
    main()
