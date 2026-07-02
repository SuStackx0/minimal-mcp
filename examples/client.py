"""
A real MCP client using the official Python SDK.

This is the "host" side. It does what Claude Desktop does under the hood:

    1. Launches examples/server.py as a subprocess, speaking over stdio.
    2. Runs the `initialize` handshake (capability negotiation).
    3. Lists what the server offers, then actually uses it.

There is NO LLM here — we drive the server by hand so you can see the raw
capabilities a model would be given. Run it from the repo root:

    python examples/client.py
"""

import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# How to start the server process. This mirrors a Claude Desktop config entry:
#   { "command": "python", "args": ["examples/server.py"] }
server = StdioServerParameters(command="python", args=["examples/server.py"])


async def main() -> None:
    # stdio_client spawns the subprocess and wires up the pipes.
    async with stdio_client(server) as (read, write):
        # A ClientSession is one conversation with one server.
        async with ClientSession(read, write) as session:
            # The mandatory handshake. Everything else fails until this runs.
            await session.initialize()

            # ── Discover what's available ──────────────────────────────────
            tools = await session.list_tools()
            print("🔧 Tools:", [t.name for t in tools.tools])

            resources = await session.list_resources()
            print("📄 Resources:", [str(r.uri) for r in resources.resources])

            prompts = await session.list_prompts()
            print("💬 Prompts:", [p.name for p in prompts.prompts])

            # ── Actually use them ──────────────────────────────────────────
            print("\n-- calling add_note --")
            result = await session.call_tool(
                "add_note", {"name": "groceries", "content": "milk, eggs, coffee"}
            )
            print(result.content[0].text)

            await session.call_tool(
                "add_note", {"name": "todo", "content": "learn MCP"}
            )

            print("\n-- reading resource notes://all --")
            content, _ = await session.read_resource("notes://all")
            print(content)

            print("\n-- rendering prompt summarize_notes --")
            prompt = await session.get_prompt("summarize_notes", {"style": "one line"})
            print(prompt.messages[0].content.text)


if __name__ == "__main__":
    asyncio.run(main())
