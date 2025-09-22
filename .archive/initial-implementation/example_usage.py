#!/usr/bin/env python3
"""
GAP Protocol Example Usage
This script demonstrates the basic GAP workflow
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:8000"

def check_service():
    """Check if GAP service is running"""
    try:
        response = requests.get(f"{API_URL}/health")
        return response.status_code == 200
    except:
        return False

def example_workflow():
    """Demonstrate a complete GAP workflow"""

    print("🔄 GAP Protocol Example Workflow")
    print("="*50)

    # Check if service is running
    if not check_service():
        print("❌ GAP service is not running!")
        print("Start it with: python gap_fastapi_service.py")
        return

    print("✅ GAP service is running")

    # Step 1: Simulate content from Claude
    claude_content = """I think the PostgreSQL optimization we discussed earlier is crucial. 
    The indexing approach I suggested should reduce query time significantly. 
    You should also consider the memory configuration changes we talked about."""

    print(f"\n📝 Original Claude content:")
    print(claude_content)

    # Step 2: Wrap with GAP
    wrap_request = {
        "content": claude_content,
        "platform": "claude.ai",
        "chat_id": "claude_optimization_chat",
        "thread_id": "db_performance_project",
        "entities": {
            "the_PostgreSQL_optimization": {
                "type": "technical_task",
                "value": "Query performance optimization for user dashboard"
            },
            "the_indexing_approach": {
                "type": "methodology", 
                "value": "Composite B-tree indexes on (user_id, created_at) columns"
            }
        }
    }

    print("\n🔧 Wrapping with GAP...")
    wrap_response = requests.post(f"{API_URL}/gap/wrap", json=wrap_request)

    if wrap_response.status_code != 200:
        print(f"❌ Failed to wrap: {wrap_response.text}")
        return

    gap_markdown = wrap_response.json()["gap_markdown"]
    print("✅ Content wrapped with GAP")
    print(f"\n📋 GAP Markdown format:")
    print("-" * 40)
    print(gap_markdown)
    print("-" * 40)

    # Step 3: Transform for ChatGPT
    print("\n🔄 Transforming for ChatGPT...")

    transform_request = {
        "gap_markdown": gap_markdown,
        "target_platform": "openai.com",
        "context_additions": {
            "current_project": "E-commerce platform optimization",
            "database_version": "PostgreSQL 14.5 on AWS RDS",
            "urgency": "High - affecting 10K+ daily users"
        }
    }

    transform_response = requests.post(f"{API_URL}/gap/transform", json=transform_request)

    if transform_response.status_code != 200:
        print(f"❌ Failed to transform: {transform_response.text}")
        return

    transformed_content = transform_response.json()["transformed_content"]
    print("✅ Content transformed for ChatGPT")
    print(f"\n🎯 Ready for ChatGPT:")
    print("-" * 40)
    print(transformed_content)
    print("-" * 40)

    print(f"\n✨ GAP Protocol workflow completed!")
    print(f"\n💡 Next steps:")
    print(f"   1. Copy the transformed content above")
    print(f"   2. Paste it into ChatGPT")
    print(f"   3. ChatGPT now has full context from your Claude conversation!")

if __name__ == "__main__":
    example_workflow()
