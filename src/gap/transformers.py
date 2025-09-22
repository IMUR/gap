"""
Platform-specific transformers for GAP Protocol
"""

import re
from typing import Dict, Optional
from .models import GAPMessage


class PlatformTransformer:
    """Transform GAP messages for different platforms"""

    PLATFORM_CONFIGS = {
        "claude.ai": {
            "prefix": "[Context from GAP-wrapped message]",
            "entity_format": "• {key}: {value}",
            "supports_markdown": True,
        },
        "chatgpt": {
            "prefix": "# Context from another AI session",
            "entity_format": "- {key}: {value}",
            "supports_markdown": True,
        },
        "gemini": {
            "prefix": "**Previous conversation context:**",
            "entity_format": "* {key}: {value}",
            "supports_markdown": True,
        },
        "copilot": {
            "prefix": "// Context from GAP protocol",
            "entity_format": "// {key}: {value}",
            "supports_markdown": False,
        },
        "perplexity": {
            "prefix": "Context Information:",
            "entity_format": "• {key}: {value}",
            "supports_markdown": True,
        },
        "generic": {
            "prefix": "=== Context ===",
            "entity_format": "{key}: {value}",
            "supports_markdown": False,
        }
    }

    def __init__(self):
        self.platforms = list(self.PLATFORM_CONFIGS.keys())

    def transform_for_platform(
        self,
        gap_message: GAPMessage,
        target_platform: str,
        context_additions: Optional[Dict[str, str]] = None,
        include_metadata: bool = True
    ) -> str:
        """Transform GAP message content for target platform"""

        # Get platform config or use generic
        config = self.PLATFORM_CONFIGS.get(
            target_platform.lower(),
            self.PLATFORM_CONFIGS["generic"]
        )

        content = gap_message.message.content

        # Apply pronoun transformations
        for old_pronoun, new_pronoun in gap_message.message.transform_hints.pronoun_map.items():
            pattern = r'\b' + re.escape(old_pronoun) + r'\b'
            content = re.sub(pattern, new_pronoun, content, flags=re.IGNORECASE)

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

        # Build the final message
        parts = []

        if include_metadata:
            # Add platform-specific prefix
            parts.append(config["prefix"])
            parts.append("")

            # Add entity definitions if any are defined
            defined_entities = {
                k: v for k, v in gap_message.message.context.entities.items()
                if v.value != "[NEEDS_DEFINITION]"
            }

            if defined_entities:
                parts.append("**Entity Definitions:**")
                for key, entity in defined_entities.items():
                    readable_key = key.replace("_", " ").title()
                    parts.append(config["entity_format"].format(
                        key=readable_key,
                        value=entity.value
                    ))
                parts.append("")

            # Add context additions if provided
            if context_additions:
                parts.append("**Additional Context:**")
                for key, value in context_additions.items():
                    parts.append(config["entity_format"].format(
                        key=key,
                        value=value
                    ))
                parts.append("")

            # Add source information
            parts.append(f"*Source: {gap_message.message.source.platform} | "
                        f"Thread: {gap_message.message.context.thread_id or 'N/A'}*")
            parts.append("")
            parts.append("---")
            parts.append("")

        # Add the transformed content
        parts.append(content)

        return "\n".join(parts)

    def transform_for_clipboard(
        self,
        gap_message: GAPMessage,
        format: str = "markdown"
    ) -> str:
        """Transform GAP message for clipboard copying"""

        if format == "markdown":
            return self._to_markdown(gap_message)
        elif format == "plain":
            return self._to_plain_text(gap_message)
        elif format == "json":
            return gap_message.model_dump_json(indent=2)
        else:
            return gap_message.message.content

    def _to_markdown(self, gap_message: GAPMessage) -> str:
        """Convert to markdown format for clipboard"""
        msg = gap_message.message

        # Build entity string
        entities_str = ""
        for key, entity in msg.context.entities.items():
            if entity.value != "[NEEDS_DEFINITION]":
                entities_str += f'"{key}" = {entity.value}, '
        entities_str = entities_str.rstrip(", ") or "None"

        return f"""[GAP:START]
From: {msg.source.platform} | Thread: {msg.context.thread_id or "Unknown"}
Context: {msg.source.role} message from {msg.source.timestamp}
Entities: {entities_str}
[GAP:CONTENT]
{msg.content}
[GAP:END]"""

    def _to_plain_text(self, gap_message: GAPMessage) -> str:
        """Convert to plain text format"""
        msg = gap_message.message

        parts = [
            f"=== GAP Message ===",
            f"From: {msg.source.platform}",
            f"Role: {msg.source.role}",
            f"Thread: {msg.context.thread_id or 'N/A'}",
            f"Time: {msg.source.timestamp}",
            "",
            "Content:",
            msg.content,
        ]

        if msg.context.entities:
            parts.extend(["", "Entities:"])
            for key, entity in msg.context.entities.items():
                if entity.value != "[NEEDS_DEFINITION]":
                    parts.append(f"  {key}: {entity.value}")

        return "\n".join(parts)


class ContextMerger:
    """Merge context from multiple GAP messages"""

    def merge_contexts(self, messages: list[GAPMessage]) -> Dict[str, any]:
        """Merge contexts from multiple messages"""
        merged = {
            "entities": {},
            "threads": set(),
            "platforms": set(),
            "timeline": []
        }

        for msg in messages:
            # Merge entities (later definitions override earlier)
            for key, entity in msg.message.context.entities.items():
                if entity.value != "[NEEDS_DEFINITION]":
                    merged["entities"][key] = entity

            # Collect threads
            if msg.message.context.thread_id:
                merged["threads"].add(msg.message.context.thread_id)

            # Collect platforms
            merged["platforms"].add(msg.message.source.platform)

            # Build timeline
            merged["timeline"].append({
                "timestamp": msg.message.source.timestamp,
                "platform": msg.message.source.platform,
                "role": msg.message.source.role,
                "summary": msg.message.content[:100] + "..."
            })

        # Convert sets to lists for JSON serialization
        merged["threads"] = list(merged["threads"])
        merged["platforms"] = list(merged["platforms"])

        return merged
