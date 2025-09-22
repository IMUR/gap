# GAP Protocol Specification

Version 0.1.0

## Overview

The Global Addressment Protocol (GAP) is a metadata wrapping protocol designed to preserve context and resolve ambiguity when transferring content between different AI conversation sessions.

## Protocol Format

### Markdown Format

The human-readable format uses markdown with specific markers:

```markdown
[GAP:START]
From: {platform} | Thread: {thread_id}
Context: {role} message from {timestamp}
Entities: "{key1}" = {value1}, "{key2}" = {value2}
[GAP:CONTENT]
{actual_message_content}
[GAP:END]
```

### JSON Structure

The programmatic format uses nested objects:

```json
{
  "gap_version": "0.1.0",
  "message": {
    "content": "string",
    "source": {
      "platform": "string",
      "model": "string|null",
      "chat_id": "string",
      "timestamp": "ISO-8601",
      "role": "assistant|user|system"
    },
    "context": {
      "thread_id": "string|null",
      "parent_messages": ["string"],
      "entities": {
        "entity_key": {
          "type": "string",
          "value": "string",
          "defined_in": "string|null"
        }
      }
    },
    "transform_hints": {
      "maintain_tense": "string|null",
      "preserve_perspective": "string|null",
      "pronoun_map": {
        "old": "new"
      }
    }
  }
}
```

## Entity Detection

### Automatic Detection

The protocol automatically detects common ambiguous references:

- `the system` → Needs specific system identification
- `the database` → Needs database specification
- `the approach` → Needs methodology description
- `that method` → Needs method clarification
- `this implementation` → Needs implementation details

### Entity Types

- `ambiguous_reference` - Detected but undefined
- `technical_component` - System components
- `software_version` - Version specifications
- `framework` - Software frameworks
- `database` - Database systems
- `file_reference` - File paths and names
- `user_defined` - Custom entities

## Pronoun Transformation

### Role-Based Mappings

**Assistant Role:**
- I → the AI assistant
- my → the AI assistant's
- me → the AI assistant

**User Role:**
- I → the user
- my → the user's
- me → the user

## Platform Transformations

### Supported Platforms

Each platform has specific formatting:

- **claude.ai** - Uses [Context from GAP-wrapped message] prefix
- **chatgpt** - Uses # Context header format
- **gemini** - Uses **bold** context markers
- **copilot** - Uses // comment style
- **perplexity** - Uses bullet points for context
- **generic** - Plain text format

## Operations

### Core Operations

1. **wrap_message** - Add GAP metadata to content
2. **transform_for_platform** - Adapt for target platform
3. **from_markdown** - Parse GAP markdown format
4. **to_markdown** - Convert to human-readable format
5. **update_entity** - Define or update entities
6. **create_context_graph** - Build relationship graph

### Entity Operations

1. **detect_entities** - Find ambiguous references
2. **merge_entities** - Combine detected and provided
3. **suggest_definitions** - Propose entity values
4. **find_undefined** - List entities needing definition

## Use Cases

### Cross-Platform Context Transfer

```python
# Wrap content from Claude
wrapped = gap.wrap_message(
    content="The system needs optimization",
    platform="claude.ai",
    chat_id="session_123"
)

# Transform for ChatGPT
transformed = gap.transform_for_platform(
    wrapped,
    target_platform="chatgpt"
)
```

### Entity Clarification

```python
# Update ambiguous references
wrapped = gap.update_entity(
    wrapped,
    entity_key="the_system",
    entity_value="PostgreSQL 14.5 cluster"
)
```

### Context Graph Building

```python
# Build relationships from multiple messages
messages = [msg1, msg2, msg3]
graph = create_context_graph(messages)
```

## Best Practices

1. **Always define entities** when they're ambiguous
2. **Preserve thread IDs** for conversation continuity
3. **Use appropriate roles** (assistant/user/system)
4. **Include timestamps** for temporal context
5. **Transform for target** platform conventions

## Version History

- **0.1.0** (Current) - Initial protocol specification
  - Basic wrapping and transformation
  - Entity detection and management
  - Platform-specific formatting

## Future Enhancements

- Nested entity references
- Multi-language support
- Binary content handling
- Compression for large contexts
- Cryptographic signatures