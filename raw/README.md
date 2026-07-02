# `raw/` — MCP under the hood

Before reaching for the official SDK, it helps to see what it actually does for you.
This folder is a **from-scratch, no-dependencies** MCP-ish server and client so you can
watch the wire protocol with your own eyes.

## What's really going on

MCP is built on **JSON-RPC 2.0** — a tiny convention for calling methods over any
transport. A request looks like this:

```json
{ "jsonrpc": "2.0", "method": "get_manifest", "id": 1 }
```

and the response echoes the same `id` with either a `result` or an `error`:

```json
{ "jsonrpc": "2.0", "id": 1, "result": { "name": "Minimal MCP Server", "...": "..." } }
```

That's the whole trick. Everything the fancy SDK does — listing tools, calling a tool,
reading a resource — is just a named JSON-RPC method with structured params. Here we
implement a single `get_manifest` method over a raw TCP socket to keep it honest.

> ⚠️ This is a **teaching toy**, not real MCP. It skips the `initialize` handshake,
> capability negotiation, the standard method names (`tools/list`, `tools/call`, …),
> and the real transports (stdio / streamable HTTP). See [`../examples/`](../examples/)
> for the real thing using the official SDK, and [`../docs/LEARN.md`](../docs/LEARN.md)
> for how the pieces fit together.

## Run it

Open two terminals from the repo root:

```bash
# terminal 1 — start the server
python raw/server.py

# terminal 2 — send it a request
python raw/client.py
```

The client sends a `get_manifest` request; the server replies with a hand-written
"manifest" describing what it can do. Try changing the `method` in `client.py` to
something the server doesn't know and watch it return a JSON-RPC error.

## Map raw → real

| This toy                    | Real MCP equivalent                          |
| --------------------------- | -------------------------------------------- |
| `get_manifest`              | `initialize` + `tools/list` + `resources/list` |
| raw TCP socket              | stdio pipe or streamable HTTP                |
| hand-written JSON dict      | typed tools/resources the SDK generates      |
| no handshake                | `initialize` capability negotiation          |
