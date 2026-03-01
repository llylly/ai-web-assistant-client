/**
 * Content Script for Website Monitor & Sync
 * Runs in the context of web pages to extract content
 */

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractContent') {
    try {
      const content = extractPageContent();
      sendResponse(content);
    } catch (error) {
      console.error('Error extracting content:', error);
      sendResponse({ error: error.message });
    }
  }
  return true; // Will respond asynchronously
});

/**
 * Extract content from the current page
 */
function extractPageContent() {
  // Get clean HTML (remove scripts, styles, etc.)
  const cleanedHtml = getCleanedHTML();

  // Get plain text content
  const text = document.body.innerText || '';

  return {
    html: cleanedHtml,
    text: text.substring(0, 10000), // Limit text size
    url: window.location.href,
    title: document.title
  };
}

/**
 * Get cleaned HTML without scripts, styles, and comments
 */
function getCleanedHTML() {
  // Clone the document to avoid modifying the actual page
  const clone = document.documentElement.cloneNode(true);

  // Remove unwanted elements
  const unwantedSelectors = [
    'script',
    'style',
    'noscript',
    'iframe',
    'svg',
    'canvas',
    'video',
    'audio',
    'object',
    'embed',
    'link[rel="stylesheet"]',
    '.ad',
    '.ads',
    '.advertisement',
    '[class*="cookie"]',
    '[class*="popup"]',
    '[class*="modal"]',
    'nav',
    'header',
    'footer',
    '.sidebar',
    '.menu'
  ];

  unwantedSelectors.forEach(selector => {
    const elements = clone.querySelectorAll(selector);
    elements.forEach(el => el.remove());
  });

  // Remove inline styles and event handlers
  const allElements = clone.querySelectorAll('*');
  allElements.forEach(el => {
    el.removeAttribute('style');
    el.removeAttribute('class');
    el.removeAttribute('id');

    // Remove event handlers
    Array.from(el.attributes).forEach(attr => {
      if (attr.name.startsWith('on')) {
        el.removeAttribute(attr.name);
      }
    });
  });

  // Get HTML
  let html = clone.outerHTML;

  // Limit size (max 1MB)
  if (html.length > 1000000) {
    html = html.substring(0, 1000000) + '... [content truncated]';
  }

  return html;
}
