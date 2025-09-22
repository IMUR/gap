# GAP Protocol REST API

Base URL: `http://localhost:8000`

## Endpoints

### Core Operations

#### POST /gap/wrap
Wrap content with GAP metadata.

**Request:**
```json
{
  "content": "string",
  "platform": "string",
  "chat_id": "string",
  "role": "assistant|user|system",
  "model": "string|null",
  "thread_id": "string|null",
  "entities": {
    "key": {
      "type": "string",
      "value": "string"
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message_id": "string",
  "gap_json": {},
  "gap_markdown": "string",
  "undefined_entities": ["string"],
  "suggested_definitions": {}
}
```

#### POST /gap/transform
Transform GAP content for a target platform.

**Request:**
```json
{
  "gap_markdown": "string",
  "target_platform": "string",
  "context_additions": {},
  "include_metadata": true
}
```

**Response:**
```json
{
  "status": "success",
  "transformed_content": "string",
  "original_entities": {},
  "undefined_entities": ["string"],
  "target_platform": "string"
}
```

#### POST /gap/update-entity
Update entity definition in GAP content.

**Request:**
```json
{
  "gap_markdown": "string",
  "entity_key": "string",
  "entity_value": "string",
  "entity_type": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "updated_markdown": "string",
  "updated_entity": {},
  "all_entities": {}
}
```

### Context Management

#### GET /gap/context/{thread_id}
Retrieve context for a thread.

**Response:**
```json
{
  "status": "success",
  "thread_id": "string",
  "message_count": 0,
  "context": [],
  "context_graph": {}
}
```

#### POST /gap/link-chats
Create relationships between chat sessions.

**Request:**
```json
{
  "chat_ids": ["string"],
  "relationship": "sequential|parallel|related"
}
```

### Utility Endpoints

#### GET /gap/platforms
List supported transformation platforms.

**Response:**
```json
{
  "status": "success",
  "platforms": ["claude.ai", "chatgpt", "gemini", ...]
}
```

#### GET /health
Service health check.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "cached_messages": 0,
  "active_threads": 0
}
```

#### GET /
API information and endpoints.

## Authentication

Currently no authentication required (local service).

## Error Responses

All errors return appropriate HTTP status codes:

```json
{
  "detail": "Error description"
}
```

- `400` - Bad request (invalid input)
- `404` - Resource not found
- `500` - Internal server error

## Interactive Documentation

When the service is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc