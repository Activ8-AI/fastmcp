"""
MCP Client Utilities

Provides helper functions for connecting to MCP servers.
The actual MCP client session is provided by the mcp library.

Usage:
    from mcp.client.session import ClientSession
    from mcp.client.stdio import stdio_client

    # Connect to a server via STDIO
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
"""

import asyncio
import subprocess
from dataclasses import dataclass
from typing import Any


@dataclass
class ServerConfig:
    """Configuration for an MCP server connection."""
    name: str
    command: str | None = None
    args: list[str] | None = None
    url: str | None = None
    env: dict[str, str] | None = None


# Default server configurations
DEFAULT_SERVERS = {
    "activ8": ServerConfig(
        name="Activ8 MCP",
        command="python",
        args=["-m", "activ8_mcp.server"],
    ),
}


def get_server_config(name: str) -> ServerConfig | None:
    """Get server configuration by name."""
    return DEFAULT_SERVERS.get(name)


def list_configured_servers() -> list[str]:
    """List all configured server names."""
    return list(DEFAULT_SERVERS.keys())


async def check_server_available(config: ServerConfig) -> tuple[bool, str]:
    """
    Check if a server is available.

    Returns (available, message) tuple.
    """
    if config.command:
        try:
            # Check if command exists
            result = subprocess.run(
                ["which", config.command],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return False, f"Command not found: {config.command}"
            return True, "Command available"
        except Exception as e:
            return False, f"Error checking command: {e}"

    if config.url:
        try:
            import urllib.request
            req = urllib.request.Request(config.url, method="HEAD")
            urllib.request.urlopen(req, timeout=5)
            return True, "URL reachable"
        except Exception as e:
            return False, f"URL not reachable: {e}"

    return False, "No command or URL configured"


async def main():
    """Demo: List and check configured servers."""
    print("\n=== MCP Server Configuration ===\n")

    for name in list_configured_servers():
        config = get_server_config(name)
        if config:
            available, message = await check_server_available(config)
            status = "[OK]" if available else "[FAIL]"
            print(f"{status} {name}: {message}")
            if config.command:
                print(f"      Command: {config.command} {' '.join(config.args or [])}")
            if config.url:
                print(f"      URL: {config.url}")


if __name__ == "__main__":
    asyncio.run(main())
