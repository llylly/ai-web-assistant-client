# AI Server Module

Desktop server that monitors markdown files, processes them with LLM, and displays results in a beautiful web interface.

## Features

- **File Monitoring**: Automatically detects new markdown files via watchdog
- **Multi-LLM Support**: OpenAI, Anthropic Claude, or local models (Ollama, LM Studio)
- **Configurable Prompts**: Customize system prompts for different use cases
- **Beautiful Web UI**: Modern dashboard to view and manage processed content
- **Side-by-Side View**: Compare original content with AI analysis
- **Real-time Processing**: Automatically processes new files as they arrive

## Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Copy and configure settings:

```bash
cp config.yaml.example config.yaml
nano config.yaml
```

3. Add your API key:
   - For OpenAI: Get key from https://platform.openai.com/api-keys
   - For Anthropic: Get key from https://console.anthropic.com/
   - For local models: No API key needed

## Configuration

Edit `config.yaml`:

### LLM Provider Options

**OpenAI:**
```yaml
llm:
  provider: openai
  model: gpt-4-turbo-preview
  api_key: sk-...
  system_prompt: "Your custom prompt here"
```

**Anthropic Claude:**
```yaml
llm:
  provider: anthropic
  model: claude-3-opus-20240229
  api_key: sk-ant-...
  system_prompt: "Your custom prompt here"
```

**Local Models (Ollama, LM Studio):**
```yaml
llm:
  provider: local
  model: llama2
  base_url: http://localhost:11434/v1
  system_prompt: "Your custom prompt here"
```

### System Prompt Examples

**Translation:**
```yaml
system_prompt: |
  You are a professional translator. Translate the following web content
  to English, maintaining the structure and key information.
```

**Summarization:**
```yaml
system_prompt: |
  You are a content summarizer. Create a concise summary of the webpage,
  highlighting key points, main arguments, and important details.
```

**Problem Solving:**
```yaml
system_prompt: |
  You are a problem-solving assistant. Analyze the content for:
  1. Problems or challenges mentioned
  2. Proposed solutions
  3. Your recommendations
```

**Research Assistant:**
```yaml
system_prompt: |
  You are a research assistant. Extract and organize:
  1. Main concepts and definitions
  2. Key findings or claims
  3. References or sources mentioned
  4. Questions for further investigation
```

## Usage

Start the server:

```bash
python ai_server.py
```

The server will:
- Start on `http://localhost:5000` (or configured port)
- Watch the `webpages/` directory for new `.md` files
- Automatically process new files with LLM
- Display results in the web interface

### Access the Dashboard

Open your browser and navigate to:
```
http://localhost:5000
```

Or from another machine:
```
http://YOUR_SERVER_IP:5000
```

## Directory Structure

```
aiserver_module/
├── ai_server.py          # Main server application
├── llm_processor.py      # LLM integration module
├── file_watcher.py       # File monitoring module
├── config.yaml           # Configuration (create from .example)
├── config.yaml.example   # Configuration template
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── templates/
│   └── dashboard.html   # Web dashboard template
├── webpages/            # Watch directory (created automatically)
├── processed/           # Processed markdown files (moved here)
└── output/              # HTML output files
```

## API Endpoints

### GET /
Main dashboard interface

### GET /view/<filename>
View processed file with AI analysis

### GET /config
Get current configuration

### POST /config
Update configuration
```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4-turbo-preview",
    "api_key": "sk-...",
    "system_prompt": "..."
  }
}
```

### GET /status
Get server status and statistics

### POST /process/<filename>
Manually trigger processing of a file

### GET /files
List all processed files

## Using with Local LLMs

### Ollama Setup

1. Install Ollama: https://ollama.ai/
2. Pull a model:
```bash
ollama pull llama2
```

3. Configure:
```yaml
llm:
  provider: local
  model: llama2
  base_url: http://localhost:11434/v1
```

### LM Studio Setup

1. Download LM Studio: https://lmstudio.ai/
2. Load a model
3. Start the server (default: http://localhost:1234/v1)
4. Configure:
```yaml
llm:
  provider: local
  model: model-name
  base_url: http://localhost:1234/v1
```

## GPU Acceleration

If you have a 4090 GPU, ensure you're using GPU-accelerated libraries:

**For local models (Ollama):**
- Ollama automatically uses GPU if available
- Check with `nvidia-smi`

**For API-based models:**
- APIs handle GPU processing on their end
- Your GPU won't be used for API calls

## Performance Tips

1. **Content Truncation**: Long pages are automatically truncated to 100k characters
2. **Token Limits**: Adjust `max_tokens` in config for longer/shorter responses
3. **Temperature**: Lower (0.3) for factual, higher (0.8) for creative responses
4. **Batch Processing**: Process multiple files at once for efficiency

## Troubleshooting

### Files not processing
- Check that files are in `webpages/` directory
- Verify `auto_process` is enabled in config
- Check server logs for errors

### LLM errors
- Verify API key is correct
- Check API quota/billing
- Test with smaller content first
- For local models, ensure server is running

### Cannot access dashboard
- Verify server is running
- Check firewall settings
- Try `0.0.0.0` instead of `localhost` in config
- Check port is not in use

### Slow processing
- Use faster models (GPT-3.5 vs GPT-4)
- Reduce `max_tokens`
- For local models, ensure GPU is being used

## Security Notes

- Keep API keys secure (never commit to git)
- Use environment variables for sensitive data
- Restrict network access if needed
- Consider using HTTPS for production

## Example Workflows

### Translation Workflow
1. Set system prompt to translation task
2. Browse foreign language websites
3. View translated content on dashboard

### Research Workflow
1. Set system prompt to extract key findings
2. Browse academic articles or documentation
3. Review AI-organized summaries

### Learning Workflow
1. Set system prompt to explain concepts
2. Browse technical documentation
3. Get simplified explanations

## Logs

Monitor logs for:
- File processing events
- LLM API calls and responses
- Errors and warnings
- Performance metrics

## Upgrading

To upgrade dependencies:
```bash
pip install --upgrade -r requirements.txt
```

## Support

For issues or questions:
- Check logs for error messages
- Verify configuration is correct
- Test with mock processor first
- Ensure all dependencies are installed
