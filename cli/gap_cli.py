#!/usr/bin/env python3
"""
GAP Protocol CLI Tool

Provides command-line interface for GAP Protocol operations.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

console = Console()

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

# Check if we should use API or direct implementation
USE_API = os.getenv("GAP_USE_API", "false").lower() == "true"

if USE_API:
    import requests

    class GAPCliAPI:
        """API-based CLI implementation"""

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
else:
    from src.gap import GAPProtocol

    class GAPCliDirect:
        """Direct implementation CLI (no API needed)"""

        def __init__(self):
            self.gap = GAPProtocol()

        def wrap(self, content, platform, chat_id, **kwargs):
            """Wrap content with GAP metadata"""
            wrapped = self.gap.wrap_message(
                content=content,
                platform=platform,
                chat_id=chat_id,
                **kwargs
            )
            return self.gap.to_markdown(wrapped)

        def transform(self, gap_markdown, target_platform, context_additions=None):
            """Transform GAP content for target platform"""
            parsed = self.gap.from_markdown(gap_markdown)
            if not parsed:
                raise ValueError("Invalid GAP markdown format")

            return self.gap.transform_for_platform(
                parsed,
                target_platform,
                context_additions
            )

        def update_entity(self, gap_markdown, entity_key, entity_value, entity_type="user_defined"):
            """Update an entity in GAP content"""
            parsed = self.gap.from_markdown(gap_markdown)
            if not parsed:
                raise ValueError("Invalid GAP markdown format")

            updated = self.gap.update_entity(
                parsed,
                entity_key,
                entity_value,
                entity_type
            )
            return self.gap.to_markdown(updated)


def read_from_stdin():
    """Read content from stdin"""
    if sys.stdin.isatty():
        return None
    return sys.stdin.read()


def read_from_clipboard():
    """Read content from clipboard"""
    if not CLIPBOARD_AVAILABLE:
        console.print("[red]Clipboard support not available. Install pyperclip.[/red]")
        return None
    try:
        return pyperclip.paste()
    except Exception as e:
        console.print(f"[red]Failed to read from clipboard: {e}[/red]")
        return None


def write_to_clipboard(content):
    """Write content to clipboard"""
    if not CLIPBOARD_AVAILABLE:
        console.print("[yellow]Clipboard support not available. Install pyperclip.[/yellow]")
        return False
    try:
        pyperclip.copy(content)
        return True
    except Exception as e:
        console.print(f"[red]Failed to write to clipboard: {e}[/red]")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="GAP Protocol CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Wrap content from a file
  gap-cli wrap "Content to wrap" --platform claude.ai --chat-id chat123

  # Wrap from clipboard
  gap-cli wrap --clipboard --platform chatgpt --chat-id session456

  # Transform for another platform
  gap-cli transform input.gap --target gemini

  # Update entity definition
  gap-cli update-entity input.gap --key the_system --value "PostgreSQL 14.5"

  # Pipe content through GAP
  echo "Some content" | gap-cli wrap --platform claude.ai --chat-id test --stdin
        """
    )

    # Global options
    parser.add_argument("--api-url", default="http://localhost:8000", help="GAP API URL (if using API mode)")
    parser.add_argument("--use-api", action="store_true", help="Use API instead of direct implementation")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-essential output")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Wrap command
    wrap_parser = subparsers.add_parser("wrap", help="Wrap content with GAP metadata")
    wrap_parser.add_argument("content", nargs="?", help="Content to wrap (or use --stdin/--clipboard)")
    wrap_parser.add_argument("--platform", "-p", required=True, help="Source platform")
    wrap_parser.add_argument("--chat-id", "-c", required=True, help="Chat identifier")
    wrap_parser.add_argument("--thread-id", "-t", help="Thread identifier")
    wrap_parser.add_argument("--role", "-r", default="assistant", choices=["assistant", "user", "system"], help="Message role")
    wrap_parser.add_argument("--model", "-m", help="Model name")
    wrap_parser.add_argument("--stdin", action="store_true", help="Read content from stdin")
    wrap_parser.add_argument("--clipboard", action="store_true", help="Read content from clipboard")
    wrap_parser.add_argument("--output", "-o", help="Output file")
    wrap_parser.add_argument("--copy", action="store_true", help="Copy result to clipboard")

    # Transform command
    transform_parser = subparsers.add_parser("transform", help="Transform GAP content")
    transform_parser.add_argument("input_file", nargs="?", help="GAP markdown file (or use --stdin/--clipboard)")
    transform_parser.add_argument("--target", "-t", required=True, help="Target platform")
    transform_parser.add_argument("--context", help="Additional context (JSON)")
    transform_parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    transform_parser.add_argument("--clipboard", action="store_true", help="Read from clipboard")
    transform_parser.add_argument("--output", "-o", help="Output file")
    transform_parser.add_argument("--copy", action="store_true", help="Copy result to clipboard")
    transform_parser.add_argument("--no-metadata", action="store_true", help="Exclude metadata from transformation")

    # Update entity command
    entity_parser = subparsers.add_parser("update-entity", help="Update entity definition")
    entity_parser.add_argument("input_file", nargs="?", help="GAP markdown file (or use --stdin/--clipboard)")
    entity_parser.add_argument("--key", "-k", required=True, help="Entity key")
    entity_parser.add_argument("--value", "-v", required=True, help="Entity value")
    entity_parser.add_argument("--type", default="user_defined", help="Entity type")
    entity_parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    entity_parser.add_argument("--clipboard", action="store_true", help="Read from clipboard")
    entity_parser.add_argument("--output", "-o", help="Output file")
    entity_parser.add_argument("--copy", action="store_true", help="Copy result to clipboard")

    # List platforms command
    platforms_parser = subparsers.add_parser("platforms", help="List supported platforms")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize CLI
    if args.use_api or USE_API:
        cli = GAPCliAPI(args.api_url)
    else:
        cli = GAPCliDirect()

    try:
        if args.command == "wrap":
            # Get content from various sources
            if args.stdin:
                content = read_from_stdin()
            elif args.clipboard:
                content = read_from_clipboard()
            elif args.content:
                content = args.content
            else:
                console.print("[red]No content provided. Use positional argument, --stdin, or --clipboard[/red]")
                return

            if not content:
                console.print("[red]Failed to read content[/red]")
                return

            result = cli.wrap(
                content=content,
                platform=args.platform,
                chat_id=args.chat_id,
                thread_id=args.thread_id,
                role=args.role,
                model=args.model
            )

            # Handle output
            if args.output:
                with open(args.output, "w") as f:
                    f.write(result)
                if not args.quiet:
                    console.print(f"[green]✓ GAP wrapped content saved to {args.output}[/green]")
            elif args.copy:
                if write_to_clipboard(result):
                    if not args.quiet:
                        console.print("[green]✓ GAP wrapped content copied to clipboard[/green]")
                print(result)
            else:
                print(result)

        elif args.command == "transform":
            # Get input from various sources
            if args.stdin:
                gap_markdown = read_from_stdin()
            elif args.clipboard:
                gap_markdown = read_from_clipboard()
            elif args.input_file:
                with open(args.input_file, "r") as f:
                    gap_markdown = f.read()
            else:
                console.print("[red]No input provided. Use positional argument, --stdin, or --clipboard[/red]")
                return

            if not gap_markdown:
                console.print("[red]Failed to read input[/red]")
                return

            context_additions = None
            if args.context:
                context_additions = json.loads(args.context)

            if hasattr(args, 'no_metadata') and not USE_API:
                # Direct mode supports no_metadata
                result = cli.gap.transform_for_platform(
                    cli.gap.from_markdown(gap_markdown),
                    args.target,
                    context_additions,
                    include_metadata=not args.no_metadata
                )
            else:
                result = cli.transform(gap_markdown, args.target, context_additions)

            # Handle output
            if args.output:
                with open(args.output, "w") as f:
                    f.write(result)
                if not args.quiet:
                    console.print(f"[green]✓ Transformed content saved to {args.output}[/green]")
            elif args.copy:
                if write_to_clipboard(result):
                    if not args.quiet:
                        console.print("[green]✓ Transformed content copied to clipboard[/green]")
                print(result)
            else:
                print(result)

        elif args.command == "update-entity":
            # Get input from various sources
            if args.stdin:
                gap_markdown = read_from_stdin()
            elif args.clipboard:
                gap_markdown = read_from_clipboard()
            elif args.input_file:
                with open(args.input_file, "r") as f:
                    gap_markdown = f.read()
            else:
                console.print("[red]No input provided. Use positional argument, --stdin, or --clipboard[/red]")
                return

            if not gap_markdown:
                console.print("[red]Failed to read input[/red]")
                return

            result = cli.update_entity(gap_markdown, args.key, args.value, args.type)

            # Handle output
            if args.output:
                with open(args.output, "w") as f:
                    f.write(result)
                if not args.quiet:
                    console.print(f"[green]✓ Updated GAP content saved to {args.output}[/green]")
            elif args.copy:
                if write_to_clipboard(result):
                    if not args.quiet:
                        console.print("[green]✓ Updated GAP content copied to clipboard[/green]")
                print(result)
            else:
                print(result)

        elif args.command == "platforms":
            if USE_API:
                console.print("[yellow]Platform list not available in API mode[/yellow]")
            else:
                from src.gap import PlatformTransformer
                transformer = PlatformTransformer()
                console.print("\n[bold]Supported platforms for transformation:[/bold]")
                for platform in transformer.platforms:
                    console.print(f"  • {platform}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
