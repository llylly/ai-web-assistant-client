/**
 * Popup UI Logic for Website Monitor & Sync
 */

// Load current configuration and stats on popup open
document.addEventListener('DOMContentLoaded', async () => {
  await loadStats();
  await loadConfig();
});

/**
 * Load statistics
 */
async function loadStats() {
  try {
    const stats = await chrome.runtime.sendMessage({ action: 'getStats' });

    // Update status
    const statusEl = document.getElementById('statusEnabled');
    if (stats.config.enabled) {
      statusEl.textContent = 'Active';
      statusEl.className = 'status-value enabled';
    } else {
      statusEl.textContent = 'Inactive';
      statusEl.className = 'status-value disabled';
    }

    // Update history count
    document.getElementById('historyCount').textContent = stats.historyCount;

    // Update last monitored
    const lastMonitoredEl = document.getElementById('lastMonitored');
    if (stats.lastMonitored && stats.lastMonitoredTime) {
      const timeAgo = getTimeAgo(stats.lastMonitoredTime);
      lastMonitoredEl.textContent = `${timeAgo} ago`;
      lastMonitoredEl.title = stats.lastMonitored;
    } else {
      lastMonitoredEl.textContent = 'None';
    }

  } catch (error) {
    console.error('Error loading stats:', error);
  }
}

/**
 * Load configuration
 */
async function loadConfig() {
  try {
    const { config } = await chrome.storage.local.get('config');

    if (config) {
      document.getElementById('enabledToggle').checked = config.enabled;
      document.getElementById('monitorInterval').value = config.monitorInterval;
      document.getElementById('maxHistory').value = config.maxHistory;
      document.getElementById('syncServerUrl').value = config.syncServerUrl;
    }

  } catch (error) {
    console.error('Error loading config:', error);
  }
}

/**
 * Save configuration
 */
document.getElementById('saveBtn').addEventListener('click', async () => {
  try {
    const config = {
      enabled: document.getElementById('enabledToggle').checked,
      monitorInterval: parseInt(document.getElementById('monitorInterval').value),
      maxHistory: parseInt(document.getElementById('maxHistory').value),
      syncServerUrl: document.getElementById('syncServerUrl').value
    };

    await chrome.storage.local.set({ config });

    // Update alarm interval if changed
    chrome.alarms.clear('monitorAlarm', () => {
      const intervalMinutes = config.monitorInterval / 60;
      chrome.alarms.create('monitorAlarm', {
        periodInMinutes: intervalMinutes
      });
    });

    showMessage('Configuration saved successfully!', 'success');
    await loadStats();

  } catch (error) {
    console.error('Error saving config:', error);
    showMessage('Error saving configuration', 'error');
  }
});

/**
 * Manual sync button
 */
document.getElementById('syncBtn').addEventListener('click', async () => {
  try {
    await chrome.runtime.sendMessage({ action: 'manualSync' });
    showMessage('Manual sync triggered!', 'success');
    setTimeout(loadStats, 500);
  } catch (error) {
    console.error('Error during manual sync:', error);
    showMessage('Error during manual sync', 'error');
  }
});

/**
 * Clear history button
 */
document.getElementById('clearBtn').addEventListener('click', async () => {
  if (confirm('Are you sure you want to clear all history?')) {
    try {
      await chrome.runtime.sendMessage({ action: 'clearHistory' });
      showMessage('History cleared!', 'success');
      await loadStats();
    } catch (error) {
      console.error('Error clearing history:', error);
      showMessage('Error clearing history', 'error');
    }
  }
});

/**
 * Show message to user
 */
function showMessage(text, type) {
  const messageEl = document.getElementById('message');
  messageEl.textContent = text;
  messageEl.className = `message ${type}`;

  setTimeout(() => {
    messageEl.className = 'message';
  }, 3000);
}

/**
 * Get time ago string
 */
function getTimeAgo(timestamp) {
  const seconds = Math.floor((Date.now() - timestamp) / 1000);

  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
  return `${Math.floor(seconds / 86400)}d`;
}
