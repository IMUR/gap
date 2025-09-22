# GAP Protocol - Guides

Step-by-step guides for common GAP Protocol tasks.

## Available Guides

### [SETUP.md](./SETUP.md)
Complete installation and configuration guide.

### [USAGE.md](./USAGE.md)
How to use GAP Protocol in your workflow.

### [INTEGRATION.md](./INTEGRATION.md)
Integrating GAP with various AI platforms and tools.

### [DEVELOPMENT.md](./DEVELOPMENT.md)
Contributing to the GAP Protocol project.

## Quick Start

1. **Install**: Follow [SETUP.md](./SETUP.md) to get GAP running
2. **Learn**: Read [USAGE.md](./USAGE.md) for basic operations
3. **Integrate**: See [INTEGRATION.md](./INTEGRATION.md) for your platforms
4. **Contribute**: Check [DEVELOPMENT.md](./DEVELOPMENT.md) to help improve GAP

## Common Tasks

- **Wrap content from clipboard**: `uv run gap-cli wrap --clipboard --platform claude.ai --chat-id session --copy`
- **Transform for another AI**: `uv run gap-cli transform --clipboard --target chatgpt --copy`
- **Start the service**: `./scripts/start_services.sh`
- **Run tests**: `uv run pytest`

For complete documentation, see the [root README.md](../../README.md).