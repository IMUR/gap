"""
Entity detection and management for GAP Protocol
"""

import re
from typing import Dict, List, Optional, Tuple
from .models import GAPEntity


class EntityDetector:
    """Detect and manage entities in content"""

    # Common ambiguous patterns to detect
    AMBIGUOUS_PATTERNS = {
        "the_system": r"\bthe system\b",
        "the_database": r"\bthe database\b",
        "the_code": r"\bthe code\b",
        "the_approach": r"\bthe approach\b",
        "the_solution": r"\bthe solution\b",
        "the_problem": r"\bthe problem\b",
        "the_issue": r"\bthe issue\b",
        "the_error": r"\bthe error\b",
        "the_project": r"\bthe project\b",
        "the_file": r"\bthe file\b",
        "the_function": r"\bthe function\b",
        "the_method": r"\bthe method\b",
        "the_class": r"\bthe class\b",
        "the_module": r"\bthe module\b",
        "the_package": r"\bthe package\b",
        "that_approach": r"\bthat approach\b",
        "that_method": r"\bthat method\b",
        "that_solution": r"\bthat solution\b",
        "this_implementation": r"\bthis implementation\b",
        "this_approach": r"\bthis approach\b",
        "this_solution": r"\bthis solution\b",
    }

    # Technical component patterns
    TECH_PATTERNS = {
        "version_patterns": [
            (r"\b(\w+)\s+v?(\d+\.\d+(?:\.\d+)?)\b", "software_version"),
            (r"\bPython\s+(\d+\.\d+(?:\.\d+)?)\b", "python_version"),
            (r"\bNode(?:\.js)?\s+v?(\d+\.\d+(?:\.\d+)?)\b", "node_version"),
        ],
        "framework_patterns": [
            (r"\b(FastAPI|Django|Flask|Express|React|Vue|Angular)\b", "framework"),
            (r"\b(PostgreSQL|MySQL|MongoDB|Redis|SQLite)\b", "database"),
        ],
        "file_patterns": [
            (r"`([^`]+\.(py|js|ts|jsx|tsx|go|rs|java|cpp|c|h|md))`", "file_reference"),
            (r"([a-zA-Z_]\w*\.(py|js|ts|jsx|tsx|go|rs|java|cpp|c|h|md))\b", "file_reference"),
        ],
    }

    def detect_entities(self, content: str) -> Dict[str, GAPEntity]:
        """Auto-detect entities from content"""
        entities = {}

        # Detect ambiguous references
        for entity_key, pattern in self.AMBIGUOUS_PATTERNS.items():
            if re.search(pattern, content, re.IGNORECASE):
                entities[entity_key] = GAPEntity(
                    type="ambiguous_reference",
                    value="[NEEDS_DEFINITION]"
                )

        # Detect technical components
        for pattern_list in self.TECH_PATTERNS.values():
            for pattern, entity_type in pattern_list:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        value = " ".join(match)
                    else:
                        value = match

                    entity_key = f"{entity_type}_{value.replace(' ', '_').replace('.', '_')}"
                    entities[entity_key] = GAPEntity(
                        type=entity_type,
                        value=value
                    )

        return entities

    def merge_entities(
        self,
        detected: Dict[str, GAPEntity],
        provided: Optional[Dict[str, Dict[str, str]]]
    ) -> Dict[str, GAPEntity]:
        """Merge detected entities with user-provided ones"""
        if not provided:
            return detected

        merged = detected.copy()
        for key, entity_data in provided.items():
            merged[key] = GAPEntity(**entity_data)

        return merged

    def update_entity(
        self,
        entities: Dict[str, GAPEntity],
        key: str,
        value: str,
        entity_type: str = "user_defined"
    ) -> Dict[str, GAPEntity]:
        """Update or add an entity definition"""
        entities[key] = GAPEntity(
            type=entity_type,
            value=value
        )
        return entities

    def find_undefined_entities(self, entities: Dict[str, GAPEntity]) -> List[str]:
        """Find entities that need definition"""
        undefined = []
        for key, entity in entities.items():
            if entity.value == "[NEEDS_DEFINITION]":
                undefined.append(key)
        return undefined

    def suggest_entity_definitions(self, content: str, entities: Dict[str, GAPEntity]) -> Dict[str, str]:
        """Suggest possible definitions for undefined entities based on context"""
        suggestions = {}

        for key in self.find_undefined_entities(entities):
            # Convert key back to natural language
            phrase = key.replace("_", " ")

            # Look for context clues around the phrase
            pattern = rf"({phrase})[^.]*?(?:is|are|was|were|means|refers to|represents)\s+([^.]+)"
            match = re.search(pattern, content, re.IGNORECASE)

            if match:
                suggestions[key] = match.group(2).strip()

        return suggestions


class PronounTransformer:
    """Handle pronoun transformations for different contexts"""

    PRONOUN_MAPS = {
        "assistant": {
            "I": "the AI assistant",
            "me": "the AI assistant",
            "my": "the AI assistant's",
            "mine": "the AI assistant's",
            "myself": "the AI assistant itself",
            "we": "the AI assistants",
            "us": "the AI assistants",
            "our": "the AI assistants'",
            "ours": "the AI assistants'",
        },
        "user": {
            "I": "the user",
            "me": "the user",
            "my": "the user's",
            "mine": "the user's",
            "myself": "the user themselves",
            "we": "the users",
            "us": "the users",
            "our": "the users'",
            "ours": "the users'",
        },
        "system": {
            "I": "the system",
            "me": "the system",
            "my": "the system's",
            "mine": "the system's",
            "myself": "the system itself",
        }
    }

    def generate_pronoun_map(self, content: str, role: str) -> Dict[str, str]:
        """Generate appropriate pronoun mappings based on role"""
        return self.PRONOUN_MAPS.get(role, {}).copy()

    def apply_pronouns(self, content: str, pronoun_map: Dict[str, str]) -> str:
        """Apply pronoun transformations to content"""
        transformed = content

        # Sort by length to avoid partial replacements
        sorted_pronouns = sorted(pronoun_map.items(), key=lambda x: len(x[0]), reverse=True)

        for old_pronoun, new_pronoun in sorted_pronouns:
            # Use word boundaries for accurate replacement
            pattern = r'\b' + re.escape(old_pronoun) + r'\b'
            transformed = re.sub(pattern, new_pronoun, transformed, flags=re.IGNORECASE)

        return transformed
