"""
GAP (Global Addressment Protocol) Core Implementation
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from .models import (
    GAPSource,
    GAPContext,
    GAPTransformHints,
    GAPMessageContent,
    GAPMessage
)
from .entities import EntityDetector, PronounTransformer
from .transformers import PlatformTransformer


class GAPProtocol:
    """Core GAP Protocol implementation"""

    def __init__(self, version: str = "0.1.0"):
        self.version = version
        self.entity_detector = EntityDetector()
        self.pronoun_transformer = PronounTransformer()
        self.platform_transformer = PlatformTransformer()

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
        detected_entities = self.entity_detector.detect_entities(content)

        # Merge with provided entities
        merged_entities = self.entity_detector.merge_entities(detected_entities, entities)

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
            entities=merged_entities
        )

        # Create transform hints
        pronoun_map = self.pronoun_transformer.generate_pronoun_map(content, role)
        transform_hints = GAPTransformHints(pronoun_map=pronoun_map)

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

    def to_markdown(self, gap_message: GAPMessage) -> str:
        """Convert GAP message to human-readable markdown format"""
        return self.platform_transformer.transform_for_clipboard(gap_message, format="markdown")

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
            context_match = re.search(r'Context: (\w+) message from ([^\n]+)', markdown)
            entities_match = re.search(r'Entities: ([^\n]+)', markdown)

            platform = from_match.group(1).strip() if from_match else "unknown"
            thread_id = from_match.group(2).strip() if from_match else None
            role = context_match.group(1) if context_match else "assistant"

            # Parse entities
            entities = {}
            if entities_match:
                entities_str = entities_match.group(1)
                if entities_str != "None":
                    # Parse entity pairs
                    entity_pairs = re.findall(r'"([^"]+)"\s*=\s*([^,]+)', entities_str)
                    for key, value in entity_pairs:
                        entities[key.strip()] = {
                            "type": "parsed",
                            "value": value.strip()
                        }

            return self.wrap_message(
                content=content,
                platform=platform,
                chat_id="parsed_from_markdown",
                role=role,
                thread_id=thread_id if thread_id != "Unknown" else None,
                entities=entities
            )

        except Exception as e:
            print(f"Error parsing markdown: {e}")
            return None

    def transform_for_platform(
        self,
        gap_message: GAPMessage,
        target_platform: str,
        context_additions: Optional[Dict[str, str]] = None,
        include_metadata: bool = True
    ) -> str:
        """Transform GAP message content for target platform"""
        return self.platform_transformer.transform_for_platform(
            gap_message,
            target_platform,
            context_additions,
            include_metadata
        )

    def update_entity(
        self,
        gap_message: GAPMessage,
        entity_key: str,
        entity_value: str,
        entity_type: str = "user_defined"
    ) -> GAPMessage:
        """Update an entity definition in a GAP message"""
        gap_message.message.context.entities = self.entity_detector.update_entity(
            gap_message.message.context.entities,
            entity_key,
            entity_value,
            entity_type
        )
        return gap_message

    def get_undefined_entities(self, gap_message: GAPMessage) -> List[str]:
        """Get list of undefined entities in message"""
        return self.entity_detector.find_undefined_entities(
            gap_message.message.context.entities
        )

    def suggest_definitions(self, gap_message: GAPMessage) -> Dict[str, str]:
        """Suggest entity definitions based on context"""
        return self.entity_detector.suggest_entity_definitions(
            gap_message.message.content,
            gap_message.message.context.entities
        )


def create_context_graph(messages: List[GAPMessage]) -> Dict[str, Any]:
    """Create a context graph from multiple GAP messages"""
    graph = {
        "nodes": {},
        "edges": [],
        "entity_definitions": {},
        "timeline": []
    }

    for msg in messages:
        # Add node for this message
        node_id = f"{msg.message.source.platform}_{msg.message.source.chat_id}_{msg.message.source.timestamp}"
        graph["nodes"][node_id] = {
            "platform": msg.message.source.platform,
            "content": msg.message.content[:100] + "...",
            "timestamp": msg.message.source.timestamp,
            "role": msg.message.source.role
        }

        # Add to timeline
        graph["timeline"].append(node_id)

        # Merge entity definitions
        for entity_key, entity in msg.message.context.entities.items():
            if entity.value != "[NEEDS_DEFINITION]":
                graph["entity_definitions"][entity_key] = {
                    "value": entity.value,
                    "type": entity.type,
                    "defined_in": node_id
                }

        # Add edges based on thread_id
        if msg.message.context.thread_id:
            # Find other nodes in same thread
            for existing_id, existing_node in graph["nodes"].items():
                if existing_id != node_id:
                    # Simple connection based on thread
                    graph["edges"].append({
                        "from": existing_id,
                        "to": node_id,
                        "type": "thread_connection"
                    })

    return graph
