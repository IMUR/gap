# GAP Protocol Browser Extensions

Browser extensions for seamless GAP Protocol integration with AI chat interfaces.

## Available Extensions

### Chrome Extension ✅
- **Status**: Implemented and ready to use
- **Location**: `chrome/`
- **Features**: Full GAP Protocol support with popup UI and content scripts
- **Supported Sites**: Claude.ai, ChatGPT, Gemini, Copilot, Perplexity, Poe

### Firefox Extension 🚧
- **Status**: Planned (uses same codebase with minor manifest changes)
- **Location**: `firefox/` (future)

### Safari Extension 🚧
- **Status**: Under consideration
- **Location**: `safari/` (future)

## Quick Start

### Installation

1. **Start GAP Service** (required):
   ```bash
   cd ..  # Go to project root
   ./scripts/start_services.sh
   ```

2. **Install Extension**:
   
   **Option A - Load Unpacked (Development)**:
   - Open `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select `extensions/chrome/` directory
   
   **Option B - Build and Install**:
   ```bash
   ./build.sh chrome
   # Drag build/gap-chrome-extension.zip to chrome://extensions/
   ```

3. **Generate Icons** (if missing):
   - Open `chrome/icons/icon.html` in browser
   - Save each canvas as PNG (icon16.png, icon32.png, icon48.png, icon128.png)

## Features

### Core Functionality
- **Wrap Selection**: Add GAP metadata to selected text
- **Transform Content**: Convert GAP content for current platform
- **Entity Detection**: Identify ambiguous references
- **Auto Platform Detection**: Recognizes AI chat interfaces

### User Interface
- **Extension Popup**: Quick access to all features
- **Floating Button**: On-page GAP actions (AI sites only)
- **Context Menu**: Right-click options (coming soon)
- **Keyboard Shortcuts**:
  - `Ctrl/Cmd+Shift+G`: Wrap selection
  - `Ctrl/Cmd+Shift+T`: Transform clipboard

### Integration
- **Clipboard Support**: Read/write GAP content
- **Direct Insertion**: Paste into chat inputs
- **Service Health Check**: Monitor GAP service status
- **Settings Sync**: Preferences across devices

## Development

### Project Structure
```
extensions/
├── build.sh              # Build script for all extensions
├── README.md            # This file
│
├── chrome/              # Chrome/Edge extension
│   ├── manifest.json    # Extension manifest v3
│   ├── background.js    # Service worker
│   ├── content.js       # Content script
│   ├── popup.html       # Popup UI
│   ├── popup.js         # Popup logic
│   ├── popup.css        # Popup styles
│   ├── styles.css       # Content styles
│   ├── icons/          # Extension icons
│   └── README.md       # Chrome-specific docs
│
└── firefox/            # Firefox extension (future)
    └── (similar structure)
```

### Building

```bash
# Build specific extension
./build.sh chrome
./build.sh firefox  # When available

# Build all extensions
./build.sh all

# Clean build artifacts
./build.sh clean
```

### Testing

1. **Local Development**:
   - Make changes in `chrome/` directory
   - Reload extension in Chrome
   - Test on AI chat sites

2. **Service Integration**:
   - Ensure GAP service is running
   - Check console for API calls
   - Verify clipboard operations

3. **Debugging**:
   - Background: `chrome://extensions/` → "Service worker"
   - Popup: Right-click icon → "Inspect popup"
   - Content: F12 on AI chat page

## Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome | ✅ Full | v88+ required for Manifest V3 |
| Edge | ✅ Full | Uses Chrome extension |
| Brave | ✅ Full | Uses Chrome extension |
| Firefox | 🚧 Planned | Minor manifest changes needed |
| Safari | 🚧 Considering | Requires Xcode for packaging |
| Opera | ⚠️ Partial | Should work, not tested |

## Security & Privacy

- **Local Processing**: All GAP operations happen locally
- **No Tracking**: No analytics or data collection
- **Secure Communication**: Only connects to localhost by default
- **Permission Minimal**: Only required permissions requested
- **Open Source**: Full code transparency

## Troubleshooting

### Common Issues

1. **"Service not available"**
   - Start GAP service: `./scripts/start_services.sh`
   - Check service URL in popup settings

2. **Extension not appearing**
   - Ensure Developer mode is enabled
   - Check for loading errors in extensions page

3. **Clipboard not working**
   - Grant clipboard permissions when prompted
   - Some sites may block clipboard access

4. **Icons missing**
   - Generate using `chrome/icons/icon.html`
   - Or download from project assets

## Contributing

### Adding Platform Support

To support a new AI platform:

1. Add domain to `manifest.json` content_scripts
2. Update platform detection in `background.js`
3. Add input selector to `content.js`
4. Test transformation rules

### Creating New Features

1. Follow existing code patterns
2. Update manifest if new permissions needed
3. Add UI elements to popup if user-facing
4. Document in README

## Roadmap

- [x] Chrome extension MVP
- [x] Keyboard shortcuts
- [x] Floating action button
- [ ] Firefox port
- [ ] Context menu integration
- [ ] Entity management UI
- [ ] Batch operations
- [ ] Cloud sync support
- [ ] Safari extension
- [ ] Mobile support (Kiwi Browser)

## License

Same as GAP Protocol project license.