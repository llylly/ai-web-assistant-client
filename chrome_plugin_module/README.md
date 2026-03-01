# Website Monitor & Sync Chrome Extension

A Chrome extension that monitors your browsing activity and syncs webpage content to a local server for LLM processing.

## Features

- **Automatic Monitoring**: Monitors your active tab at configurable intervals (default: 30 seconds)
- **Smart Deduplication**: Avoids capturing the same page multiple times within the interval
- **Content Extraction**: Extracts clean HTML and text content from web pages
- **History Management**: Stores up to 100 recent pages (configurable)
- **Local Sync**: Automatically syncs content to local server via HTTP POST

## Installation

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked"
4. Select the `chrome_plugin_module` directory
5. The extension icon should appear in your toolbar

## Configuration

Click the extension icon to open the popup UI:

- **Enable Monitoring**: Toggle to start/stop monitoring
- **Monitor Interval**: Set how often to check the active tab (10-300 seconds)
- **Max History Size**: Set how many pages to keep in history (10-1000)
- **Sync Server URL**: URL of the local sync service (default: `http://localhost:8000/sync`)

## Manual Actions

- **Save Config**: Save your configuration changes
- **Sync Now**: Manually trigger a sync of the current tab
- **Clear History**: Clear all stored history

## Icons

The extension requires icon files in the `icons/` directory:
- `icon16.png` (16x16 pixels)
- `icon48.png` (48x48 pixels)
- `icon128.png` (128x128 pixels)

You can create simple placeholder icons or use your own custom icons.

## Data Format

The extension sends data to the sync server in the following JSON format:

```json
{
  "id": "unique_id",
  "url": "https://example.com",
  "title": "Page Title",
  "html": "<html>...</html>",
  "text": "Page text content...",
  "timestamp": 1234567890000
}
```

## Privacy

- All data is stored locally in Chrome's storage
- Content is only sent to the configured local server
- No data is sent to external services
- You have full control over what is monitored

## Requirements

- Chrome/Chromium browser (Manifest V3 compatible)
- Local sync service running (see `webpage_sync_module`)
