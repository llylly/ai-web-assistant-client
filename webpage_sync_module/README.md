# Webpage Sync Module

Local service that receives webpage content from Chrome extension, converts to markdown, and syncs to remote server.

## Features

- **HTTP API**: Receives webpage content from Chrome extension via REST API
- **HTML to Markdown**: Converts HTML content to clean, LLM-friendly markdown format
- **Local Storage**: Stores markdown files with metadata
- **SSH/SFTP Sync**: Automatically syncs to remote server using SSH public key authentication
- **History Management**: Maintains a configurable number of recent pages
- **Status Monitoring**: Provides API endpoints for monitoring service health

## Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Copy and configure the settings:

```bash
cp config.yaml.example config.yaml
nano config.yaml
```

3. Update configuration with your server details:
   - SSH server hostname/IP
   - SSH port (default: 22, your case: 9911)
   - Username
   - Remote directory path

## Configuration

Edit `config.yaml`:

```yaml
server:
  host: 192.168.59.111
  port: 9911
  username: your_username
  remote_path: /home/your_username/webpages

sync:
  enabled: true
  auto_sync: true

storage:
  max_files: 100
```

## SSH Setup

Ensure you have SSH key authentication set up:

1. Generate SSH key if you don't have one:
```bash
ssh-keygen -t ed25519
```

2. Copy public key to remote server:
```bash
ssh-copy-id -p 9911 your_username@192.168.59.111
```

3. Test connection:
```bash
ssh -p 9911 your_username@192.168.59.111
```

## Usage

Start the service:

```bash
python sync_service.py
```

The service will:
- Start HTTP server on `http://localhost:8000`
- Accept POST requests from Chrome extension at `/sync`
- Convert HTML to markdown
- Store files in `data/markdown/`
- Sync to remote server automatically

## API Endpoints

### POST /sync
Receive webpage content from Chrome extension

**Request body:**
```json
{
  "id": "unique_id",
  "url": "https://example.com",
  "title": "Page Title",
  "html": "<html>...</html>",
  "text": "Page text...",
  "timestamp": 1234567890000
}
```

**Response:**
```json
{
  "success": true,
  "filename": "20240227_123456_Page_Title",
  "markdown_file": "20240227_123456_Page_Title.md"
}
```

### GET /status
Get service status

**Response:**
```json
{
  "status": "running",
  "markdown_count": 42,
  "config": {...},
  "ssh_connected": true
}
```

### GET /files
List all stored markdown files

**Response:**
```json
{
  "files": [
    {
      "filename": "20240227_123456_Page_Title.md",
      "size": 12345,
      "modified": 1234567890.0,
      "metadata": {...}
    }
  ]
}
```

### GET/POST /config
Get or update configuration

## Directory Structure

```
webpage_sync_module/
├── sync_service.py       # Main service
├── ssh_sync.py          # SSH/SFTP sync module
├── config.yaml          # Configuration (create from .example)
├── config.yaml.example  # Configuration template
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── data/               # Data directory (created automatically)
    ├── markdown/       # Markdown files
    └── metadata/       # Metadata JSON files
```

## Markdown Format

Each markdown file includes:
- Page title as H1 header
- URL reference
- Capture timestamp
- Converted markdown content from HTML

Example:
```markdown
# Example Page Title

**URL:** https://example.com

**Captured:** 2024-02-27T12:34:56

---

[Converted markdown content...]
```

## Troubleshooting

### SSH connection fails
- Verify SSH key is set up correctly
- Check server hostname/port in config
- Test SSH connection manually
- Ensure remote directory exists and is writable

### Chrome extension can't connect
- Verify service is running on port 8000
- Check firewall settings
- Ensure CORS is enabled (should be by default)

### Files not syncing
- Check SSH connection status via `/status` endpoint
- Verify `auto_sync` is enabled in config
- Check logs for error messages

## Logs

The service logs to console with timestamps. Monitor for:
- Connection status
- File conversion progress
- Sync operations
- Errors and warnings
