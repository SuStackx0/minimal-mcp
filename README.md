# minimal-mcp

A small, hands-on tour of the **Model Context Protocol (MCP)** — the open standard
that lets AI models plug into tools and data ("USB-C for AI"). Built to learn the
protocol properly and to show I can work with it, from the raw wire format up to the
official SDK.

## What's inside

| Path                                     | What it teaches                                                        |
| ---------------------------------------- | ---------------------------------------------------------------------- |
| [`docs/LEARN.md`](docs/LEARN.md)         | The concept guide — architecture, primitives, transports, security. Start here. |
| [`raw/`](raw/)                           | MCP **under the hood**: a from-scratch JSON-RPC server/client, no dependencies. |
| [`examples/server.py`](examples/server.py) | A **real** MCP server (official SDK / FastMCP) showing tools, resources, and prompts. |
| [`examples/client.py`](examples/client.py) | A **real** MCP client that launches the server over stdio and drives it — no LLM required. |

## Quickstart

```bash
# 1. Install the official SDK (a virtualenv is recommended)
pip install -r requirements.txt

# 2. Run the real client — it spawns the server and exercises every primitive
python examples/client.py
```

Expected output: the client lists the server's tools/resources/prompts, adds a couple
of notes, reads them back, and renders a prompt template.

To see the protocol with no libraries at all, run the raw demo instead —
see [`raw/README.md`](raw/README.md).

## The mental model in one line

> A **host** (like Claude Desktop) runs an MCP **client** that speaks JSON-RPC to an
> MCP **server** you write, which exposes **tools** (actions), **resources** (data),
> and **prompts** (templates) — over **stdio** locally or **HTTP** remotely.

Full explanation and interview talking points in [`docs/LEARN.md`](docs/LEARN.md).
