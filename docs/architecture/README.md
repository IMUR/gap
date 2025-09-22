# GAP Protocol - Architecture

Technical design and implementation documentation for the GAP Protocol.

## Documents

### [STRUCTURE.md](./STRUCTURE.md)
Current project structure and organization (migrated from PROJECT_STRUCTURE_SUMMARY.md).

### [PROTOCOL.md](./PROTOCOL.md)
Detailed specification of the GAP Protocol format and operations.

### [API.md](./API.md)
REST API documentation for the FastAPI service.

## Architecture Overview

The GAP Protocol follows a modular, layered architecture:

```
┌─────────────────────────────────────┐
│         External Interfaces         │
│  (CLI, REST API, Browser Extension) │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│          Service Layer              │
│   (FastAPI Service, MCP Server)     │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│           Core Protocol             │
│  (GAPProtocol, Models, Transformers)│
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│        Foundation Layer             │
│   (Entities, Pronouns, Detection)   │
└─────────────────────────────────────┘
```

## Key Design Principles

1. **Separation of Concerns** - Each module has a single responsibility
2. **Dependency Injection** - Components are loosely coupled
3. **Protocol First** - The GAP format is the contract
4. **Platform Agnostic** - Core works independently of platforms
5. **Extensible** - Easy to add new platforms and transformers

## Module Descriptions

See individual documentation files for detailed specifications.