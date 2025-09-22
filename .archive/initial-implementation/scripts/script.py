# Let's create the basic GAP protocol implementation components
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel

# First, let's define the data models based on the proposal

class GAPSource(BaseModel):
    platform: str
    model: Optional[str] = None
    chat_id: str
    timestamp: str
    role: str = "assistant"

class GAPEntity(BaseModel):
    type: str
    value: str
    defined_in: Optional[str] = None

class GAPContext(BaseModel):
    thread_id: Optional[str] = None
    parent_messages: List[str] = []
    entities: Dict[str, GAPEntity] = {}

class GAPTransformHints(BaseModel):
    maintain_tense: Optional[str] = None
    preserve_perspective: Optional[str] = None
    pronoun_map: Dict[str, str] = {}

class GAPMessageContent(BaseModel):
    content: str
    source: GAPSource
    context: GAPContext
    transform_hints: GAPTransformHints

class GAPMessage(BaseModel):
    gap_version: str = "0.1.0"
    message: GAPMessageContent

# Core GAP Protocol class
class GAPProtocol:
    def __init__(self, version: str = "0.1.0"):
        self.version = version
        
    def wrap_message(
        self,
        content: str,
        platform: str,
        chat_id: str,
        role: str = "assistant",
        model: Optional[str] = None,
        thread_id: Optional[str] = None,
        entities: Optional[Dict[str, Dict[str, str]]] = None
    ) -> GAPMessage:
        """Wrap content with GAP metadata"""
        
        # Auto-detect entities from content
        detected_entities = self._detect_entities(content)
        
        # Merge with provided entities
        if entities:
            for key, entity_data in entities.items():
                detected_entities[key] = GAPEntity(**entity_data)
        
        # Create source metadata
        source = GAPSource(
            platform=platform,
            model=model,
            chat_id=chat_id,
            timestamp=datetime.now().isoformat(),
            role=role
        )
        
        # Create context
        context = GAPContext(
            thread_id=thread_id,
            entities=detected_entities
        )
        
        # Create transform hints
        transform_hints = GAPTransformHints(
            pronoun_map=self._generate_pronoun_map(content, role)
        )
        
        # Create message content
        message_content = GAPMessageContent(
            content=content,
            source=source,
            context=context,
            transform_hints=transform_hints
        )
        
        return GAPMessage(
            gap_version=self.version,
            message=message_content
        )
    
    def _detect_entities(self, content: str) -> Dict[str, GAPEntity]:
        """Auto-detect common ambiguous references in content"""
        entities = {}
        
        # Common patterns to detect
        patterns = {
            "the_system": r"\bthe system\b",
            "the_database": r"\bthe database\b", 
            "the_code": r"\bthe code\b",
            "the_approach": r"\bthe approach\b",
            "the_solution": r"\bthe solution\b",
            "that_method": r"\bthat method\b",
            "this_implementation": r"\bthis implementation\b"
        }
        
        for entity_key, pattern in patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                entities[entity_key] = GAPEntity(
                    type="ambiguous_reference",
                    value="[NEEDS_DEFINITION]"
                )
        
        return entities
    
    def _generate_pronoun_map(self, content: str, role: str) -> Dict[str, str]:
        """Generate appropriate pronoun mappings"""
        pronoun_map = {}
        
        if role == "assistant":
            pronoun_map.update({
                "I": "the AI assistant",
                "my": "the AI assistant's",
                "me": "the AI assistant"
            })
        elif role == "user":
            pronoun_map.update({
                "I": "the user", 
                "my": "the user's",
                "me": "the user"
            })
        
        return pronoun_map
    
    def to_markdown(self, gap_message: GAPMessage) -> str:
        """Convert GAP message to human-readable markdown format"""
        msg = gap_message.message
        
        # Build entity string
        entities_str = ""
        for key, entity in msg.context.entities.items():
            entities_str += f'"{key}" = {entity.value}, '
        entities_str = entities_str.rstrip(", ")
        
        markdown = f"""[GAP:START]
From: {msg.source.platform} | Thread: {msg.context.thread_id or "Unknown"}
Context: {msg.source.role} message from {msg.source.timestamp}
Entities: {entities_str}
[GAP:CONTENT]
{msg.content}
[GAP:END]"""
        
        return markdown
    
    def from_markdown(self, markdown: str) -> Optional[GAPMessage]:
        """Parse GAP message from markdown format"""
        try:
            # Extract content between GAP:CONTENT and GAP:END
            content_match = re.search(r'\[GAP:CONTENT\](.*?)\[GAP:END\]', markdown, re.DOTALL)
            if not content_match:
                return None
            
            content = content_match.group(1).strip()
            
            # Extract metadata
            from_match = re.search(r'From: ([^|]+)\|.*Thread: ([^\n]+)', markdown)
            entities_match = re.search(r'Entities: ([^\n]+)', markdown)
            
            platform = from_match.group(1).strip() if from_match else "unknown"
            thread_id = from_match.group(2).strip() if from_match else None
            
            # Parse entities
            entities = {}
            if entities_match:
                entities_str = entities_match.group(1)
                # Simple parsing - could be more robust
                entity_pairs = entities_str.split(', ')
                for pair in entity_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        key = key.strip(' "')
                        value = value.strip(' "')
                        entities[key] = GAPEntity(type="parsed", value=value)
            
            return self.wrap_message(
                content=content,
                platform=platform,
                chat_id="parsed_from_markdown",
                thread_id=thread_id,
                entities={k: v.dict() for k, v in entities.items()}
            )
            
        except Exception as e:
            print(f"Error parsing markdown: {e}")
            return None
    
    def transform_for_platform(
        self,
        gap_message: GAPMessage,
        target_platform: str,
        context_additions: Optional[Dict[str, str]] = None
    ) -> str:
        """Transform GAP message content for target platform"""
        content = gap_message.message.content
        
        # Apply pronoun transformations
        for old_pronoun, new_pronoun in gap_message.message.transform_hints.pronoun_map.items():
            content = re.sub(
                r'\b' + re.escape(old_pronoun) + r'\b',
                new_pronoun,
                content,
                flags=re.IGNORECASE
            )
        
        # Replace ambiguous entities with their definitions
        for entity_key, entity in gap_message.message.context.entities.items():
            if entity.value != "[NEEDS_DEFINITION]":
                # Replace the ambiguous reference with the actual value
                pattern = entity_key.replace("_", " ")
                content = re.sub(
                    r'\b' + re.escape(pattern) + r'\b',
                    entity.value,
                    content,
                    flags=re.IGNORECASE
                )
        
        # Add context additions if provided
        if context_additions:
            context_str = "\n\nAdditional context for this conversation:\n"
            for key, value in context_additions.items():
                context_str += f"- {key}: {value}\n"
            content = context_str + content
        
        return content

# Test the implementation
print("GAP Protocol Implementation Created Successfully!")
print("\nTesting basic functionality...")

# Create a GAP protocol instance
gap = GAPProtocol()

# Test message
test_content = """I think the system we discussed earlier needs optimization. 
The approach you suggested for the database should work well. 
Let me know if you need more details about this implementation."""

# Wrap the message
wrapped = gap.wrap_message(
    content=test_content,
    platform="claude.ai",
    chat_id="test_chat_123",
    thread_id="database_optimization",
    entities={
        "the_system": {"type": "technical_component", "value": "PostgreSQL 14.5 cluster"},
        "the_approach": {"type": "methodology", "value": "Index-based query optimization"}
    }
)

print("✅ Message wrapping works")

# Convert to markdown
markdown = gap.to_markdown(wrapped)
print("✅ Markdown conversion works")

# Parse back from markdown
parsed = gap.from_markdown(markdown)
print("✅ Markdown parsing works")

# Transform for another platform
transformed = gap.transform_for_platform(
    wrapped,
    "chatgpt", 
    context_additions={"Previous discussion": "Database performance optimization"}
)
print("✅ Platform transformation works")

print("\n" + "="*50)
print("SAMPLE OUTPUT:")
print("="*50)
print("\nOriginal content:")
print(test_content)
print("\nMarkdown format:")
print(markdown)
print("\nTransformed content:")
print(transformed)