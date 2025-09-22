#!/usr/bin/env python3
import argparse
import json
import sys
import requests
from pathlib import Path

class GAPCli:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url

    def wrap(self, content, platform, chat_id, **kwargs):
        """Wrap content with GAP metadata"""
        data = {
            "content": content,
            "platform": platform,
            "chat_id": chat_id,
            **kwargs
        }

        response = requests.post(f"{self.api_url}/gap/wrap", json=data)
        if response.status_code == 200:
            result = response.json()
            return result["gap_markdown"]
        else:
            raise Exception(f"API Error: {response.text}")

    def transform(self, gap_markdown, target_platform, context_additions=None):
        """Transform GAP content for target platform"""
        data = {
            "gap_markdown": gap_markdown,
            "target_platform": target_platform,
            "context_additions": context_additions
        }

        response = requests.post(f"{self.api_url}/gap/transform", json=data)
        if response.status_code == 200:
            result = response.json()
            return result["transformed_content"]
        else:
            raise Exception(f"API Error: {response.text}")

    def update_entity(self, gap_markdown, entity_key, entity_value, entity_type="user_defined"):
        """Update an entity in GAP content"""
        data = {
            "gap_markdown": gap_markdown,
            "entity_key": entity_key,
            "entity_value": entity_value,
            "entity_type": entity_type
        }

        response = requests.post(f"{self.api_url}/gap/update-entity", json=data)
        if response.status_code == 200:
            result = response.json()
            return result["updated_markdown"]
        else:
            raise Exception(f"API Error: {response.text}")

def main():
    parser = argparse.ArgumentParser(description="GAP Protocol CLI Tool")
    parser.add_argument("--api-url", default="http://localhost:8000", help="GAP API URL")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Wrap command
    wrap_parser = subparsers.add_parser("wrap", help="Wrap content with GAP metadata")
    wrap_parser.add_argument("content", help="Content to wrap")
    wrap_parser.add_argument("--platform", required=True, help="Source platform")
    wrap_parser.add_argument("--chat-id", required=True, help="Chat identifier")
    wrap_parser.add_argument("--thread-id", help="Thread identifier")
    wrap_parser.add_argument("--role", default="assistant", help="Message role")
    wrap_parser.add_argument("--output", "-o", help="Output file")

    # Transform command
    transform_parser = subparsers.add_parser("transform", help="Transform GAP content")
    transform_parser.add_argument("input_file", help="GAP markdown file")
    transform_parser.add_argument("--target", required=True, help="Target platform")
    transform_parser.add_argument("--context", help="Additional context (JSON)")
    transform_parser.add_argument("--output", "-o", help="Output file")

    # Update entity command
    entity_parser = subparsers.add_parser("update-entity", help="Update entity definition")
    entity_parser.add_argument("input_file", help="GAP markdown file")
    entity_parser.add_argument("--key", required=True, help="Entity key")
    entity_parser.add_argument("--value", required=True, help="Entity value")
    entity_parser.add_argument("--type", default="user_defined", help="Entity type")
    entity_parser.add_argument("--output", "-o", help="Output file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = GAPCli(args.api_url)

    try:
        if args.command == "wrap":
            result = cli.wrap(
                content=args.content,
                platform=args.platform,
                chat_id=args.chat_id,
                thread_id=args.thread_id,
                role=args.role
            )

            if args.output:
                with open(args.output, "w") as f:
                    f.write(result)
                print(f"GAP wrapped content saved to {args.output}")
            else:
                print(result)

        elif args.command == "transform":
            with open(args.input_file, "r") as f:
                gap_markdown = f.read()

            context_additions = None
            if args.context:
                context_additions = json.loads(args.context)

            result = cli.transform(gap_markdown, args.target, context_additions)

            if args.output:
                with open(args.output, "w") as f:
                    f.write(result)
                print(f"Transformed content saved to {args.output}")
            else:
                print(result)

        elif args.command == "update-entity":
            with open(args.input_file, "r") as f:
                gap_markdown = f.read()

            result = cli.update_entity(gap_markdown, args.key, args.value, args.type)

            if args.output:
                with open(args.output, "w") as f:
                    f.write(result)
                print(f"Updated GAP content saved to {args.output}")
            else:
                print(result)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
