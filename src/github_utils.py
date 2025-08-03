import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def get_github_mcp_tool_info():
    """
    Returns a list of dicts with tool name, description, and input schema from the MCP server.
    """

    async def _list_tools():
        server_params = StdioServerParameters(
            command="npx", args=["-y", "@modelcontextprotocol/server-github"]
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                tool_dict = dict(tools)
                tool_list = tool_dict.get("tools", [])

                return [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema,
                    }
                    for tool in tool_list
                ]

    return asyncio.run(_list_tools())


def call_github_mcp_tool(tool_name, params):
    """
    Generic MCP tool caller for GitHub via Docker Desktop MCP Toolkit.
    tool_name: str, e.g. 'github_list_pull_requests'
    params: dict, tool parameters
    """

    async def _call():
        server_params = StdioServerParameters(
            command="npx", args=["-y", "@modelcontextprotocol/server-github"]
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, params)
                return parse_github_data(result)

    return asyncio.run(_call())


def parse_github_data(mcp_output):
    """
    Universal parser for GitHub issues and pull requests from MCP output.
    Returns a list of dictionaries with useful information.
    """
    # Extract the JSON string from the MCP output
    try:
        content = mcp_output.content[0].text
        data = json.loads(content)
    except (KeyError, json.JSONDecodeError) as e:
        return {"error": f"Invalid MCP output format: {str(e)}"}

    parsed_data = []

    # Handle GitHub search API format: {'total_count': ..., 'incomplete_results': ..., 'items': [...]}
    if isinstance(data, dict) and "items" in data:
        items = data["items"]
        for item in items:
            parsed_item = {
                "type": item.get("type", "repo"),
                "id": item.get("id"),
                "name": item.get("name"),
                "full_name": item.get("full_name"),
                "private": item.get("private"),
                "owner": item.get("owner", {}).get("login"),
                "html_url": item.get("html_url"),
                "description": item.get("description"),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "pushed_at": item.get("pushed_at"),
                "default_branch": item.get("default_branch"),
            }
            parsed_data.append(parsed_item)
        # Optionally, add metadata
        parsed_data = {
            "total_count": data.get("total_count"),
            "incomplete_results": data.get("incomplete_results"),
            "items": parsed_data,
        }
        return parsed_data

    # Handle previous list-of-issues/pull-requests format
    if isinstance(data, list):
        for item in data:
            # Extract common fields
            parsed_item = {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": item.get("state"),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "closed_at": item.get("closed_at"),
                "user": item.get("user", {}).get("login"),
                "html_url": item.get("html_url"),
                "labels": [label.get("name") for label in item.get("labels", [])],
            }

            parsed_data.append(parsed_item)
        return parsed_data

    # If not recognized, just return the raw data
    return data
