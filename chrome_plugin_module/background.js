/**
 * Background Service Worker for Website Monitor & Sync
 * Handles periodic monitoring, storage, and communication with local sync service
 */

// Default configuration
const DEFAULT_CONFIG = {
  monitorInterval: 30, // seconds
  maxHistory: 100,
  syncServerUrl: 'http://localhost:8000/sync',
  enabled: true,
  captureScreenshot: false  // Capture visible tab screenshot and send as JPEG base64
};

// Initialize configuration on install
chrome.runtime.onInstalled.addListener(async () => {
  const config = await chrome.storage.local.get('config');
  if (!config.config) {
    await chrome.storage.local.set({ config: DEFAULT_CONFIG });
  }

  // Initialize history if not exists
  const history = await chrome.storage.local.get('history');
  if (!history.history) {
    await chrome.storage.local.set({ history: [] });
  }

  // Set up alarm for periodic monitoring
  chrome.alarms.create('monitorAlarm', { periodInMinutes: 0.5 }); // 30 seconds
});

// Listen to alarm for periodic monitoring
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === 'monitorAlarm') {
    await monitorCurrentTab();
  }
});

// Track last monitored URL to avoid duplicates
let lastMonitoredUrl = null;
let lastMonitoredTime = 0;

/**
 * Monitor the current active tab
 */
async function monitorCurrentTab() {
  try {
    const { config } = await chrome.storage.local.get('config');
    if (!config || !config.enabled) {
      return;
    }

    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.url) {
      return;
    }

    // Skip chrome:// and other internal URLs
    if (tab.url.startsWith('chrome://') ||
        tab.url.startsWith('chrome-extension://') ||
        tab.url.startsWith('about:')) {
      return;
    }

    // Skip if same URL was just monitored (within interval)
    const now = Date.now();
    const minInterval = (config.monitorInterval || 30) * 1000;
    if (tab.url === lastMonitoredUrl && (now - lastMonitoredTime) < minInterval) {
      return;
    }

    // Extract content from the page
    const result = await chrome.tabs.sendMessage(tab.id, { action: 'extractContent' })
      .catch(err => {
        console.log('Could not extract content:', err);
        return null;
      });

    if (!result || !result.html) {
      return;
    }

    // Capture screenshot of the visible tab if enabled
    // Returns a JPEG data URL: "data:image/jpeg;base64,..."
    let screenshot = null;
    if (config.captureScreenshot) {
      try {
        screenshot = await chrome.tabs.captureVisibleTab(null, { format: 'png' });
      } catch (err) {
        console.warn('Could not capture screenshot:', err);
      }
    }

    // Create entry
    const entry = {
      url: tab.url,
      title: tab.title || 'Untitled',
      html: result.html,
      text: result.text,
      screenshot: screenshot,  // null when disabled, data URL string when enabled
      timestamp: now,
      id: `${now}_${Math.random().toString(36).substr(2, 9)}`
    };

    // Update last monitored
    lastMonitoredUrl = tab.url;
    lastMonitoredTime = now;

    // Save to history
    await saveToHistory(entry, config.maxHistory || 100);

    // Sync to local server
    await syncToServer(entry, config.syncServerUrl);

    console.log('Monitored:', tab.url);

  } catch (error) {
    console.error('Error monitoring tab:', error);
  }
}

/**
 * Save a lightweight metadata-only record to history.
 *
 * The full payload (html, text, screenshot) is intentionally excluded:
 * those fields can be several MB each and would quickly exhaust the
 * chrome.storage.local 10 MB quota.  History is only used for the popup
 * stats display, so only the small identifying fields are needed.
 */
async function saveToHistory(entry, maxHistory) {
  const { history } = await chrome.storage.local.get('history');
  let historyList = history || [];

  // Store only the lightweight fields
  const record = {
    id:        entry.id,
    url:       entry.url,
    title:     entry.title,
    timestamp: entry.timestamp,
    hasScreenshot: entry.screenshot !== null  // record whether a screenshot was sent
  };

  historyList.unshift(record);

  // Limit history size
  if (historyList.length > maxHistory) {
    historyList = historyList.slice(0, maxHistory);
  }

  await chrome.storage.local.set({ history: historyList });
}

/**
 * Sync entry to local server
 */
async function syncToServer(entry, serverUrl) {
  try {
    const response = await fetch(serverUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: entry.url,
        title: entry.title,
        html: entry.html,
        text: entry.text,
        screenshot: entry.screenshot,  // PNG data URL, or null if disabled
        timestamp: entry.timestamp,
        id: entry.id
      })
    });

    if (!response.ok) {
      console.error('Sync failed:', response.statusText);
    } else {
      console.log('Synced to server:', entry.url);
    }
  } catch (error) {
    console.error('Error syncing to server:', error);
  }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getStats') {
    getStats().then(sendResponse);
    return true; // Will respond asynchronously
  } else if (request.action === 'clearHistory') {
    chrome.storage.local.set({ history: [] }).then(() => {
      sendResponse({ success: true });
    });
    return true;
  } else if (request.action === 'manualSync') {
    monitorCurrentTab().then(() => {
      sendResponse({ success: true });
    });
    return true;
  }
});

/**
 * Get statistics
 */
async function getStats() {
  const { history, config } = await chrome.storage.local.get(['history', 'config']);
  return {
    historyCount: (history || []).length,
    config: config || DEFAULT_CONFIG,
    lastMonitored: lastMonitoredUrl,
    lastMonitoredTime: lastMonitoredTime
  };
}
