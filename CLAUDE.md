# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GAP (Global Addressment Protocol) is a Python toolkit for preserving context when transferring content between AI chat sessions. It wraps messages with metadata to resolve ambiguous references like "the system" or "that approach" and transforms content for different AI platforms.

## Essential Commands

### Development Setup
```bash
# Install dependencies (uses UV package manager)
uv sync

# Install with dev dependencies
uv sync --dev
```

### Running Services
```bash
# Start FastAPI service (port 8000)
./scripts/start_services.sh

# Or directly with UV
uv run uvicorn services.fastapi_service:app --reload
```

### CLI Operations
```bash
# Wrap content with GAP metadata
uv run gap-cli wrap "content" --platform claude.ai --chat-id session1

# Transform GAP content for another platform
uv run gap-cli transform --clipboard --target chatgpt --copy

# Update entity definitions
uv run gap-cli update-entity --clipboard --key the_system --value "PostgreSQL 14.5"
```

### Testing & Quality
```bash
# Run tests (currently no test files implemented)
uv run pytest

# Run specific test
uv run pytest tests/test_protocol.py -v

# Format code
uv run black .
uv run ruff check --fix .

# Type checking
uv run mypy src/

# Lint and format check (no auto-fix)
uv run black --check .
uv run ruff check .
```

## Architecture Overview

### Core Protocol Design (`src/gap/`)

The protocol follows a modular separation of concerns:

1. **`protocol.py`** - Main `GAPProtocol` class orchestrates all operations. It delegates to specialized components rather than implementing everything itself.

2. **`models.py`** - Pydantic models define the GAP message structure. Key models:
   - `GAPMessage` wraps everything with version info
   - `GAPMessageContent` contains the actual content and metadata
   - `GAPEntity` represents detected/defined entities

3. **`entities.py`** - `EntityDetector` and `PronounTransformer` handle:
   - Auto-detecting ambiguous references using regex patterns
   - Transforming pronouns based on role (assistant/user/system)
   - Suggesting entity definitions from context

4. **`transformers.py`** - `PlatformTransformer` adapts content for different AI platforms, each with specific formatting preferences (Claude uses markdown, ChatGPT uses headers, etc.)

### Service Layer (`services/`)

- **`fastapi_service.py`** - REST API with in-memory storage for context graphs. Provides endpoints for wrapping, transforming, and managing GAP messages. Auto-generates OpenAPI docs at `/docs`.

- **`mcp_server.py`** - MCP (Model Context Protocol) server for AI tool integration (requires additional MCP library).

### Dual-Mode CLI (`cli/gap_cli.py`)

The CLI can operate in two modes:
- **Direct mode** (default): Imports and uses `GAPProtocol` directly
- **API mode**: Makes HTTP requests to the FastAPI service

Mode is controlled by `GAP_USE_API` environment variable.

### Key Design Patterns

1. **Markdown as Transport Format**: GAP messages use a human-readable markdown format `[GAP:START]...[GAP:END]` that can be copied/pasted between AI chats.

2. **Entity Detection Pipeline**: Content flows through detection → merging with user-provided entities → transformation based on target platform.

3. **Platform Configurations**: Each AI platform has specific formatting rules defined in `PlatformTransformer.PLATFORM_CONFIGS`.

## Project Constraints

### Critical Rules (from `docs/governance/RULES.md`)

- **Port 8000 is hardcoded** - FastAPI service must use this port
- **Archive is read-only** - Never modify files in `.archive/`
- **Use absolute imports** - Always `from src.gap import ...`
- **Python 3.11+ required** - Project uses UV and modern Python features
- **Use `git mv` for file moves** - Preserves history
- **Dependencies via UV only** - No manual pip installs

### File Organization

- Configuration files (`pyproject.toml`, `.python-version`) must stay at root
- Test files go in `tests/` (currently empty, needs implementation)
- Documentation follows Universal Documentation Strategy in `docs/`

## Working with GAP Messages

### Message Flow
1. User provides content with ambiguous references
2. `EntityDetector` identifies ambiguous terms
3. User can define entities explicitly
4. `PronounTransformer` maps pronouns based on role
5. `PlatformTransformer` formats for target AI platform
6. Result includes resolved references and proper context

### Context Graphs
Multiple GAP messages can be linked via `create_context_graph()` to track:
- Entity definitions across messages
- Timeline of interactions
- Platform/thread relationships

## ZED IDE Integration

When working in ZED:
- Tasks defined in `.zed/tasks.json`
- Key bindings: `Cmd+Shift+G` prefix for GAP operations
- Dependencies auto-install on project open

## Environment Variables

```bash
GAP_USE_API=false      # Use direct mode (default) or API mode
GAP_API_URL=http://localhost:8000  # API URL if using API mode  
GAP_LOG_LEVEL=INFO     # Logging verbosity
```

## Important Notes

- Browser extension code exists in `.archive/initial-implementation/browser-extension/` but hasn't been properly extracted to `extensions/chrome/`
- Test suite needs implementation - `tests/` directory exists but is empty
- MCP server requires additional `model-context-protocol` library not in dependencies