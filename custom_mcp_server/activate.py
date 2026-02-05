#!/usr/bin/env python
"""
MCP Server Activation CLI - Wire up and activate MCP servers

Usage:
    # List all servers and their status
    uv run python custom_mcp_server/activate.py --list

    # Generate Claude Desktop config
    uv run python custom_mcp_server/activate.py --claude-desktop

    # Check server readiness (secrets available)
    uv run python custom_mcp_server/activate.py --check

    # Run the activ8 server in HTTP mode
    uv run python custom_mcp_server/activate.py --serve --port 8000
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_registry import (
    MCP_SERVERS,
    ServerType,
    UseCase,
    auto_enable_servers,
    get_enabled_servers,
    get_servers_by_use_case,
    print_registry,
)

# Auto-enable servers based on available environment variables
auto_enable_servers()


def check_server_readiness(name: str) -> tuple[str, bool, str]:
    """Check if a server is ready (has required secrets)."""
    if name not in MCP_SERVERS:
        return name, False, f"Unknown server: {name}"

    config = MCP_SERVERS[name]

    if not config.enabled:
        return name, False, "Server is disabled"

    # Check required env vars
    missing = []
    for key, value in config.env_vars.items():
        if value.startswith("${") and value.endswith("}"):
            env_name = value[2:-1]
            if not os.environ.get(env_name):
                missing.append(env_name)

    if missing:
        return name, False, f"Missing secrets: {', '.join(missing)}"

    return name, True, f"Ready ({config.server_type.value})"


def check_all_servers():
    """Check readiness of all enabled servers."""
    print("\nChecking MCP Server Readiness...\n")

    enabled = get_enabled_servers()
    if not enabled:
        print("No servers enabled!")
        return

    print("-" * 60)
    for name in enabled.keys():
        name, success, message = check_server_readiness(name)
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {name}: {message}")
    print("-" * 60)


def generate_claude_desktop_config():
    """Generate configuration for Claude Desktop."""
    config = {"mcpServers": {}}

    for name, server in MCP_SERVERS.items():
        if not server.enabled:
            continue

        if server.server_type == ServerType.LOCAL_STDIO:
            config["mcpServers"][name] = {
                "command": "uv",
                "args": ["run", "python", server.script_path],
                "cwd": str(Path(__file__).parent.parent),
            }
        elif server.server_type == ServerType.NPX:
            config["mcpServers"][name] = {
                "command": "npx",
                "args": [server.npx_package],
                "env": {
                    k: os.environ.get(v[2:-1], "") if v.startswith("${") else v
                    for k, v in server.env_vars.items()
                },
            }

    print("\nClaude Desktop Configuration")
    print("=" * 60)
    print("Add to: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("=" * 60)
    print(json.dumps(config, indent=2))
    print("=" * 60)


def serve_http(port: int):
    """Run the server in HTTP mode."""
    print(f"Starting Activ8 MCP on http://0.0.0.0:{port}/mcp")

    from server import mcp

    mcp.run(transport="http", host="0.0.0.0", port=port)


def list_by_use_case():
    """List servers grouped by use case."""
    print("\nMCP Servers by Use Case\n")

    for use_case in UseCase:
        servers = get_servers_by_use_case(use_case)
        if servers:
            print(f"  {use_case.value.upper()}:")
            for s in servers:
                print(f"    - {s.name}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Activ8-AI MCP Server Activation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("--list", "-l", action="store_true", help="List all registered MCP servers")
    parser.add_argument(
        "--use-cases", "-u", action="store_true", help="List servers grouped by use case"
    )
    parser.add_argument(
        "--check", "-t", action="store_true", help="Check server readiness (secrets available)"
    )
    parser.add_argument(
        "--claude-desktop", "-c", action="store_true", help="Generate Claude Desktop configuration"
    )
    parser.add_argument("--serve", "-s", action="store_true", help="Run the server in HTTP mode")
    parser.add_argument(
        "--port", "-p", type=int, default=8000, help="Port for HTTP server (default: 8000)"
    )

    args = parser.parse_args()

    # Default to --list if no args
    if len(sys.argv) == 1:
        args.list = True

    if args.list:
        print_registry()
    elif args.use_cases:
        list_by_use_case()
    elif args.check:
        check_all_servers()
    elif args.claude_desktop:
        generate_claude_desktop_config()
    elif args.serve:
        serve_http(args.port)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
