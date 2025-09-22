# Let's create the browser extension manifest and basic files for Chrome/Firefox
browser_extension_manifest = '''
{
  "manifest_version": 3,
  "name": "GAP Protocol Assistant",
  "version": "0.1.0",
  "description": "Preserve context when sharing content between AI chats using GAP Protocol",
  
  "permissions": [
    "clipboardWrite",
    "clipboardRead",
    "activeTab",
    "storage"
  ],
  
  "content_scripts": [{
    "matches": ["*://*/*"],
    "js": ["content.js"],
    "css": ["styles.css"]
  }],
  
  "background": {
    "service_worker": "background.js"
  },
  
  "action": {
    "default_popup": "popup.html",
    "default_title": "GAP Protocol"
  },
  
  "icons": {
    "16": "icon16.png",
    "48": "icon48.png",
    "128": "icon128.png"
  }
}
'''

extension_content_js = '''
// GAP Protocol Browser Extension - Content Script

class GAPExtension {
    constructor() {
        this.gapServiceUrl = 'http://localhost:8000';
        this.init();
    }
    
    init() {
        this.addGAPButton();
        this.listenForCopyEvents();
    }
    
    addGAPButton() {
        // Add a floating GAP button to the page
        const gapButton = document.createElement('div');
        gapButton.id = 'gap-assistant-button';
        gapButton.innerHTML = '🔗 GAP';
        gapButton.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            font-size: 12px;
        `;
        
        gapButton.addEventListener('click', () => this.handleGAPClick());
        document.body.appendChild(gapButton);
    }
    
    async handleGAPClick() {
        const selection = window.getSelection().toString().trim();
        
        if (!selection) {
            this.showToast('Please select some text first', 'warning');
            return;
        }
        
        try {
            const gapContent = await this.wrapWithGAP(selection);
            await this.copyToClipboard(gapContent);
            this.showToast('Content wrapped with GAP and copied to clipboard!', 'success');
        } catch (error) {
            console.error('GAP Error:', error);
            this.showToast('Error wrapping content with GAP', 'error');
        }
    }
    
    async wrapWithGAP(content) {
        const platform = window.location.hostname;
        const chatId = `browser_${Date.now()}`;
        const threadId = await this.promptForThreadId();
        
        const requestData = {
            content: content,
            platform: platform,
            chat_id: chatId,
            thread_id: threadId,
            role: 'assistant'
        };
        
        try {
            const response = await fetch(`${this.gapServiceUrl}/gap/wrap`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            return result.gap_markdown;
        } catch (error) {
            // Fallback to simple markdown format if service is unavailable
            return this.createSimpleGAPMarkdown(content, platform, threadId);
        }
    }
    
    createSimpleGAPMarkdown(content, platform, threadId) {
        const timestamp = new Date().toISOString();
        return `[GAP:START]
From: ${platform} | Thread: ${threadId}
Context: Selected text from ${timestamp}
Entities: [AUTO-DETECTED]
[GAP:CONTENT]
${content}
[GAP:END]`;
    }
    
    async promptForThreadId() {
        return new Promise((resolve) => {
            const modal = this.createModal();
            const input = modal.querySelector('#thread-id-input');
            const submitBtn = modal.querySelector('#submit-thread-id');
            const cancelBtn = modal.querySelector('#cancel-thread-id');
            
            submitBtn.addEventListener('click', () => {
                const threadId = input.value.trim() || 'untitled';
                document.body.removeChild(modal);
                resolve(threadId);
            });
            
            cancelBtn.addEventListener('click', () => {
                document.body.removeChild(modal);
                resolve('untitled');
            });
            
            document.body.appendChild(modal);
            input.focus();
        });
    }
    
    createModal() {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 10001;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        modal.innerHTML = `
            <div style="background: white; padding: 20px; border-radius: 8px; max-width: 400px;">
                <h3 style="margin: 0 0 10px 0;">GAP Protocol</h3>
                <label for="thread-id-input">Thread ID (optional):</label>
                <input type="text" id="thread-id-input" placeholder="Enter thread ID" 
                       style="width: 100%; margin: 10px 0; padding: 8px; border: 1px solid #ccc; border-radius: 4px;">
                <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 15px;">
                    <button id="cancel-thread-id" style="padding: 8px 16px; border: 1px solid #ccc; background: white; border-radius: 4px; cursor: pointer;">Cancel</button>
                    <button id="submit-thread-id" style="padding: 8px 16px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Continue</button>
                </div>
            </div>
        `;
        
        return modal;
    }
    
    async copyToClipboard(text) {
        if (navigator.clipboard) {
            await navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
            color: white;
            border-radius: 4px;
            z-index: 10002;
            max-width: 300px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 3000);
    }
    
    listenForCopyEvents() {
        document.addEventListener('copy', (event) => {
            // Could enhance this to automatically wrap copied content
            // For now, just log that a copy occurred
            console.log('Copy event detected - GAP could auto-wrap this');
        });
    }
}

// Initialize the GAP extension when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new GAPExtension();
    });
} else {
    new GAPExtension();
}
'''

extension_popup_html = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            width: 300px;
            padding: 15px;
            font-family: Arial, sans-serif;
            margin: 0;
        }
        h2 {
            margin: 0 0 15px 0;
            font-size: 16px;
            color: #333;
        }
        .section {
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }
        .section:last-child {
            border-bottom: none;
        }
        button {
            width: 100%;
            padding: 8px;
            margin: 5px 0;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
        }
        .primary {
            background: #4CAF50;
            color: white;
        }
        .secondary {
            background: #f5f5f5;
            color: #333;
            border: 1px solid #ddd;
        }
        input, select {
            width: 100%;
            padding: 6px;
            margin: 3px 0;
            border: 1px solid #ccc;
            border-radius: 3px;
            box-sizing: border-box;
        }
        label {
            display: block;
            font-size: 12px;
            color: #666;
            margin-top: 8px;
        }
        .status {
            font-size: 12px;
            padding: 5px;
            border-radius: 3px;
            margin: 5px 0;
        }
        .status.success {
            background: #e8f5e8;
            color: #2e7d2e;
        }
        .status.error {
            background: #ffeaea;
            color: #d8000c;
        }
    </style>
</head>
<body>
    <h2>🔗 GAP Protocol Assistant</h2>
    
    <div class="section">
        <button id="wrap-selection" class="primary">Wrap Selected Text</button>
        <button id="paste-and-transform" class="secondary">Paste & Transform GAP</button>
    </div>
    
    <div class="section">
        <label for="target-platform">Target Platform:</label>
        <select id="target-platform">
            <option value="claude.ai">Claude</option>
            <option value="openai.com">ChatGPT</option>
            <option value="gemini.google.com">Gemini</option>
            <option value="copilot.microsoft.com">Copilot</option>
            <option value="other">Other</option>
        </select>
        
        <label for="thread-id">Thread ID:</label>
        <input type="text" id="thread-id" placeholder="Optional thread identifier">
    </div>
    
    <div class="section">
        <button id="check-service" class="secondary">Check GAP Service</button>
        <button id="open-docs" class="secondary">Open Documentation</button>
    </div>
    
    <div id="status-message"></div>
    
    <script src="popup.js"></script>
</body>
</html>
'''

extension_popup_js = '''
// GAP Protocol Browser Extension - Popup Script

class GAPPopup {
    constructor() {
        this.gapServiceUrl = 'http://localhost:8000';
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.checkServiceStatus();
    }
    
    bindEvents() {
        document.getElementById('wrap-selection').addEventListener('click', () => {
            this.wrapSelection();
        });
        
        document.getElementById('paste-and-transform').addEventListener('click', () => {
            this.pasteAndTransform();
        });
        
        document.getElementById('check-service').addEventListener('click', () => {
            this.checkServiceStatus();
        });
        
        document.getElementById('open-docs').addEventListener('click', () => {
            chrome.tabs.create({ url: 'https://github.com/your-repo/gap-protocol' });
        });
    }
    
    async wrapSelection() {
        try {
            // Get active tab and execute content script
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            const result = await chrome.tabs.executeScript(tab.id, {
                code: 'window.getSelection().toString()'
            });
            
            const selection = result[0];
            if (!selection) {
                this.showStatus('Please select some text on the page first', 'error');
                return;
            }
            
            const threadId = document.getElementById('thread-id').value.trim();
            const gapContent = await this.wrapWithGAP(selection, tab.url, threadId);
            
            await this.copyToClipboard(gapContent);
            this.showStatus('Content wrapped with GAP and copied to clipboard!', 'success');
            
        } catch (error) {
            console.error('Error wrapping selection:', error);
            this.showStatus('Error wrapping content', 'error');
        }
    }
    
    async pasteAndTransform() {
        try {
            const clipboardText = await navigator.clipboard.readText();
            
            if (!this.isGAPContent(clipboardText)) {
                this.showStatus('Clipboard does not contain GAP content', 'error');
                return;
            }
            
            const targetPlatform = document.getElementById('target-platform').value;
            const transformed = await this.transformGAPContent(clipboardText, targetPlatform);
            
            await this.copyToClipboard(transformed);
            this.showStatus('Content transformed and copied to clipboard!', 'success');
            
        } catch (error) {
            console.error('Error transforming content:', error);
            this.showStatus('Error transforming content', 'error');
        }
    }
    
    async wrapWithGAP(content, url, threadId) {
        const platform = new URL(url).hostname;
        const chatId = `ext_${Date.now()}`;
        
        const requestData = {
            content: content,
            platform: platform,
            chat_id: chatId,
            thread_id: threadId || 'untitled',
            role: 'assistant'
        };
        
        try {
            const response = await fetch(`${this.gapServiceUrl}/gap/wrap`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const result = await response.json();
            return result.gap_markdown;
            
        } catch (error) {
            // Fallback to simple format
            return this.createSimpleGAPMarkdown(content, platform, threadId);
        }
    }
    
    createSimpleGAPMarkdown(content, platform, threadId) {
        const timestamp = new Date().toISOString();
        return `[GAP:START]
From: ${platform} | Thread: ${threadId || 'untitled'}
Context: Browser selection from ${timestamp}
Entities: [AUTO-DETECTED]
[GAP:CONTENT]
${content}
[GAP:END]`;
    }
    
    async transformGAPContent(gapContent, targetPlatform) {
        try {
            const response = await fetch(`${this.gapServiceUrl}/gap/transform`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    gap_markdown: gapContent,
                    target_platform: targetPlatform
                })
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const result = await response.json();
            return result.transformed_content;
            
        } catch (error) {
            // Fallback: just extract content from GAP markdown
            const contentMatch = gapContent.match(/\\[GAP:CONTENT\\](.*?)\\[GAP:END\\]/s);
            return contentMatch ? contentMatch[1].trim() : gapContent;
        }
    }
    
    isGAPContent(text) {
        return text.includes('[GAP:START]') && text.includes('[GAP:CONTENT]') && text.includes('[GAP:END]');
    }
    
    async copyToClipboard(text) {
        await navigator.clipboard.writeText(text);
    }
    
    async checkServiceStatus() {
        try {
            const response = await fetch(`${this.gapServiceUrl}/health`);
            if (response.ok) {
                this.showStatus('GAP service is running ✓', 'success');
            } else {
                this.showStatus('GAP service error', 'error');
            }
        } catch (error) {
            this.showStatus('GAP service not found. Start with: python gap_fastapi_service.py', 'error');
        }
    }
    
    showStatus(message, type) {
        const statusDiv = document.getElementById('status-message');
        statusDiv.textContent = message;
        statusDiv.className = `status ${type}`;
        
        setTimeout(() => {
            statusDiv.textContent = '';
            statusDiv.className = '';
        }, 3000);
    }
}

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new GAPPopup();
});
'''

extension_background_js = '''
// GAP Protocol Browser Extension - Background Script

chrome.runtime.onInstalled.addListener(() => {
    console.log('GAP Protocol Extension installed');
    
    // Create context menu item
    chrome.contextMenus.create({
        id: 'gap-wrap-selection',
        title: 'Wrap with GAP Protocol',
        contexts: ['selection']
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'gap-wrap-selection') {
        // Execute GAP wrapping on the selected text
        chrome.tabs.executeScript(tab.id, {
            code: `
                const selection = window.getSelection().toString();
                if (selection) {
                    // This would trigger the GAP wrapping process
                    console.log('GAP wrapping:', selection);
                }
            `
        });
    }
});

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'wrapWithGAP') {
        // Handle GAP wrapping request
        sendResponse({ success: true });
    }
});
'''

# Create extension files
extension_files = {
    'manifest.json': browser_extension_manifest.strip(),
    'content.js': extension_content_js.strip(),
    'popup.html': extension_popup_html.strip(),
    'popup.js': extension_popup_js.strip(),
    'background.js': extension_background_js.strip()
}

print("✅ Browser extension files created:")
for filename, content in extension_files.items():
    with open(f"extension_{filename.replace('.', '_')}.txt", "w") as f:
        f.write(content)
    print(f"   - extension_{filename.replace('.', '_')}.txt")

print(f"\n📦 To create the browser extension:")
print(f"1. Create a new folder called 'gap-extension'")  
print(f"2. Copy the content from each extension_*.txt file into the corresponding file:")
for filename in extension_files.keys():
    print(f"   - extension_{filename.replace('.', '_')}.txt → {filename}")
print(f"3. Load the extension in Chrome/Edge (Developer mode)")
print(f"4. Or use web-ext for Firefox development")

# Create a simple MCP server template
mcp_server_code = '''
#!/usr/bin/env python3
"""
GAP Protocol MCP Server
Model Context Protocol server implementation for GAP
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

try:
    from mcp import ClientSession, StdioServerSession
    from mcp.server.models import InitializeParams
    from mcp.server.server import NotificationOptions, Server
    from mcp.server.fastapi import create_server_app
except ImportError:
    print("MCP library not available. Install with: pip install model-context-protocol")
    exit(1)

# Import our GAP protocol
from gap_protocol import GAPProtocol

class GAPMCPServer:
    def __init__(self):
        self.server = Server("gap-protocol")
        self.gap = GAPProtocol()
        self.context_store = {}
        
    async def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Dict[str, Any]]:
            """List available GAP resources"""
            return [
                {
                    "uri": "gap://context-store",
                    "name": "GAP Context Store",
                    "description": "Stored context information across chats",
                    "mimeType": "application/json"
                }
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read GAP resource content"""
            if uri == "gap://context-store":
                return json.dumps(self.context_store, indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.server.list_tools()
        async def list_tools() -> List[Dict[str, Any]]:
            """List available GAP tools"""
            return [
                {
                    "name": "gap_wrap_message",
                    "description": "Wrap content with GAP metadata for context preservation",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Content to wrap"},
                            "platform": {"type": "string", "description": "Source platform"},
                            "chat_id": {"type": "string", "description": "Chat identifier"},
                            "thread_id": {"type": "string", "description": "Thread identifier", "default": None},
                            "entities": {"type": "object", "description": "Entity definitions", "default": {}}
                        },
                        "required": ["content", "platform", "chat_id"]
                    }
                },
                {
                    "name": "gap_transform_message", 
                    "description": "Transform GAP content for target platform",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "gap_markdown": {"type": "string", "description": "GAP markdown content"},
                            "target_platform": {"type": "string", "description": "Target platform"},
                            "context_additions": {"type": "object", "description": "Additional context", "default": {}}
                        },
                        "required": ["gap_markdown", "target_platform"]
                    }
                },
                {
                    "name": "gap_link_conversations",
                    "description": "Link multiple conversations in context graph",
                    "inputSchema": {
                        "type": "object", 
                        "properties": {
                            "chat_ids": {"type": "array", "items": {"type": "string"}},
                            "relationship": {"type": "string", "default": "related"}
                        },
                        "required": ["chat_ids"]
                    }
                }
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Execute GAP tools"""
            
            if name == "gap_wrap_message":
                try:
                    wrapped = self.gap.wrap_message(**arguments)
                    markdown = self.gap.to_markdown(wrapped)
                    
                    # Store in context
                    thread_id = arguments.get('thread_id', 'default')
                    if thread_id not in self.context_store:
                        self.context_store[thread_id] = []
                    
                    self.context_store[thread_id].append({
                        'wrapped_message': wrapped.dict(),
                        'markdown': markdown,
                        'timestamp': wrapped.message.source.timestamp
                    })
                    
                    return [{
                        "type": "text",
                        "text": f"Message wrapped with GAP:\\n\\n{markdown}"
                    }]
                    
                except Exception as e:
                    return [{
                        "type": "text", 
                        "text": f"Error wrapping message: {str(e)}"
                    }]
            
            elif name == "gap_transform_message":
                try:
                    parsed = self.gap.from_markdown(arguments['gap_markdown'])
                    if not parsed:
                        raise ValueError("Invalid GAP markdown format")
                    
                    transformed = self.gap.transform_for_platform(
                        parsed,
                        arguments['target_platform'],
                        arguments.get('context_additions')
                    )
                    
                    return [{
                        "type": "text",
                        "text": f"Transformed content:\\n\\n{transformed}"
                    }]
                    
                except Exception as e:
                    return [{
                        "type": "text",
                        "text": f"Error transforming message: {str(e)}"
                    }]
            
            elif name == "gap_link_conversations":
                try:
                    chat_ids = arguments['chat_ids']
                    relationship = arguments.get('relationship', 'related')
                    
                    # Create link in context store
                    link_id = f"link_{len(self.context_store)}"
                    self.context_store[link_id] = {
                        'type': 'conversation_link',
                        'chat_ids': chat_ids,
                        'relationship': relationship
                    }
                    
                    return [{
                        "type": "text",
                        "text": f"Linked conversations: {', '.join(chat_ids)} ({relationship})"
                    }]
                    
                except Exception as e:
                    return [{
                        "type": "text",
                        "text": f"Error linking conversations: {str(e)}"
                    }]
            
            else:
                return [{
                    "type": "text",
                    "text": f"Unknown tool: {name}"
                }]

async def main():
    """Run the GAP MCP server"""
    server_instance = GAPMCPServer()
    await server_instance.setup_handlers()
    
    async with StdioServerSession() as session:
        await server_instance.server.run(
            session.read_message,
            session.write_message,
            InitializeParams(
                protocol_version="2024-11-05",
                capabilities={},
                client_info={"name": "gap-mcp-server", "version": "0.1.0"},
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
'''

with open("gap_mcp_server.py", "w") as f:
    f.write(mcp_server_code)

print(f"\n✅ MCP server template created: gap_mcp_server.py")
print(f"   (Note: Requires model-context-protocol package)")

print(f"\n🎉 COMPLETE GAP PROTOCOL ECOSYSTEM READY!")
print(f"="*60)
print(f"You now have:")
print(f"• Core Python implementation")
print(f"• FastAPI web service")  
print(f"• CLI tool")
print(f"• Browser extension templates")
print(f"• MCP server template")
print(f"• Complete documentation")
print(f"• Working examples")
print(f"\n🚀 You can start using GAP immediately with any combination of these tools!")