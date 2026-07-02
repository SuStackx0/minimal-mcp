import asyncio
import json

# Minimal Model Context Protocol (MCP) Server
# -------------------------------------------
# Simulates a basic MCP server that can respond to a "get_manifest" request.

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"🔗 Connection from {addr}")

    # Read client request
    data = await reader.read(4096)
    if not data:
        writer.close()
        return

    try:
        request = json.loads(data.decode())
    except json.JSONDecodeError:
        writer.write(b'{"error": "Invalid JSON"}')
        await writer.drain()
        writer.close()
        return

    method = request.get("method")
    response = {"jsonrpc": "2.0", "id": request.get("id", 1)}

    if method == "get_manifest":
        # The MCP "manifest" describes what the server can do.
        response["result"] = {
            "name": "Minimal MCP Server",
            "version": "0.1.0",
            "resources": [
                {
                    "uri": "mcp://example/resource1",
                    "description": "A simple example resource"
                }
            ],
            "methods": ["get_manifest"]
        }
    else:
        response["error"] = {"code": -32601, "message": "Method not found"}

    # Send response back to client
    writer.write((json.dumps(response) + "\n").encode())
    await writer.drain()
    writer.close()

async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 8765)
    addr = server.sockets[0].getsockname()
    print(f"✅ MCP server listening on {addr}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
