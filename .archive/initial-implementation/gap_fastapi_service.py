
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
