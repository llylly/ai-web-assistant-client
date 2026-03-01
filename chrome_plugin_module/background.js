/**
 * Background Service Worker for Website Monitor & Sync
 * Handles periodic monitoring, storage, and communication with local sync service
 */

// Default configuration
const DEFAULT_CONFIG = {
  monitorInterval: 30, // seconds
  maxHistory: 100,
  syncServerUrl: 'http://localhost:8000/sync',
  enabled: true
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

    // Create entry
    const entry = {
      url: tab.url,
      title: tab.title || 'Untitled',
      html: result.html,
      text: result.text,
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
 * Save entry to history with max limit
 */
async function saveToHistory(entry, maxHistory) {
  const { history } = await chrome.storage.local.get('history');
  let historyList = history || [];

  // Add new entry
  historyList.unshift(entry);

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
