#!/usr/bin/env python3
"""
Basic GAP Protocol Usage Examples
"""

from src.gap import GAPProtocol, create_context_graph


def example_basic_wrapping():
    """Basic example of wrapping content with GAP metadata"""
    print("=" * 50)
    print("EXAMPLE 1: Basic Content Wrapping")
    print("=" * 50)

    # Initialize GAP Protocol
    gap = GAPProtocol()

    # Content with ambiguous references
    content = """
    I've analyzed the system and found several issues.
    The database is running slow, and the approach we discussed
    yesterday needs refinement. Let me know if you want to proceed
    with this implementation.
    """

    # Wrap the content
    wrapped = gap.wrap_message(
        content=content,
        platform="claude.ai",
        chat_id="analysis_session_123",
        role="assistant",
        thread_id="system_optimization",
        entities={
            "the_system": {
                "type": "technical_component",
                "value": "E-commerce platform backend"
            },
            "the_database": {
                "type": "database",
                "value": "PostgreSQL 14.5 with 100GB data"
            },
            "the_approach": {
                "type": "methodology",
                "value": "Incremental index optimization strategy"
            }
        }
    )

    # Convert to markdown
    markdown = gap.to_markdown(wrapped)
    print("\nWrapped content (Markdown):")
    print(markdown)

    # Show undefined entities
    undefined = gap.get_undefined_entities(wrapped)
    if undefined:
        print("\nEntities needing definition:")
        for entity in undefined:
            print(f"  - {entity}")

    return wrapped


def example_platform_transformation():
    """Example of transforming content for different platforms"""
    print("\n" + "=" * 50)
    print("EXAMPLE 2: Platform Transformation")
    print("=" * 50)

    gap = GAPProtocol()

    # Create a wrapped message
    wrapped = gap.wrap_message(
        content="I analyzed the code and found that the system needs optimization.",
        platform="claude.ai",
        chat_id="code_review",
        role="assistant",
        entities={
            "the_code": {
                "type": "codebase",
                "value": "Python FastAPI application"
            },
            "the_system": {
                "type": "infrastructure",
                "value": "Docker Kubernetes deployment"
            }
        }
    )

    # Transform for different platforms
    platforms = ["chatgpt", "gemini", "copilot"]

    for platform in platforms:
        print(f"\n--- Transformed for {platform} ---")
        transformed = gap.transform_for_platform(
            wrapped,
            target_platform=platform,
            context_additions={
                "Previous Discussion": "Performance optimization strategies",
                "Project": "E-commerce Platform v2.0"
            }
        )
        print(transformed[:200] + "..." if len(transformed) > 200 else transformed)


def example_context_graph():
    """Example of building a context graph from multiple messages"""
    print("\n" + "=" * 50)
    print("EXAMPLE 3: Context Graph Creation")
    print("=" * 50)

    gap = GAPProtocol()

    # Create multiple related messages
    messages = []

    # Message 1: Initial problem statement
    msg1 = gap.wrap_message(
        content="The system is experiencing high latency issues.",
        platform="claude.ai",
        chat_id="session_1",
        role="user",
        thread_id="performance_investigation",
        entities={
            "the_system": {
                "type": "service",
                "value": "Order Processing Service"
            }
        }
    )
    messages.append(msg1)

    # Message 2: Analysis
    msg2 = gap.wrap_message(
        content="I've identified the database queries as the bottleneck.",
        platform="claude.ai",
        chat_id="session_1",
        role="assistant",
        thread_id="performance_investigation",
        entities={
            "the_database": {
                "type": "database",
                "value": "PostgreSQL order_db"
            }
        }
    )
    messages.append(msg2)

    # Message 3: Solution
    msg3 = gap.wrap_message(
        content="The solution involves adding indexes to improve query performance.",
        platform="chatgpt",
        chat_id="session_2",
        role="assistant",
        thread_id="performance_investigation",
        entities={
            "the_solution": {
                "type": "optimization",
                "value": "Composite indexes on frequently queried columns"
            }
        }
    )
    messages.append(msg3)

    # Create context graph
    graph = create_context_graph(messages)

    print("\nContext Graph Summary:")
    print(f"  Nodes: {len(graph['nodes'])}")
    print(f"  Edges: {len(graph['edges'])}")
    print(f"  Entity Definitions: {len(graph['entity_definitions'])}")

    print("\nDefined Entities:")
    for key, entity in graph['entity_definitions'].items():
        print(f"  {key}: {entity['value']}")

    print("\nTimeline:")
    for i, node_id in enumerate(graph['timeline'], 1):
        node = graph['nodes'][node_id]
        print(f"  {i}. [{node['platform']}] {node['role']}: {node['content']}")


def example_entity_updates():
    """Example of updating entity definitions"""
    print("\n" + "=" * 50)
    print("EXAMPLE 4: Updating Entity Definitions")
    print("=" * 50)

    gap = GAPProtocol()

    # Create a message with undefined entities
    wrapped = gap.wrap_message(
        content="The system needs to be updated to handle the new requirements.",
        platform="gemini",
        chat_id="planning_session",
        role="assistant"
    )

    print("Initial undefined entities:")
    undefined = gap.get_undefined_entities(wrapped)
    for entity in undefined:
        print(f"  - {entity}")

    # Update entity definitions
    wrapped = gap.update_entity(
        wrapped,
        entity_key="the_system",
        entity_value="User Authentication Service",
        entity_type="microservice"
    )

    wrapped = gap.update_entity(
        wrapped,
        entity_key="the_new_requirements",
        entity_value="OAuth 2.0 and SAML support",
        entity_type="feature_request"
    )

    print("\nAfter updates:")
    markdown = gap.to_markdown(wrapped)
    print(markdown)


def example_markdown_parsing():
    """Example of parsing GAP markdown"""
    print("\n" + "=" * 50)
    print("EXAMPLE 5: Parsing GAP Markdown")
    print("=" * 50)

    gap = GAPProtocol()

    # Sample GAP markdown
    markdown = """[GAP:START]
From: claude.ai | Thread: database_optimization
Context: assistant message from 2024-01-15T10:30:00
Entities: "the_system" = PostgreSQL cluster, "the_approach" = Index optimization
[GAP:CONTENT]
The system performance improved with the approach we implemented.
[GAP:END]"""

    print("Input markdown:")
    print(markdown)

    # Parse the markdown
    parsed = gap.from_markdown(markdown)

    if parsed:
        print("\nParsed successfully!")
        print(f"Platform: {parsed.message.source.platform}")
        print(f"Thread: {parsed.message.context.thread_id}")
        print(f"Content: {parsed.message.content}")
        print("Entities:")
        for key, entity in parsed.message.context.entities.items():
            print(f"  {key}: {entity.value}")
    else:
        print("\nFailed to parse markdown")


if __name__ == "__main__":
    # Run all examples
    example_basic_wrapping()
    example_platform_transformation()
    example_context_graph()
    example_entity_updates()
    example_markdown_parsing()

    print("\n" + "=" * 50)
    print("All examples completed successfully!")
    print("=" * 50)
