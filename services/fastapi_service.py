"""
FastAPI service for GAP Protocol
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.gap import GAPProtocol, GAPEntity, create_context_graph

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
    include_metadata: bool = True

class EntityUpdateRequest(BaseModel):
    gap_markdown: str
    entity_key: str
    entity_value: str
    entity_type: str = "user_defined"

class LinkChatsRequest(BaseModel):
    chat_ids: List[str]
    relationship: str = "sequential"

# In-memory storage for context graphs (would be a database in production)
context_store = {}
chat_links = {}
message_cache = {}

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

        # Cache the message
        message_id = f"{request.platform}_{request.chat_id}_{wrapped.message.source.timestamp}"
        message_cache[message_id] = wrapped

        # Store in context store by thread
        if request.thread_id:
            if request.thread_id not in context_store:
                context_store[request.thread_id] = []
            context_store[request.thread_id].append(wrapped.model_dump())

        return {
            "status": "success",
            "message_id": message_id,
            "gap_json": wrapped.model_dump(),
            "gap_markdown": gap.to_markdown(wrapped),
            "undefined_entities": gap.get_undefined_entities(wrapped),
            "suggested_definitions": gap.suggest_definitions(wrapped)
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
            request.context_additions,
            request.include_metadata
        )

        # Get undefined entities
        undefined = gap.get_undefined_entities(parsed)

        return {
            "status": "success",
            "transformed_content": transformed_content,
            "original_entities": {k: v.model_dump() for k, v in parsed.message.context.entities.items()},
            "undefined_entities": undefined,
            "target_platform": request.target_platform
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
        updated = gap.update_entity(
            parsed,
            request.entity_key,
            request.entity_value,
            request.entity_type
        )

        # Return updated markdown
        updated_markdown = gap.to_markdown(updated)

        return {
            "status": "success",
            "updated_markdown": updated_markdown,
            "updated_entity": {
                "key": request.entity_key,
                "value": request.entity_value,
                "type": request.entity_type
            },
            "all_entities": {k: v.model_dump() for k, v in updated.message.context.entities.items()}
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/gap/link-chats")
async def link_chats(request: LinkChatsRequest):
    """Create a relationship between chat sessions"""
    try:
        link_id = f"link_{len(chat_links)}"
        chat_links[link_id] = {
            "chat_ids": request.chat_ids,
            "relationship": request.relationship,
            "created_at": datetime.now().isoformat()
        }

        return {
            "status": "success",
            "link_id": link_id,
            "linked_chats": request.chat_ids,
            "relationship": request.relationship
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/gap/context/{thread_id}")
async def get_thread_context(thread_id: str):
    """Get all context for a thread"""
    try:
        thread_context = context_store.get(thread_id, [])

        # Create a context graph if we have messages
        if thread_context:
            from src.gap.models import GAPMessage
            messages = [GAPMessage(**msg_data) for msg_data in thread_context]
            graph = create_context_graph(messages)
        else:
            graph = None

        return {
            "status": "success",
            "thread_id": thread_id,
            "message_count": len(thread_context),
            "context": thread_context,
            "context_graph": graph
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/gap/platforms")
async def get_supported_platforms():
    """Get list of supported platforms for transformation"""
    gap = GAPProtocol()
    return {
        "status": "success",
        "platforms": gap.platform_transformer.platforms
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "cached_messages": len(message_cache),
        "active_threads": len(context_store),
        "chat_links": len(chat_links)
    }

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
            "get_context": "GET /gap/context/{thread_id} - Get thread context",
            "platforms": "GET /gap/platforms - Get supported platforms",
            "health": "GET /health - Service health check"
        }
    }

def start():
    """Entry point for UV script runner"""
    import uvicorn
    uvicorn.run(
        "services.fastapi_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    start()
