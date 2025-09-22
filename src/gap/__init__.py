"""
GAP (Global Addressment Protocol) - Core Package

A protocol for preserving context and continuity across AI conversations.
"""

from .protocol import GAPProtocol, create_context_graph
from .models import (
    GAPMessage,
    GAPMessageContent,
    GAPSource,
    GAPContext,
    GAPEntity,
    GAPTransformHints,
)
from .entities import EntityDetector, PronounTransformer
from .transformers import PlatformTransformer, ContextMerger

__version__ = "0.1.0"
__all__ = [
    "GAPProtocol",
    "GAPMessage",
    "GAPMessageContent",
    "GAPSource",
    "GAPContext",
    "GAPEntity",
    "GAPTransformHints",
    "EntityDetector",
    "PronounTransformer",
    "PlatformTransformer",
    "ContextMerger",
    "create_context_graph",
]
