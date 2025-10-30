import asyncio
import json

# Minimal Model Context Protocol (MCP) Client
# -------------------------------------------
# This simulates what an LLM would do — sending a get_manifest
# JSON-RPC request to the MCP server and printing the response.

async def main():
    reader, writer = await asyncio.open_connection("127.0.0.1", 8765)

    # Prepare the handshake request
    request = {
        "jsonrpc": "2.0",
        "method": "get_manifest",
        "id": 1
    }

    # Send request to the MCP server
    writer.write((json.dumps(request) + "\n").encode())
    await writer.drain()

    # Read and print response
    data = await reader.read(4096)
    print("🧠 Server response:\n", data.decode())

    writer.close()
    await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
