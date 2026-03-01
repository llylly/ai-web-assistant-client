Note: The `aiserver_module` module is outdated. Please see its separate corresponding repo.

Pure generated from vibe coding.

--------------

# AI-Powered Web Reading System

A cross-platform system that monitors your web browsing, converts content to markdown, and uses LLM to provide intelligent analysis and assistance.

## Overview

This system consists of three integrated modules:

1. **Chrome Extension** - Monitors your browsing activity
2. **Webpage Sync Service** (MacBook) - Converts HTML to markdown and syncs to server
3. **AI Server** (Desktop) - Processes content with LLM and displays results

### Data Flow

```
Chrome Browser → Extension monitors tabs
       ↓
Local Sync Service (MacBook)
       ├─ Converts HTML to Markdown
       └─ Syncs via SSH
              ↓
Desktop AI Server (4090)
       ├─ Processes with LLM
       └─ Displays in Web UI
```

## Quick Start

### 1. Chrome Extension Setup

```bash
cd chrome_plugin_module
```

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `chrome_plugin_module` directory
5. Configure sync URL to `http://localhost:8000/sync`

**Note**: You'll need to create placeholder icons in the `icons/` directory or the extension will show default icons.

### 2. Webpage Sync Service (MacBook)

```bash
cd webpage_sync_module
pip install -r requirements.txt
cp config.yaml.example config.yaml
nano config.yaml  # Configure SSH settings
python sync_service.py
```

The service will start on `http://localhost:8000`

### 3. AI Server (Desktop with 4090)

```bash
cd aiserver_module
pip install -r requirements.txt
cp config.yaml.example config.yaml
nano config.yaml  # Configure LLM provider and API key
python ai_server.py
```

The dashboard will be available at `http://localhost:5000`

## Architecture

### Chrome Extension (`chrome_plugin_module`)

**Technology**: JavaScript (Manifest V3)

**Features**:
- Monitors active tab every 30 seconds (configurable)
- Extracts clean HTML content
- Maintains history of last 100 pages
- Sends content to local sync service

**Files**:
- `manifest.json` - Extension configuration
- `background.js` - Background service worker
- `content.js` - Content extraction script
- `popup.html/js` - Configuration UI

### Webpage Sync Service (`webpage_sync_module`)

**Technology**: Python + Flask

**Features**:
- HTTP server receives content from Chrome
- Converts HTML to markdown using html2text
- Stores markdown files locally
- Syncs to remote server via SSH/SFTP
- Manages file history (configurable limit)

**Files**:
- `sync_service.py` - Main Flask application
- `ssh_sync.py` - SSH/SFTP sync module
- `config.yaml` - Configuration

**API Endpoints**:
- `POST /sync` - Receive webpage content
- `GET /status` - Service status
- `GET /files` - List stored files
- `GET/POST /config` - Configuration management

### AI Server (`aiserver_module`)

**Technology**: Python + Flask

**Features**:
- Monitors directory for new markdown files
- Processes content with LLM (OpenAI, Anthropic, or local)
- Generates beautiful HTML reports
- Web dashboard for viewing results
- Configurable system prompts

**Files**:
- `ai_server.py` - Main Flask application
- `llm_processor.py` - LLM integration
- `file_watcher.py` - File monitoring
- `templates/dashboard.html` - Web UI
- `config.yaml` - Configuration

**Supported LLM Providers**:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Local models (Ollama, LM Studio)

## Configuration

### Chrome Extension

Configure via popup UI:
- Monitor interval: 10-300 seconds
- Max history: 10-1000 pages
- Sync server URL: Default `http://localhost:8000/sync`

### Webpage Sync Service

Edit `webpage_sync_module/config.yaml`:

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

### AI Server

Edit `aiserver_module/config.yaml`:

```yaml
llm:
  provider: openai  # or anthropic, local
  model: gpt-4-turbo-preview
  api_key: your_api_key_here
  system_prompt: |
    You are a helpful assistant that analyzes web content.

server:
  host: 0.0.0.0
  port: 5000

watch:
  auto_process: true
```

## SSH Setup

For syncing from MacBook to desktop server:

1. Generate SSH key on MacBook (if not exists):
```bash
ssh-keygen -t ed25519
```

2. Copy public key to desktop server:
```bash
ssh-copy-id -p 9911 username@192.168.59.111
```

3. Test connection:
```bash
ssh -p 9911 username@192.168.59.111
```

## Use Cases

### Translation Assistant

Configure AI server with translation prompt:
```yaml
system_prompt: |
  Translate the following content to English while preserving
  structure and key information.
```

Browse foreign language websites and get instant translations.

### Research Assistant

Configure AI server for research:
```yaml
system_prompt: |
  Extract and organize:
  1. Main concepts and definitions
  2. Key findings
  3. References
  4. Questions for further study
```

Browse academic papers and get structured summaries.

### Learning Assistant

Configure AI server for learning:
```yaml
system_prompt: |
  Explain the content in simple terms, providing:
  1. Core concepts
  2. Examples
  3. Practical applications
```

Browse technical documentation and get explanations.

### News Summarizer

Configure AI server for news:
```yaml
system_prompt: |
  Summarize the news article focusing on:
  1. Main story (who, what, when, where, why)
  2. Key facts
  3. Implications
```

Browse news sites and get quick summaries.

## System Requirements

### MacBook (Webpage Sync Service)
- Python 3.8+
- Network access to desktop server
- SSH client

### Desktop Server (AI Server)
- Python 3.8+
- NVIDIA GPU (optional, for local models)
- CUDA toolkit (optional)
- 4GB+ RAM
- Network accessible from MacBook

### Chrome Browser
- Chrome/Chromium with Manifest V3 support
- Extension permissions for all URLs

## File Structure

```
chrome_plugin_development/
├── README.md                    # This file
├── claude.md                    # Project instructions
├── requirement.md              # Initial requirements
│
├── chrome_plugin_module/       # Chrome Extension
│   ├── manifest.json
│   ├── background.js
│   ├── content.js
│   ├── popup.html
│   ├── popup.js
│   ├── icons/
│   └── README.md
│
├── webpage_sync_module/        # Sync Service (MacBook)
│   ├── sync_service.py
│   ├── ssh_sync.py
│   ├── config.yaml.example
│   ├── requirements.txt
│   ├── data/
│   │   ├── markdown/
│   │   └── metadata/
│   └── README.md
│
└── aiserver_module/            # AI Server (Desktop)
    ├── ai_server.py
    ├── llm_processor.py
    ├── file_watcher.py
    ├── config.yaml.example
    ├── requirements.txt
    ├── templates/
    │   └── dashboard.html
    ├── webpages/
    ├── processed/
    ├── output/
    └── README.md
```

## Troubleshooting

### Chrome Extension Issues

**Extension not loading:**
- Check for errors in `chrome://extensions/`
- Ensure all required files are present
- Create placeholder icon files

**Not capturing pages:**
- Check extension is enabled
- Verify monitor interval setting
- Check browser console for errors

### Sync Service Issues

**Cannot connect to extension:**
- Verify service is running on port 8000
- Check firewall settings
- Test with `curl http://localhost:8000/status`

**SSH sync failing:**
- Test SSH connection manually
- Verify SSH key is set up
- Check remote directory permissions

### AI Server Issues

**Files not processing:**
- Verify files are in `webpages/` directory
- Check `auto_process` is enabled
- Review server logs

**LLM errors:**
- Verify API key is correct
- Check API quota
- Test with mock processor first

## Performance Tips

1. **Monitor Interval**: Start with 60 seconds to reduce overhead
2. **History Size**: Reduce if using limited storage
3. **Content Truncation**: Large pages are automatically truncated
4. **LLM Model**: Use GPT-3.5 for faster processing, GPT-4 for better quality
5. **Local Processing**: Use Ollama with 4090 GPU for fastest local processing

## Security Considerations

- **API Keys**: Store securely, never commit to version control
- **SSH Keys**: Use strong keys, protect private keys
- **Network**: Consider firewall rules for production use
- **HTTPS**: Use HTTPS for production deployments
- **CORS**: Configured for localhost by default

## Development

### Adding New Features

**Chrome Extension**:
- Modify `background.js` for monitoring logic
- Update `popup.html/js` for UI changes

**Sync Service**:
- Add endpoints in `sync_service.py`
- Enhance markdown conversion in html2text configuration

**AI Server**:
- Add LLM providers in `llm_processor.py`
- Customize prompts in configuration
- Modify templates for UI changes

### Testing

**Chrome Extension**:
```bash
# Load in developer mode and check console
```

**Sync Service**:
```bash
curl -X POST http://localhost:8000/sync \
  -H "Content-Type: application/json" \
  -d '{"url":"test","title":"test","html":"<h1>test</h1>","timestamp":123}'
```

**AI Server**:
```bash
# Place a markdown file in webpages/ and watch logs
cp test.md aiserver_module/webpages/
```

## Future Enhancements

- [ ] Browser extension for Firefox and Safari
- [ ] Support for more LLM providers
- [ ] PDF export of processed content
- [ ] Search functionality in dashboard
- [ ] Tags and categories for pages
- [ ] Browser history integration
- [ ] Mobile app for viewing results
- [ ] Real-time notifications
- [ ] Scheduled processing
- [ ] Multi-user support

## License

This is a personal customized project. Feel free to modify and adapt for your needs.

## Acknowledgments

- html2text for HTML to markdown conversion
- Watchdog for file system monitoring
- Flask for web framework
- OpenAI and Anthropic for LLM APIs
