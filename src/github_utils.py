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
    print(data)
    for item in data:
        # Determine if the item is an issue or pull request
        is_pull_request = False

        # Extract common fields
        parsed_item = {
            "type": "pull_request" if is_pull_request else "issue",
            "number": item.get("number"),
            "title": item.get("title"),
            "state": item.get("state"),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
            "closed_at": item.get("closed_at"),
            "user": item.get("user", {}).get("login"),
            "html_url": item.get("html_url"),
            "labels": [label.get("name") for label in item.get("labels", [])],
            # "body": item.get("body"),
        }

        # Add issue-specific fields
        # if not is_pull_request:
        #     parsed_item.update(
        #         {
        #             "comments_count": item.get("comments"),
        #             "reactions": item.get("reactions", {}).get("total_count"),
        #             "milestone": item.get("milestone", {}).get("title")
        #             if item.get("milestone")
        #             else None,
        #             "author_association": item.get("author_association"),
        #         }
        #     )

        # Add pull request-specific fields
        if is_pull_request:
            parsed_item.update(
                {
                    "merged_at": item.get("merged_at")
                    or (
                        item.get("pull_request", {}).get("merged_at")
                        if "pull_request" in item
                        else None
                    ),
                    "head_branch": item.get("head", {}).get("ref")
                    if "head" in item
                    else None,
                    "base_branch": item.get("base", {}).get("ref")
                    if "base" in item
                    else None,
                    "merge_commit_sha": item.get("merge_commit_sha")
                    if "merge_commit_sha" in item
                    else None,
                    "draft": item.get("draft", False),
                }
            )

        parsed_data.append(parsed_item)

    return parsed_data
