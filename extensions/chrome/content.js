/**
 * GAP Protocol Browser Extension - Content Script
 * Injected into AI chat pages to interact with page content
 */

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getSelection') {
    const selection = window.getSelection().toString();
    sendResponse({ selection: selection });
  }

  if (request.action === 'getClipboard') {
    // Try to read from clipboard (may require user interaction)
    navigator.clipboard.readText()
      .then(text => sendResponse({ clipboard: text }))
      .catch(err => sendResponse({ error: 'Cannot read clipboard' }));
    return true; // Will respond asynchronously
  }

  if (request.action === 'copyToClipboard') {
    navigator.clipboard.writeText(request.text)
      .then(() => {
        showNotification('Copied to clipboard!', 'success');
        sendResponse({ success: true });
      })
      .catch(err => {
        showNotification('Failed to copy', 'error');
        sendResponse({ error: err.message });
      });
    return true;
  }

  if (request.action === 'insertText') {
    insertAtCursor(request.text);
    sendResponse({ success: true });
  }
});

// Insert text at current cursor position or in active textarea
function insertAtCursor(text) {
  // Try to find the active element
  let targetElement = document.activeElement;

  // If no active element, try to find the main chat input
  if (!targetElement || !isEditableElement(targetElement)) {
    targetElement = findChatInput();
  }

  if (targetElement && isEditableElement(targetElement)) {
    // For input/textarea elements
    if (targetElement.tagName === 'TEXTAREA' || targetElement.tagName === 'INPUT') {
      const start = targetElement.selectionStart;
      const end = targetElement.selectionEnd;
      const currentValue = targetElement.value;

      targetElement.value = currentValue.substring(0, start) + text + currentValue.substring(end);
      targetElement.selectionStart = targetElement.selectionEnd = start + text.length;

      // Trigger input event for React/Vue/etc
      targetElement.dispatchEvent(new Event('input', { bubbles: true }));
    }
    // For contenteditable elements
    else if (targetElement.contentEditable === 'true') {
      document.execCommand('insertText', false, text);
    }
  } else {
    showNotification('Please click in a text input area first', 'warning');
  }
}

// Check if element is editable
function isEditableElement(element) {
  return (
    element.tagName === 'TEXTAREA' ||
    element.tagName === 'INPUT' ||
    element.contentEditable === 'true'
  );
}

// Find the main chat input based on common patterns
function findChatInput() {
  // Claude.ai
  let input = document.querySelector('div[contenteditable="true"]');
  if (input) return input;

  // ChatGPT
  input = document.querySelector('textarea[data-id]');
  if (input) return input;

  // Gemini
  input = document.querySelector('textarea[aria-label*="chat"]');
  if (input) return input;

  // Generic textarea search
  input = document.querySelector('textarea');
  if (input) return input;

  return null;
}

// Show notification overlay
function showNotification(message, type = 'info') {
  // Remove any existing notifications
  const existing = document.getElementById('gap-notification');
  if (existing) existing.remove();

  const notification = document.createElement('div');
  notification.id = 'gap-notification';
  notification.className = `gap-notification gap-notification-${type}`;
  notification.textContent = message;

  document.body.appendChild(notification);

  // Auto-remove after 3 seconds
  setTimeout(() => {
    notification.classList.add('gap-notification-fade');
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Add floating GAP button for quick access
function addGAPButton() {
  if (document.getElementById('gap-float-button')) return;

  const button = document.createElement('div');
  button.id = 'gap-float-button';
  button.className = 'gap-float-button';
  button.innerHTML = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <circle cx="12" cy="12" r="10" stroke-width="2"/>
      <path d="M12 6v6l4 2" stroke-width="2"/>
    </svg>
  `;
  button.title = 'GAP Protocol Actions';

  button.addEventListener('click', () => {
    showGAPMenu();
  });

  document.body.appendChild(button);
}

// Show GAP action menu
function showGAPMenu() {
  const existing = document.getElementById('gap-menu');
  if (existing) {
    existing.remove();
    return;
  }

  const menu = document.createElement('div');
  menu.id = 'gap-menu';
  menu.className = 'gap-menu';
  menu.innerHTML = `
    <div class="gap-menu-header">GAP Protocol</div>
    <button id="gap-wrap-selection">Wrap Selection</button>
    <button id="gap-transform-clipboard">Transform from Clipboard</button>
    <button id="gap-detect-entities">Detect Entities</button>
    <div class="gap-menu-divider"></div>
    <button id="gap-close-menu">Close</button>
  `;

  document.body.appendChild(menu);

  // Add event listeners
  document.getElementById('gap-wrap-selection').addEventListener('click', () => {
    wrapCurrentSelection();
    menu.remove();
  });

  document.getElementById('gap-transform-clipboard').addEventListener('click', () => {
    transformFromClipboard();
    menu.remove();
  });

  document.getElementById('gap-detect-entities').addEventListener('click', () => {
    detectEntitiesInSelection();
    menu.remove();
  });

  document.getElementById('gap-close-menu').addEventListener('click', () => {
    menu.remove();
  });
}

// Wrap current selection
async function wrapCurrentSelection() {
  const selection = window.getSelection().toString();
  if (!selection) {
    showNotification('Please select some text first', 'warning');
    return;
  }

  const platform = detectCurrentPlatform();

  chrome.runtime.sendMessage({
    action: 'wrapContent',
    data: {
      content: selection,
      platform: platform,
      chatId: `content_${Date.now()}`
    }
  }, response => {
    if (response.error) {
      showNotification(`Error: ${response.error}`, 'error');
    } else {
      navigator.clipboard.writeText(response);
      showNotification('Selection wrapped and copied!', 'success');
    }
  });
}

// Transform content from clipboard
async function transformFromClipboard() {
  const text = await navigator.clipboard.readText();

  if (!text.includes('[GAP:START]')) {
    showNotification('No GAP content in clipboard', 'warning');
    return;
  }

  const platform = detectCurrentPlatform();

  chrome.runtime.sendMessage({
    action: 'transformContent',
    data: {
      gapMarkdown: text,
      targetPlatform: platform
    }
  }, response => {
    if (response.error) {
      showNotification(`Error: ${response.error}`, 'error');
    } else {
      insertAtCursor(response);
      showNotification('Content transformed and inserted!', 'success');
    }
  });
}

// Detect entities in selection
async function detectEntitiesInSelection() {
  const selection = window.getSelection().toString();
  if (!selection) {
    showNotification('Please select some text first', 'warning');
    return;
  }

  chrome.runtime.sendMessage({
    action: 'wrapContent',
    data: {
      content: selection,
      platform: 'analysis',
      chatId: `detect_${Date.now()}`
    }
  }, response => {
    if (response.error) {
      showNotification(`Error: ${response.error}`, 'error');
    } else {
      // Extract entities from response
      const entityMatch = response.match(/Entities: ([^\n]+)/);
      if (entityMatch && entityMatch[1] !== 'None') {
        showNotification(`Found entities: ${entityMatch[1]}`, 'info');
      } else {
        showNotification('No ambiguous entities detected', 'info');
      }
    }
  });
}

// Detect current platform
function detectCurrentPlatform() {
  const hostname = window.location.hostname;

  if (hostname.includes('claude.ai')) return 'claude.ai';
  if (hostname.includes('chat.openai.com')) return 'chatgpt';
  if (hostname.includes('gemini.google.com')) return 'gemini';
  if (hostname.includes('copilot.microsoft.com')) return 'copilot';
  if (hostname.includes('perplexity.ai')) return 'perplexity';
  if (hostname.includes('poe.com')) return 'poe';

  return 'generic';
}

// Initialize when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', addGAPButton);
} else {
  addGAPButton();
}
