# GAP Protocol (Global Addressment Protocol)

> 🌍 Preserving context and continuity across AI conversations

## Overview

GAP (Global Addressment Protocol) is a protocol and toolkit for maintaining context when coordinating between multiple AI chat sessions. It solves the problem of ambiguous references, lost context, and pronoun confusion when copying content between different AI platforms.

## Features

- **🔄 Context Preservation**: Automatically detects and preserves entity definitions
- **🎯 Ambiguity Resolution**: Identifies and resolves ambiguous references like "the system" or "that approach"
- **🔀 Platform Transformation**: Adapts content for different AI platforms (Claude, ChatGPT, Gemini, etc.)
- **🖥️ ZED IDE Integration**: Seamless integration with ZED editor via ACP protocol
- **⚡ Fast UV-based Setup**: Modern Python tooling with UV package manager
- **🌐 Web Service**: FastAPI service for programmatic access
- **📦 Browser Extension**: Capture and transform content directly from AI chat interfaces

## Quick Start

### Prerequisites

- Python 3.11+
- [UV package manager](https://github.com/astral-sh/uv) (installed automatically if missing)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd GAP

# Run the installation script
./scripts/install.sh

# Or manually with UV
uv sync
```

### Basic Usage

#### Start the Service

```bash
# Start the FastAPI service
./scripts/start_services.sh

# Service will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

#### CLI Usage

```bash
# Wrap content with GAP metadata
uv run gap-cli wrap "The system needs optimization" \
  --platform claude.ai \
  --chat-id session123

# Transform for another platform
uv run gap-cli transform input.gap --target chatgpt

# Update entity definitions
uv run gap-cli update-entity input.gap \
  --key the_system \
  --value "PostgreSQL 14.5 database cluster"

# Work with clipboard
uv run gap-cli wrap --clipboard --platform gemini --chat-id test --copy
```

#### ZED IDE Integration

The project includes full ZED IDE integration:

1. Open the project in ZED
2. Dependencies auto-install on open
3. Use keyboard shortcuts:
   - `Cmd+Shift+G, W` - Wrap selection with GAP
   - `Cmd+Shift+G, T` - Transform clipboard content
   - `Cmd+Shift+G, E` - Update entity definition
   - `Cmd+Shift+G, S` - Start GAP service

## Project Structure

```
GAP/
├── src/gap/              # Core protocol implementation
│   ├── protocol.py       # Main GAP Protocol class
│   ├── models.py        # Pydantic data models
│   ├── entities.py      # Entity detection and management
│   └── transformers.py  # Platform-specific transformers
├── services/            # Service implementations
│   ├── fastapi_service.py  # REST API service
│   └── mcp_server.py       # MCP server for AI tools
├── cli/                 # Command-line interface
├── extensions/          # Browser extension
├── .zed/               # ZED IDE configuration
└── scripts/            # Utility scripts
```

## API Examples

### Python

```python
from src.gap import GAPProtocol

# Initialize protocol
gap = GAPProtocol()

# Wrap a message
wrapped = gap.wrap_message(
    content="The system we discussed needs optimization",
    platform="claude.ai",
    chat_id="session_123",
    entities={
        "the_system": {
            "type": "technical_component",
            "value": "PostgreSQL database cluster"
        }
    }
)

# Transform for another platform
transformed = gap.transform_for_platform(
    wrapped,
    target_platform="chatgpt"
)
```

### REST API

```bash
# Wrap content
curl -X POST http://localhost:8000/gap/wrap \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The system needs optimization",
    "platform": "claude.ai",
    "chat_id": "session123"
  }'

# Transform content
curl -X POST http://localhost:8000/gap/transform \
  -H "Content-Type: application/json" \
  -d '{
    "gap_markdown": "[GAP:START]...[GAP:END]",
    "target_platform": "chatgpt"
  }'
```

## GAP Markdown Format

GAP uses a human-readable markdown format:

```markdown
[GAP:START]
From: claude.ai | Thread: database_optimization
Context: assistant message from 2024-01-15T10:30:00
Entities: "the_system" = PostgreSQL 14.5, "the_approach" = Index optimization
[GAP:CONTENT]
The system performance has improved significantly with the approach we implemented.
[GAP:END]
```

## Development

### Setup Development Environment

```bash
# Full development setup
./scripts/dev_setup.sh

# Run tests
uv run pytest

# Format code
uv run black .
uv run ruff check --fix .

# Type checking
uv run mypy src/
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/gap

# Run specific test file
uv run pytest tests/test_protocol.py
```

## Configuration

### Environment Variables

Create a `.env` file:

```env
# Use API mode (true) or direct mode (false)
GAP_USE_API=false

# API URL (if using API mode)
GAP_API_URL=http://localhost:8000

# Log level
GAP_LOG_LEVEL=INFO
```

### ZED Configuration

The project includes ZED-specific configuration in `.zed/`:
- `tasks.json` - Task definitions for GAP operations
- `settings.json` - Project settings and key bindings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and formatting
5. Submit a pull request

## License

[Your License Here]

## Acknowledgments

- Original concept and proposal by [user]
- Initial implementation by Perplexity AI
- Enhancements and ZED integration by Claude
- UV-based restructuring and modern tooling updates

## Support

- Report issues at: [GitHub Issues URL]
- Documentation: See `/docs` folder
- API Documentation: http://localhost:8000/docs (when service is running)