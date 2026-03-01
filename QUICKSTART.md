# Quick Start Guide

Get your AI-powered web reading system up and running in minutes!

## Prerequisites

- Python 3.8+ installed
- Chrome browser
- SSH access between MacBook and Desktop server

## Step 1: Install Dependencies

On your **MacBook**:
```bash
cd webpage_sync_module
pip3 install -r requirements.txt
```

On your **Desktop Server** (4090):
```bash
cd aiserver_module
pip3 install -r requirements.txt
```

## Step 2: Configure SSH (MacBook → Desktop)

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519

# Copy to desktop server (update with your details)
ssh-copy-id -p 9911 linyi@192.168.1.66

# Test connection
ssh -p 9911 linyi@192.168.1.66
```

## Step 3: Configure Services

### Webpage Sync Module (MacBook)

```bash
cd webpage_sync_module
cp config.yaml.example config.yaml
nano config.yaml
```

Update with your settings:
```yaml
server:
  host: 192.168.1.66
  port: 9911
  username: linyi
  remote_path: /home/linyi/Documents/services/aiserver_module
```

### AI Server Module (Desktop)

```bash
cd aiserver_module
cp config.yaml.example config.yaml
nano config.yaml
```

Add your LLM API key:
```yaml
llm:
  provider: openai  # or anthropic, local
  model: gpt-4-turbo-preview
  api_key: sk-YOUR_API_KEY_HERE
  system_prompt: |
    You are a helpful assistant that analyzes web content.
```

## Step 4: Start Services

### Terminal 1 - Sync Service (MacBook)

```bash
cd webpage_sync_module
python3 sync_service.py
```

You should see:
```
INFO - Starting Webpage Sync Service
INFO - SSH sync initialized successfully
INFO - Running on http://0.0.0.0:8000
```

### Terminal 2 - AI Server (Desktop)

```bash
cd aiserver_module
python3 ai_server.py
```

You should see:
```
INFO - Starting AI Server Module
INFO - Initialized OpenAI client
INFO - Started watching directory
INFO - Running on http://0.0.0.0:5000
```

## Step 5: Install Chrome Extension

1. Open Chrome and navigate to: `chrome://extensions/`
2. Enable **Developer mode** (toggle in top right)
3. Click **Load unpacked**
4. Select the `chrome_plugin_module` directory
5. The extension icon (white "L" on black) should appear in your toolbar

## Step 6: Configure Chrome Extension

Click the extension icon and configure:

- **Enable Monitoring**: ✓ (toggle on)
- **Monitor Interval**: 30 seconds
- **Max History Size**: 100
- **Sync Server URL**: `http://localhost:8000/sync`

Click **Save Config**

## Step 7: Access Dashboard

Open your browser and go to:
```
http://localhost:5000
```

Or from another device:
```
http://YOUR_DESKTOP_IP:5000
```

## Step 8: Start Browsing!

That's it! Now browse any website and:

1. Chrome extension monitors your active tab every 30 seconds
2. Content is sent to MacBook sync service
3. Converted to markdown format
4. Synced to desktop server via SSH
5. Processed by LLM with your custom prompt
6. Results displayed in the dashboard

## Testing

### Test Sync Service

```bash
curl -X POST http://localhost:8000/sync \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test123",
    "url": "https://example.com",
    "title": "Test Page",
    "html": "<html><body><h1>Hello World</h1><p>This is a test.</p></body></html>",
    "timestamp": 1234567890000
  }'
```

### Check Status

Sync service:
```bash
curl http://localhost:8000/status
```

AI server:
```bash
curl http://localhost:5000/status
```

## Customization Examples

### Translation Mode

In `aiserver_module/config.yaml`:
```yaml
system_prompt: |
  Translate the following content to English while preserving
  the original structure and key information.
```

### Summarization Mode

```yaml
system_prompt: |
  Provide a concise summary of this webpage including:
  1. Main topic and purpose
  2. Key points (3-5 bullet points)
  3. Important takeaways
```

### Learning Mode

```yaml
system_prompt: |
  Explain this content in simple terms suitable for learning:
  1. Core concepts
  2. Examples
  3. Practical applications
  4. Related topics to explore
```

## Troubleshooting

### Extension not capturing pages
- Verify extension is enabled
- Check console: Right-click extension → Inspect popup
- Ensure sync service is running
- Try manual sync button

### SSH sync failing
```bash
# Test SSH connection
ssh -p 9911 linyi@192.168.1.66 "echo 'Connection successful'"

# Check SSH logs
tail -f /var/log/auth.log  # Linux
tail -f /var/log/system.log  # macOS
```

### LLM not processing
- Verify API key is correct
- Check API balance/quota
- Review server logs for errors
- Test with a simple markdown file manually

### Can't access dashboard
- Check firewall settings
- Verify port 5000 is not in use
- Try `http://0.0.0.0:5000` instead
- Check if process is running: `ps aux | grep ai_server`

## Performance Tips

1. **Monitor interval**: Start with 60 seconds, adjust based on needs
2. **Max history**: Reduce if storage is limited
3. **LLM model**: Use GPT-3.5 for speed, GPT-4 for quality
4. **Local LLM**: Use Ollama with your 4090 for free processing

## Support

Check individual module READMEs for detailed information:
- `chrome_plugin_module/README.md`
- `webpage_sync_module/README.md`
- `aiserver_module/README.md`

## File Locations

- Markdown files: `webpage_sync_module/data/markdown/`
- Processed files: `aiserver_module/processed/`
- HTML outputs: `aiserver_module/output/`
- Logs: Console output from each service

---

**Enjoy your AI-powered web reading experience! 🚀**
