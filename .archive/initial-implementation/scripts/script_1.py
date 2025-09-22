# Now let's create a FastAPI service for GAP transformations

fastapi_code = '''
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import re
from datetime import datetime

# Import our GAP protocol (would be in a separate file in real implementation)
# For now, we'll include a simplified version

app = FastAPI(
    title="GAP Protocol Service",
    description="Global Addressment Protocol for AI chat context preservation",
    version="0.1.0"
)

# Enable CORS for browser-based clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class WrapRequest(BaseModel):
    content: str
    platform: str
    chat_id: str
    role: str = "assistant"
    model: Optional[str] = None
    thread_id: Optional[str] = None
    entities: Optional[Dict[str, Dict[str, str]]] = None

class TransformRequest(BaseModel):
    gap_markdown: str
    target_platform: str
    context_additions: Optional[Dict[str, str]] = None

class EntityUpdateRequest(BaseModel):
    gap_markdown: str
    entity_key: str
    entity_value: str
    entity_type: str = "user_defined"

# In-memory storage for context graphs (would be a database in production)
context_store = {}
chat_links = {}

@app.post("/gap/wrap")
async def wrap_message(request: WrapRequest):
    """Wrap a message with GAP metadata"""
    try:
        gap = GAPProtocol()
        wrapped = gap.wrap_message(
            content=request.content,
            platform=request.platform,
            chat_id=request.chat_id,
            role=request.role,
            model=request.model,
            thread_id=request.thread_id,
            entities=request.entities
        )
        
        return {
            "status": "success",
            "gap_json": wrapped.dict(),
            "gap_markdown": gap.to_markdown(wrapped)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/gap/transform")
async def transform_message(request: TransformRequest):
    """Transform a GAP message for a target platform"""
    try:
        gap = GAPProtocol()
        parsed = gap.from_markdown(request.gap_markdown)
        
        if not parsed:
            raise HTTPException(status_code=400, detail="Invalid GAP markdown format")
        
        transformed_content = gap.transform_for_platform(
            parsed,
            request.target_platform,
            request.context_additions
        )
        
        return {
            "status": "success",
            "transformed_content": transformed_content,
            "original_entities": parsed.message.context.entities
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/gap/update-entity")
async def update_entity(request: EntityUpdateRequest):
    """Update an entity definition in a GAP message"""
    try:
        gap = GAPProtocol()
        parsed = gap.from_markdown(request.gap_markdown)
        
        if not parsed:
            raise HTTPException(status_code=400, detail="Invalid GAP markdown format")
        
        # Update the entity
        from gap_protocol import GAPEntity  # Would import from separate module
        parsed.message.context.entities[request.entity_key] = GAPEntity(
            type=request.entity_type,
            value=request.entity_value
        )
        
        # Return updated markdown
        updated_markdown = gap.to_markdown(parsed)
        
        return {
            "status": "success",
            "updated_markdown": updated_markdown,
            "updated_entity": {
                "key": request.entity_key,
                "value": request.entity_value,
                "type": request.entity_type
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/gap/link-chats")
async def link_chats(chat_ids: list[str], relationship: str = "sequential"):
    """Create a relationship between chat sessions"""
    try:
        link_id = f"link_{len(chat_links)}"
        chat_links[link_id] = {
            "chat_ids": chat_ids,
            "relationship": relationship,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "link_id": link_id,
            "linked_chats": chat_ids,
            "relationship": relationship
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/gap/context/{thread_id}")
async def get_thread_context(thread_id: str):
    """Get all context for a thread"""
    try:
        thread_context = context_store.get(thread_id, {})
        return {
            "status": "success",
            "thread_id": thread_id,
            "context": thread_context
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0"}

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "GAP Protocol Service",
        "version": "0.1.0",
        "endpoints": {
            "wrap": "POST /gap/wrap - Wrap content with GAP metadata",
            "transform": "POST /gap/transform - Transform GAP content for target platform",
            "update_entity": "POST /gap/update-entity - Update entity definitions",
            "link_chats": "POST /gap/link-chats - Link chat sessions",
            "get_context": "GET /gap/context/{thread_id} - Get thread context"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

# Save the FastAPI service code
with open("gap_fastapi_service.py", "w") as f:
    f.write(fastapi_code)

print("✅ FastAPI service code generated: gap_fastapi_service.py")

# Now let's create a CLI tool
cli_code = '''#!/usr/bin/env python3
import argparse
import json
import sys
import requests
from pathlib import Path

class GAPCli:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
    
    def wrap(self, content, platform, chat_id, **kwargs):
        """Wrap content with GAP metadata"""
        data = {
            "content": content,
            "platform": platform,
            "chat_id": chat_id,
            **kwargs
        }
        
        response = requests.post(f"{self.api_url}/gap/wrap", json=data)
        if response.status_code == 200:
            result = response.json()
            return result["gap_markdown"]
        else:
            raise Exception(f"API Error: {response.text}")
    
    def transform(self, gap_markdown, target_platform, context_additions=None):
        """Transform GAP content for target platform"""
        data = {
            "gap_markdown": gap_markdown,
            "target_platform": target_platform,
            "context_additions": context_additions
        }
        
        response = requests.post(f"{self.api_url}/gap/transform", json=data)
        if response.status_code == 200:
            result = response.json()
            return result["transformed_content"]
        else:
            raise Exception(f"API Error: {response.text}")
    
    def update_entity(self, gap_markdown, entity_key, entity_value, entity_type="user_defined"):
        """Update an entity in GAP content"""
        data = {
            "gap_markdown": gap_markdown,
            "entity_key": entity_key,
            "entity_value": entity_value,
            "entity_type": entity_type
        }
        
        response = requests.post(f"{self.api_url}/gap/update-entity", json=data)
        if response.status_code == 200:
            result = response.json()
            return result["updated_markdown"]
        else:
            raise Exception(f"API Error: {response.text}")

def main():
    parser = argparse.ArgumentParser(description="GAP Protocol CLI Tool")
    parser.add_argument("--api-url", default="http://localhost:8000", help="GAP API URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Wrap command
    wrap_parser = subparsers.add_parser("wrap", help="Wrap content with GAP metadata")
    wrap_parser.add_argument("content", help="Content to wrap")
    wrap_parser.add_argument("--platform", required=True, help="Source platform")
    wrap_parser.add_argument("--chat-id", required=True, help="Chat identifier")
    wrap_parser.add_argument("--thread-id", help="Thread identifier")
    wrap_parser.add_argument("--role", default="assistant", help="Message role")
    wrap_parser.add_argument("--output", "-o", help="Output file")
    
    # Transform command
    transform_parser = subparsers.add_parser("transform", help="Transform GAP content")
    transform_parser.add_argument("input_file", help="GAP markdown file")
    transform_parser.add_argument("--target", required=True, help="Target platform")
    transform_parser.add_argument("--context", help="Additional context (JSON)")
    transform_parser.add_argument("--output", "-o", help="Output file")
    
    # Update entity command
    entity_parser = subparsers.add_parser("update-entity", help="Update entity definition")
    entity_parser.add_argument("input_file", help="GAP markdown file")
    entity_parser.add_argument("--key", required=True, help="Entity key")
    entity_parser.add_argument("--value", required=True, help="Entity value")
    entity_parser.add_argument("--type", default="user_defined", help="Entity type")
    entity_parser.add_argument("--output", "-o", help="Output file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = GAPCli(args.api_url)
    
    try:
        if args.command == "wrap":
            result = cli.wrap(
                content=args.content,
                platform=args.platform,
                chat_id=args.chat_id,
                thread_id=args.thread_id,
                role=args.role
            )
            
            if args.output:
                with open(args.output, "w") as f:
                    f.write(result)
                print(f"GAP wrapped content saved to {args.output}")
            else:
                print(result)
        
        elif args.command == "transform":
            with open(args.input_file, "r") as f:
                gap_markdown = f.read()
            
            context_additions = None
            if args.context:
                context_additions = json.loads(args.context)
            
            result = cli.transform(gap_markdown, args.target, context_additions)
            
            if args.output:
                with open(args.output, "w") as f:
                    f.write(result)
                print(f"Transformed content saved to {args.output}")
            else:
                print(result)
        
        elif args.command == "update-entity":
            with open(args.input_file, "r") as f:
                gap_markdown = f.read()
            
            result = cli.update_entity(gap_markdown, args.key, args.value, args.type)
            
            if args.output:
                with open(args.output, "w") as f:
                    f.write(result)
                print(f"Updated GAP content saved to {args.output}")
            else:
                print(result)
                
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

# Save the CLI tool
with open("gap_cli.py", "w") as f:
    f.write(cli_code)

print("✅ CLI tool generated: gap_cli.py")

# Create a simple browser bookmarklet
bookmarklet_code = '''javascript:(function(){
    var selection = window.getSelection().toString();
    if (!selection) {
        alert('Please select some text first');
        return;
    }
    
    var platform = window.location.hostname;
    var chatId = 'browser_' + Date.now();
    var threadId = prompt('Thread ID (optional):') || 'untitled';
    
    var gapContent = `[GAP:START]
From: ${platform} | Thread: ${threadId}
Context: Selected text from ${new Date().toISOString()}
Entities: [AUTO-DETECTED]
[GAP:CONTENT]
${selection}
[GAP:END]`;
    
    // Copy to clipboard
    navigator.clipboard.writeText(gapContent).then(function() {
        alert('GAP-wrapped content copied to clipboard!');
    }, function() {
        // Fallback for older browsers
        var textarea = document.createElement('textarea');
        textarea.value = gapContent;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        alert('GAP-wrapped content copied to clipboard!');
    });
})();'''

print("✅ Browser bookmarklet generated")
print("\nBookmarklet code (drag to bookmarks bar):")
print(bookmarklet_code)