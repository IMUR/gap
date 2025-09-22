
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
from src.gap import GAPProtocol

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
                        "text": f"Message wrapped with GAP:\n\n{markdown}"
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
                        "text": f"Transformed content:\n\n{transformed}"
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
