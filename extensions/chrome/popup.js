/**
 * GAP Protocol Browser Extension - Popup Script
 */

class GAPPopup {
  constructor() {
    this.serviceUrl = 'http://localhost:8000';
    this.init();
  }

  async init() {
    await this.loadSettings();
    this.bindEvents();
    this.checkServiceStatus();
  }

  async loadSettings() {
    const settings = await chrome.storage.sync.get([
      'serviceUrl',
      'defaultPlatform',
      'lastThreadId'
    ]);

    this.serviceUrl = settings.serviceUrl || 'http://localhost:8000';
    document.getElementById('service-url').value = this.serviceUrl;

    if (settings.defaultPlatform) {
      document.getElementById('target-platform').value = settings.defaultPlatform;
    }

    if (settings.lastThreadId) {
      document.getElementById('thread-id').value = settings.lastThreadId;
    }
  }

  bindEvents() {
    // Action buttons
    document.getElementById('wrap-selection').addEventListener('click', () => {
      this.wrapSelection();
    });

    document.getElementById('transform-clipboard').addEventListener('click', () => {
      this.transformClipboard();
    });

    // Footer buttons
    document.getElementById('open-docs').addEventListener('click', () => {
      chrome.tabs.create({ url: 'http://localhost:8000/docs' });
    });

    document.getElementById('check-service').addEventListener('click', () => {
      this.checkServiceStatus();
    });

    document.getElementById('open-options').addEventListener('click', () => {
      if (chrome.runtime.openOptionsPage) {
        chrome.runtime.openOptionsPage();
      }
    });

    // Settings changes
    document.getElementById('service-url').addEventListener('change', (e) => {
      this.serviceUrl = e.target.value;
      chrome.storage.sync.set({ serviceUrl: this.serviceUrl });
    });

    document.getElementById('target-platform').addEventListener('change', (e) => {
      chrome.storage.sync.set({ defaultPlatform: e.target.value });
    });

    document.getElementById('thread-id').addEventListener('change', (e) => {
      chrome.storage.sync.set({ lastThreadId: e.target.value });
    });
  }

  async wrapSelection() {
    try {
      // Get the active tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

      // Execute script to get selection
      const [result] = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => window.getSelection().toString()
      });

      const selection = result.result;

      if (!selection) {
        this.showStatus('Please select some text on the page first', 'warning');
        return;
      }

      const platform = this.detectPlatform(tab.url);
      const threadId = document.getElementById('thread-id').value;

      // Send to background script
      const response = await chrome.runtime.sendMessage({
        action: 'wrapContent',
        data: {
          content: selection,
          platform: platform,
          chatId: `popup_${Date.now()}`,
          threadId: threadId || undefined
        }
      });

      if (response.error) {
        this.showStatus(response.error, 'error');
      } else {
        // Copy to clipboard
        await this.copyToClipboard(response);
        this.showStatus('Selection wrapped and copied!', 'success');
      }

    } catch (error) {
      console.error('Error wrapping selection:', error);
      this.showStatus('Error wrapping selection', 'error');
    }
  }

  async transformClipboard() {
    try {
      // Read from clipboard
      const clipboardText = await this.readFromClipboard();

      if (!clipboardText) {
        this.showStatus('Could not read clipboard', 'error');
        return;
      }

      if (!this.isGAPContent(clipboardText)) {
        this.showStatus('Clipboard does not contain GAP content', 'warning');
        return;
      }

      const targetPlatform = document.getElementById('target-platform').value;
      const platform = targetPlatform === 'auto' ? await this.getCurrentTabPlatform() : targetPlatform;

      // Send to background script
      const response = await chrome.runtime.sendMessage({
        action: 'transformContent',
        data: {
          gapMarkdown: clipboardText,
          targetPlatform: platform
        }
      });

      if (response.error) {
        this.showStatus(response.error, 'error');
      } else {
        // Copy transformed content
        await this.copyToClipboard(response);

        // Try to insert into page
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        chrome.tabs.sendMessage(tab.id, {
          action: 'insertText',
          text: response
        });

        this.showStatus('Content transformed and copied!', 'success');
      }

    } catch (error) {
      console.error('Error transforming clipboard:', error);
      this.showStatus('Error transforming content', 'error');
    }
  }

  async checkServiceStatus() {
    const statusEl = document.getElementById('service-status');

    try {
      const response = await chrome.runtime.sendMessage({
        action: 'checkService'
      });

      if (response.error) {
        statusEl.className = 'status-indicator offline';
        statusEl.title = 'Service offline';
        this.showStatus('GAP service is not running', 'warning');
      } else {
        statusEl.className = 'status-indicator online';
        statusEl.title = `Service online (v${response.version})`;
        this.showStatus('Service connected', 'success');
      }
    } catch (error) {
      statusEl.className = 'status-indicator offline';
      statusEl.title = 'Service offline';
      this.showStatus('Cannot connect to service', 'error');
    }
  }

  detectPlatform(url) {
    const hostname = new URL(url).hostname;

    if (hostname.includes('claude.ai')) return 'claude.ai';
    if (hostname.includes('chat.openai.com')) return 'chatgpt';
    if (hostname.includes('gemini.google.com')) return 'gemini';
    if (hostname.includes('copilot.microsoft.com')) return 'copilot';
    if (hostname.includes('perplexity.ai')) return 'perplexity';
    if (hostname.includes('poe.com')) return 'poe';

    return 'generic';
  }

  async getCurrentTabPlatform() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    return this.detectPlatform(tab.url);
  }

  isGAPContent(text) {
    return text.includes('[GAP:START]') && text.includes('[GAP:END]');
  }

  async copyToClipboard(text) {
    // Try using the Chrome API first
    try {
      await chrome.clipboard.writeText(text);
      return;
    } catch (err) {
      // Fallback to execCommand
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
    }
  }

  async readFromClipboard() {
    try {
      // Try Chrome API first
      return await chrome.clipboard.readText();
    } catch (err) {
      // Fallback to paste event
      return new Promise((resolve) => {
        const textarea = document.createElement('textarea');
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.focus();

        document.addEventListener('paste', function handler(e) {
          e.preventDefault();
          const text = e.clipboardData.getData('text');
          document.removeEventListener('paste', handler);
          document.body.removeChild(textarea);
          resolve(text);
        });

        document.execCommand('paste');

        // Timeout fallback
        setTimeout(() => {
          document.body.removeChild(textarea);
          resolve('');
        }, 100);
      });
    }
  }

  showStatus(message, type = 'info') {
    const statusEl = document.getElementById('status-message');
    statusEl.textContent = message;
    statusEl.className = `status-message ${type}`;
    statusEl.style.display = 'block';

    // Auto-hide after 3 seconds
    setTimeout(() => {
      statusEl.style.display = 'none';
    }, 3000);
  }
}

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new GAPPopup();
});
