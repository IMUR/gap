# GAP Protocol Chrome Extension

Browser extension for using GAP Protocol directly in AI chat interfaces.

## Features

- **Quick Wrap**: Select text and wrap with GAP metadata
- **Transform**: Convert GAP content from clipboard for current platform
- **Auto-detect**: Automatically identifies AI platforms
- **Floating Button**: Quick access to GAP functions on supported sites
- **Keyboard Shortcuts**: 
  - `Ctrl/Cmd+Shift+G`: Wrap selected text
  - `Ctrl/Cmd+Shift+T`: Transform clipboard content

## Installation

### Development Mode

1. **Generate Icons**:
   ```bash
   # Open icons/icon.html in browser
   # Right-click each canvas and save as:
   # - icon16.png, icon32.png, icon48.png, icon128.png
   ```

2. **Start GAP Service**:
   ```bash
   # From project root
   ./scripts/start_services.sh
   ```

3. **Load Extension**:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (top right)
   - Click "Load unpacked"
   - Select the `extensions/chrome/` directory

### Production Build

```bash
# From project root
cd extensions/chrome
zip -r ../../gap-extension.zip . -x "*.md" -x "*.sh" -x "*.html"
```

## Usage

### On Supported Sites

The extension automatically activates on:
- claude.ai
- chat.openai.com
- gemini.google.com
- copilot.microsoft.com
- perplexity.ai
- poe.com

A floating GAP button appears in the bottom-right corner.

### Popup Interface

Click the extension icon in the toolbar to:
1. **Wrap Selection**: Wraps selected text with GAP metadata
2. **Transform from Clipboard**: Converts GAP content for current platform
3. **Configure Settings**: Set thread ID, target platform, service URL

### Content Script Features

On AI chat pages:
- **Floating Button**: Click for quick access menu
- **Auto-insert**: Transformed content can be inserted directly into chat input
- **Visual Feedback**: Notifications show operation status

## Configuration

### Service URL

By default, connects to `http://localhost:8000`. To change:
1. Click extension icon
2. Update "Service URL" field
3. Changes save automatically

### Thread Management

Set a Thread ID to link related conversations:
1. Click extension icon
2. Enter Thread ID
3. All subsequent wraps use this thread

## Permissions

The extension requires:
- **activeTab**: To read selected text
- **clipboardRead/Write**: For clipboard operations
- **storage**: To save settings
- **scripting**: To interact with page content

## Troubleshooting

### Service Not Connected

1. Check if GAP service is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Start service if needed:
   ```bash
   ./scripts/start_services.sh
   ```

### Extension Not Working

1. Check Chrome console for errors:
   - Right-click extension icon → "Inspect popup"
   - Check Console tab

2. Reload extension:
   - Go to `chrome://extensions/`
   - Click refresh icon on GAP extension

### Icons Not Showing

1. Generate icons using `icons/icon.html`
2. Save each canvas as PNG with correct filename
3. Reload extension

## Development

### File Structure

```
chrome/
├── manifest.json       # Extension configuration
├── background.js      # Service worker
├── content.js        # Content script for AI sites
├── popup.html        # Extension popup UI
├── popup.js          # Popup logic
├── popup.css         # Popup styles
├── styles.css        # Content script styles
└── icons/            # Extension icons
```

### Testing Changes

1. Make changes to files
2. Go to `chrome://extensions/`
3. Click refresh icon on GAP extension
4. Test on AI chat sites

### Debugging

- **Background Script**: chrome://extensions/ → "Inspect views: service worker"
- **Content Script**: F12 on AI chat page → Console
- **Popup**: Right-click extension icon → "Inspect popup"

## API Integration

The extension communicates with the GAP service API:

- `POST /gap/wrap` - Wrap content with metadata
- `POST /gap/transform` - Transform for target platform
- `GET /health` - Check service status

## Security

- Only connects to localhost by default
- No external data transmission
- All processing happens locally
- Settings stored in Chrome sync storage

## Future Enhancements

- [ ] Firefox support
- [ ] Safari support
- [ ] Cloud service option
- [ ] Batch operations
- [ ] Entity management UI
- [ ] Context graph visualization
- [ ] Custom platform configurations