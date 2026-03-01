"""
AI Server Module
Desktop server that monitors markdown files, processes with LLM, and displays results
"""

import os
import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, jsonify, send_from_directory
import yaml

from file_watcher import FileWatcher
from llm_processor import LLMProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
CONFIG_FILE = 'config.yaml'
WATCH_DIR = Path('webpages')
PROCESSED_DIR = Path('processed')
OUTPUT_DIR = Path('output')

# Create directories
WATCH_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Global objects
file_watcher: Optional[FileWatcher] = None
llm_processor: Optional[LLMProcessor] = None
processed_files: list = []


def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file"""
    if not os.path.exists(CONFIG_FILE):
        logger.warning(f"Config file {CONFIG_FILE} not found, using defaults")
        return {
            'llm': {
                'provider': 'openai',  # openai, anthropic, or local
                'model': 'gpt-4-turbo-preview',
                'api_key': '',
                'system_prompt': 'You are a helpful assistant that summarizes and analyzes web content.'
            },
            'server': {
                'host': '0.0.0.0',
                'port': 5000
            },
            'watch': {
                'directory': str(WATCH_DIR),
                'auto_process': True
            }
        }

    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    return config


def save_config(config: Dict[str, Any]):
    """Save configuration to YAML file"""
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def process_markdown_file(file_path: Path, config: Dict[str, Any]):
    """Process a markdown file with LLM"""
    try:
        logger.info(f"Processing file: {file_path.name}")

        # Read markdown content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract metadata from markdown header
        metadata = extract_metadata(content)

        # Process with LLM
        llm_response = llm_processor.process(content, config['llm'])

        # Generate HTML output
        output_filename = f"{file_path.stem}.html"
        output_path = OUTPUT_DIR / output_filename

        # Create HTML page
        html_content = generate_html_page(
            title=metadata.get('title', 'Untitled'),
            url=metadata.get('url', ''),
            captured_at=metadata.get('captured', ''),
            original_content=content,
            llm_response=llm_response,
            llm_config=config['llm']
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Move processed file
        processed_path = PROCESSED_DIR / file_path.name
        file_path.rename(processed_path)

        # Add to processed files list
        processed_entry = {
            'filename': file_path.name,
            'output_file': output_filename,
            'title': metadata.get('title', 'Untitled'),
            'url': metadata.get('url', ''),
            'captured_at': metadata.get('captured', ''),
            'processed_at': datetime.now().isoformat(),
            'llm_provider': config['llm']['provider'],
            'llm_model': config['llm']['model']
        }
        processed_files.insert(0, processed_entry)

        # Keep only last 100 entries
        if len(processed_files) > 100:
            processed_files.pop()

        logger.info(f"Successfully processed: {file_path.name}")

    except Exception as e:
        logger.error(f"Error processing file {file_path.name}: {e}", exc_info=True)


def extract_metadata(markdown_content: str) -> Dict[str, str]:
    """Extract metadata from markdown header"""
    metadata = {}
    lines = markdown_content.split('\n')

    for line in lines[:10]:  # Check first 10 lines
        if line.startswith('# '):
            metadata['title'] = line[2:].strip()
        elif line.startswith('**URL:**'):
            metadata['url'] = line.replace('**URL:**', '').strip()
        elif line.startswith('**Captured:**'):
            metadata['captured'] = line.replace('**Captured:**', '').strip()

    return metadata


def generate_html_page(title: str, url: str, captured_at: str,
                       original_content: str, llm_response: str,
                       llm_config: Dict[str, Any]) -> str:
    """Generate HTML page with original content and LLM response"""
    import markdown2

    # Convert markdown to HTML
    original_html = markdown2.markdown(original_content, extras=['tables', 'fenced-code-blocks'])
    response_html = markdown2.markdown(llm_response, extras=['tables', 'fenced-code-blocks'])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .metadata {{
            color: #666;
            font-size: 14px;
        }}

        .metadata a {{
            color: #3498db;
            text-decoration: none;
        }}

        .metadata a:hover {{
            text-decoration: underline;
        }}

        .content-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}

        @media (max-width: 1024px) {{
            .content-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .panel {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .panel h2 {{
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }}

        .llm-badge {{
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            margin-left: 10px;
        }}

        .content {{
            overflow-y: auto;
            max-height: calc(100vh - 300px);
        }}

        .content pre {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }}

        .content code {{
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
        }}

        .content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}

        .content th,
        .content td {{
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }}

        .content th {{
            background: #f8f9fa;
            font-weight: 600;
        }}

        .content img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}

        .back-link {{
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            transition: background 0.2s;
        }}

        .back-link:hover {{
            background: #2980b9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <div class="metadata">
                <p><strong>URL:</strong> <a href="{url}" target="_blank">{url}</a></p>
                <p><strong>Captured:</strong> {captured_at}</p>
                <p><strong>LLM:</strong> {llm_config['provider']} - {llm_config['model']}</p>
            </div>
        </header>

        <div class="content-grid">
            <div class="panel">
                <h2>📄 Original Content</h2>
                <div class="content">
                    {original_html}
                </div>
            </div>

            <div class="panel">
                <h2>🤖 AI Analysis <span class="llm-badge">{llm_config['provider']}</span></h2>
                <div class="content">
                    {response_html}
                </div>
            </div>
        </div>

        <a href="/" class="back-link">← Back to Dashboard</a>
    </div>
</body>
</html>"""

    return html


# Flask routes

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html', files=processed_files)


@app.route('/view/<filename>')
def view_file(filename):
    """View processed file"""
    return send_from_directory(OUTPUT_DIR, filename)


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

            # Reinitialize LLM processor
            global llm_processor
            llm_processor = LLMProcessor(new_config['llm'])

            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/process/<filename>', methods=['POST'])
def process_file_endpoint(filename):
    """Manually trigger processing of a file"""
    try:
        file_path = WATCH_DIR / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404

        config = load_config()
        process_markdown_file(file_path, config)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/files', methods=['GET'])
def list_files():
    """List all processed files"""
    return jsonify({'files': processed_files})


@app.route('/status', methods=['GET'])
def status():
    """Get server status"""
    config = load_config()
    watch_files = len(list(WATCH_DIR.glob('*.md')))

    return jsonify({
        'status': 'running',
        'config': config,
        'watch_directory': str(WATCH_DIR),
        'pending_files': watch_files,
        'processed_files': len(processed_files),
        'llm_initialized': llm_processor is not None
    })


def on_new_file(file_path: Path):
    """Callback when new file is detected"""
    config = load_config()
    if config.get('watch', {}).get('auto_process', True):
        # Give file time to finish writing
        time.sleep(1)
        process_markdown_file(file_path, config)
    
    ## Keep only the latest max_files files in the watch directory
    if config.get('watch', {}).get('max_files', 100):
        files = list(WATCH_DIR.glob('*.md'))
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for file in files[config.get('watch', {}).get('max_files', 100):]:
            logger.info(f"Removing old file: {file.name}")
            file.unlink()


def main():
    """Main entry point"""
    global file_watcher, llm_processor

    logger.info("Starting AI Server Module")

    # Load configuration
    config = load_config()

    # Initialize LLM processor
    llm_processor = LLMProcessor(config['llm'])

    # Initialize file watcher
    file_watcher = FileWatcher(WATCH_DIR, on_new_file)
    file_watcher.start()

    # Start Flask app
    try:
        app.run(
            host=config['server']['host'],
            port=config['server']['port'],
            debug=False
        )
    finally:
        if file_watcher:
            file_watcher.stop()


if __name__ == '__main__':
    main()
