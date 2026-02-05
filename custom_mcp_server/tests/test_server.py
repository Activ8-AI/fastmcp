"""Tests for Activ8-AI MCP Server."""

import pytest


async def test_server_import():
    """Test that the server can be imported."""
    from activ8_mcp import mcp
    assert mcp is not None
    assert mcp.name == "Activ8MCP"


async def test_registry_import():
    """Test that the registry can be imported."""
    from activ8_mcp import MCP_REGISTRY, get_enabled_servers
    assert MCP_REGISTRY is not None
    assert len(MCP_REGISTRY) > 0

    enabled = get_enabled_servers()
    assert isinstance(enabled, dict)


async def test_tools_available():
    """Test that tools are registered."""
    from activ8_mcp import mcp

    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]

    # Check core tools exist
    assert "get_system_info" in tool_names
    assert "list_directory" in tool_names
    assert "git_status" in tool_names
    assert "http_get" in tool_names
    assert len(tools) == 21


async def test_get_system_info():
    """Test the get_system_info tool."""
    from activ8_mcp import mcp

    result = await mcp.call_tool("get_system_info", {})
    assert result is not None
    assert len(result) > 0


async def test_calculate():
    """Test the calculate tool."""
    from activ8_mcp import mcp

    result = await mcp.call_tool("calculate", {"expression": "2 + 2"})
    assert result is not None
