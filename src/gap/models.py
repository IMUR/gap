"""
GAP Protocol Data Models
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class GAPSource(BaseModel):
    """Source metadata for a GAP message"""
    platform: str = Field(..., description="Platform where message originated (claude.ai, chatgpt, etc.)")
    model: Optional[str] = Field(None, description="AI model used (gpt-4, claude-3, etc.)")
    chat_id: str = Field(..., description="Unique identifier for the chat session")
    timestamp: str = Field(..., description="ISO format timestamp")
    role: str = Field("assistant", description="Role of message sender (user, assistant, system)")


class GAPEntity(BaseModel):
    """Entity definition in GAP context"""
    type: str = Field(..., description="Entity type (ambiguous_reference, technical_component, etc.)")
    value: str = Field(..., description="Entity value or definition")
    defined_in: Optional[str] = Field(None, description="Where this entity was defined")


class GAPContext(BaseModel):
    """Context information for GAP message"""
    thread_id: Optional[str] = Field(None, description="Thread or conversation ID")
    parent_messages: List[str] = Field(default_factory=list, description="IDs of parent messages")
    entities: Dict[str, GAPEntity] = Field(default_factory=dict, description="Entity definitions")


class GAPTransformHints(BaseModel):
    """Hints for transforming content between platforms"""
    maintain_tense: Optional[str] = Field(None, description="Tense to maintain (past, present, future)")
    preserve_perspective: Optional[str] = Field(None, description="Perspective to preserve (first, second, third)")
    pronoun_map: Dict[str, str] = Field(default_factory=dict, description="Pronoun replacements")


class GAPMessageContent(BaseModel):
    """Content and metadata of a GAP message"""
    content: str = Field(..., description="The actual message content")
    source: GAPSource
    context: GAPContext
    transform_hints: GAPTransformHints


class GAPMessage(BaseModel):
    """Complete GAP message with version"""
    gap_version: str = Field("0.1.0", description="GAP protocol version")
    message: GAPMessageContent
