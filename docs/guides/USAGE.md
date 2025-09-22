# GAP Protocol - Usage Guide

## Basic Concepts

GAP wraps your AI conversation content with metadata to:
- Preserve context across sessions
- Resolve ambiguous references
- Transform content for different platforms

## CLI Usage

### Wrapping Content

```bash
# Wrap text directly
uv run gap-cli wrap "Your content here" --platform claude.ai --chat-id session1

# Wrap from clipboard
uv run gap-cli wrap --clipboard --platform chatgpt --chat-id session2

# Wrap from file
uv run gap-cli wrap --stdin < input.txt --platform gemini --chat-id session3

# Include entities
uv run gap-cli wrap "The system is slow" \
  --platform claude.ai \
  --chat-id debug1 \
  --thread-id performance
```

### Transforming Content

```bash
# Transform from file
uv run gap-cli transform input.gap --target chatgpt

# Transform from clipboard
uv run gap-cli transform --clipboard --target gemini --copy

# Add context
uv run gap-cli transform input.gap \
  --target claude.ai \
  --context '{"Project": "E-commerce v2"}'
```

### Updating Entities

```bash
# Define an ambiguous reference
uv run gap-cli update-entity input.gap \
  --key the_system \
  --value "PostgreSQL 14.5 database"

# Update from clipboard
uv run gap-cli update-entity --clipboard \
  --key the_approach \
  --value "Incremental indexing strategy" \
  --copy
```

## Service Usage

### Starting the Service

```bash
# Start in foreground
./scripts/start_services.sh

# Or with UV directly
uv run uvicorn services.fastapi_service:app --reload
```

### Using the API

```bash
# Wrap content via API
curl -X POST http://localhost:8000/gap/wrap \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The database query is slow",
    "platform": "claude.ai",
    "chat_id": "debug_session"
  }'

# Transform content
curl -X POST http://localhost:8000/gap/transform \
  -H "Content-Type: application/json" \
  -d '{
    "gap_markdown": "[GAP:START]...[GAP:END]",
    "target_platform": "chatgpt"
  }'
```

## Python Usage

### As a Library

```python
from src.gap import GAPProtocol

# Initialize
gap = GAPProtocol()

# Wrap content
wrapped = gap.wrap_message(
    content="The system performance has degraded",
    platform="claude.ai",
    chat_id="perf_analysis",
    entities={
        "the_system": {
            "type": "service",
            "value": "API Gateway"
        }
    }
)

# Transform for another platform
transformed = gap.transform_for_platform(
    wrapped,
    target_platform="chatgpt"
)

print(transformed)
```

## ZED Integration

### Using Tasks

1. Select text in editor
2. Copy to clipboard (Cmd+C)
3. Run GAP task:
   - `Cmd+Shift+G, W` - Wrap with GAP
   - `Cmd+Shift+G, T` - Transform
   - `Cmd+Shift+G, E` - Update entity

### Available Tasks

- **GAP: Start Service** - Launch API service
- **GAP: Wrap Selection** - Wrap clipboard content
- **GAP: Transform Clipboard** - Transform for platform
- **GAP: Update Entity** - Define entities
- **GAP: Run Tests** - Execute test suite

## Workflow Examples

### Cross-AI Debugging Session

1. **In Claude.ai**: Describe a bug
2. **Wrap**: Copy response, wrap with GAP
3. **In ChatGPT**: Paste wrapped content
4. **Transform**: ChatGPT understands context
5. **Continue**: Seamless conversation flow

### Multi-Platform Code Review

```bash
# Get code review from Claude
uv run gap-cli wrap --clipboard \
  --platform claude.ai \
  --chat-id "code_review_1" \
  --copy

# Transform for ChatGPT
uv run gap-cli transform --clipboard \
  --target chatgpt \
  --copy

# Transform for Gemini
uv run gap-cli transform --clipboard \
  --target gemini \
  --copy
```

### Building Context Graphs

```python
from src.gap import GAPProtocol, create_context_graph

gap = GAPProtocol()
messages = []

# Collect messages from different sessions
for content in conversation_history:
    msg = gap.wrap_message(content, **metadata)
    messages.append(msg)

# Build relationship graph
graph = create_context_graph(messages)

# Analyze connections
print(f"Found {len(graph['entity_definitions'])} entities")
print(f"Timeline has {len(graph['timeline'])} messages")
```

## Best Practices

1. **Always include platform and chat_id** for tracking
2. **Use thread_id** for related conversations
3. **Define entities** when introducing new concepts
4. **Copy to clipboard** for quick platform switches
5. **Use the service** for programmatic access
6. **Keep markdown format** for manual editing

## Tips & Tricks

- **Clipboard workflow**: Use `--clipboard` and `--copy` for speed
- **Batch processing**: Pipe files through CLI
- **Entity shortcuts**: Define common entities in scripts
- **Platform testing**: Transform to 'generic' to see raw output
- **Debug mode**: Set `GAP_LOG_LEVEL=DEBUG` for verbose output

## Next Steps

- See [INTEGRATION.md](./INTEGRATION.md) for platform-specific setup
- Check [examples/](../../examples/) for code samples
- Read [API.md](../architecture/API.md) for service details