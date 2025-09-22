/**
 * GAP Protocol Browser Extension - Background Service Worker
 */

const GAP_SERVICE_URL = 'http://localhost:8000';

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  console.log('GAP Protocol Extension installed');

  // Set default settings
  chrome.storage.sync.set({
    serviceUrl: GAP_SERVICE_URL,
    defaultPlatform: 'generic',
    autoDetectPlatform: true
  });
});

// Handle keyboard shortcuts
chrome.commands.onCommand.addListener(async (command) => {
  if (command === 'wrap-selection') {
    await handleWrapSelection();
  } else if (command === 'quick-transform') {
    await handleQuickTransform();
  }
});

// Handle messages from content script and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'wrapContent') {
    wrapWithGAP(request.data)
      .then(sendResponse)
      .catch(error => sendResponse({ error: error.message }));
    return true; // Will respond asynchronously
  }

  if (request.action === 'transformContent') {
    transformGAPContent(request.data)
      .then(sendResponse)
      .catch(error => sendResponse({ error: error.message }));
    return true;
  }

  if (request.action === 'checkService') {
    checkServiceHealth()
      .then(sendResponse)
      .catch(error => sendResponse({ error: error.message }));
    return true;
  }
});

// Core GAP operations
async function wrapWithGAP(data) {
  const { content, platform, chatId, threadId, role = 'assistant' } = data;

  const settings = await chrome.storage.sync.get(['serviceUrl']);
  const serviceUrl = settings.serviceUrl || GAP_SERVICE_URL;

  const response = await fetch(`${serviceUrl}/gap/wrap`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      content,
      platform: platform || 'generic',
      chat_id: chatId || `ext_${Date.now()}`,
      thread_id: threadId,
      role
    })
  });

  if (!response.ok) {
    throw new Error(`Service error: ${response.status}`);
  }

  const result = await response.json();
  return result.gap_markdown;
}

async function transformGAPContent(data) {
  const { gapMarkdown, targetPlatform, contextAdditions } = data;

  const settings = await chrome.storage.sync.get(['serviceUrl']);
  const serviceUrl = settings.serviceUrl || GAP_SERVICE_URL;

  const response = await fetch(`${serviceUrl}/gap/transform`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      gap_markdown: gapMarkdown,
      target_platform: targetPlatform,
      context_additions: contextAdditions
    })
  });

  if (!response.ok) {
    throw new Error(`Service error: ${response.status}`);
  }

  const result = await response.json();
  return result.transformed_content;
}

async function checkServiceHealth() {
  const settings = await chrome.storage.sync.get(['serviceUrl']);
  const serviceUrl = settings.serviceUrl || GAP_SERVICE_URL;

  const response = await fetch(`${serviceUrl}/health`, {
    method: 'GET'
  });

  if (!response.ok) {
    throw new Error('Service not available');
  }

  return await response.json();
}

// Handle wrap selection command
async function handleWrapSelection() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.tabs.sendMessage(
    tab.id,
    { action: 'getSelection' },
    async (response) => {
      if (response && response.selection) {
        const platform = detectPlatform(tab.url);
        const wrapped = await wrapWithGAP({
          content: response.selection,
          platform: platform,
          chatId: `cmd_${Date.now()}`
        });

        // Send back to content script to copy
        chrome.tabs.sendMessage(tab.id, {
          action: 'copyToClipboard',
          text: wrapped
        });
      }
    }
  );
}

// Handle quick transform command
async function handleQuickTransform() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const platform = detectPlatform(tab.url);

  chrome.tabs.sendMessage(
    tab.id,
    { action: 'getClipboard' },
    async (response) => {
      if (response && response.clipboard && isGAPContent(response.clipboard)) {
        const transformed = await transformGAPContent({
          gapMarkdown: response.clipboard,
          targetPlatform: platform
        });

        chrome.tabs.sendMessage(tab.id, {
          action: 'copyToClipboard',
          text: transformed
        });
      }
    }
  );
}

// Utility functions
function detectPlatform(url) {
  const hostname = new URL(url).hostname;

  if (hostname.includes('claude.ai')) return 'claude.ai';
  if (hostname.includes('chat.openai.com')) return 'chatgpt';
  if (hostname.includes('gemini.google.com')) return 'gemini';
  if (hostname.includes('copilot.microsoft.com')) return 'copilot';
  if (hostname.includes('perplexity.ai')) return 'perplexity';
  if (hostname.includes('poe.com')) return 'poe';

  return 'generic';
}

function isGAPContent(text) {
  return text.includes('[GAP:START]') && text.includes('[GAP:END]');
}
