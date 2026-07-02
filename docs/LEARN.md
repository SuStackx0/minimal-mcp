# Learn MCP (fast)

A concise tour of everything an AI engineer should be able to explain about the
**Model Context Protocol**. Each section is short on purpose — enough to *get it*
and to *talk about it*, not a spec dump. The official spec lives at
<https://modelcontextprotocol.io>.

---

## 1. What it is & why it exists

An LLM on its own is a text-in/text-out box. To be useful it needs **context**
(your files, your database, live data) and **actions** (send an email, run a query).
Before MCP, every app wired each tool to each model with bespoke glue — an *M×N*
integration mess.

**MCP is an open standard that turns M×N into M+N.** A tool provider writes *one*
MCP server; any MCP-compatible app can use it. The canonical analogy: **MCP is the
"USB-C port" for AI** — one standard plug between models and the world. Announced by
Anthropic in late 2024, now adopted broadly across the industry.

## 2. Architecture: host, client, server

```
┌─────────── Host (Claude Desktop, IDE, your app) ───────────┐
│  contains the LLM + one MCP client per server it connects   │
│                                                             │
│   ┌────────────┐        JSON-RPC 2.0        ┌────────────┐  │
│   │ MCP client │  <──────────────────────>  │ MCP server │  │
│   └────────────┘   (over stdio or HTTP)     └────────────┘  │
└─────────────────────────────────────────────┬──────────────┘
                                               │
                                    files / DB / API / tools
```

- **Host** — the user-facing app that holds the model and decides what to expose to it.
- **Client** — lives inside the host; maintains a 1:1 connection to one server.
- **Server** — a program you write that exposes tools/resources/prompts. It does *not*
  contain a model; it just offers capabilities.

Key idea: the **server never talks to the LLM directly**. It hands capabilities to the
client, and the host decides how/whether the model uses them.

## 3. The three primitives

| Primitive     | Who initiates      | Analogy        | Side effects? |
| ------------- | ------------------ | -------------- | ------------- |
| **Tool**      | model-controlled   | POST endpoint  | yes           |
| **Resource**  | app/user-controlled| GET endpoint   | no            |
| **Prompt**    | user-controlled    | slash-command  | n/a           |

- **Tools** — functions the model can call (`add_note`, `run_query`). The function
  signature + docstring become a schema the model reads to decide *when* and *how* to
  call. This is the primitive you'll use most.
- **Resources** — read-only data addressed by a URI (`notes://all`, `file:///…`).
  Loaded into context; no side effects.
- **Prompts** — pre-written, parameterized message templates the *user* triggers.

See all three in one file: [`../examples/server.py`](../examples/server.py).

> **Advanced primitives** (know the names): **Roots** let the client tell the server
> which directories/URLs it may touch. **Sampling** lets a *server* ask the *host's*
> model to generate text (server-initiated LLM calls). **Elicitation** lets a server
> pause to ask the user for more input mid-operation.

## 4. Transports

MCP messages are **JSON-RPC 2.0**; the transport is how those bytes travel:

- **stdio** — the server runs as a local subprocess; messages go over stdin/stdout.
  Simple, fast, no ports. Default for local tools (what our examples use).
- **Streamable HTTP** (with optional Server-Sent Events) — the server is a remote
  web service. Used for hosted/multi-user servers. (Replaces the older "HTTP+SSE"
  transport.)

Same protocol either way — only the pipe changes.

## 5. Connection lifecycle

1. **initialize** — client and server exchange versions and **negotiate capabilities**
   (what each side supports). Nothing else works before this handshake.
2. **discovery** — client calls `tools/list`, `resources/list`, `prompts/list`.
3. **use** — `tools/call`, `resources/read`, `prompts/get`.
4. **teardown** — connection closes when the host is done.

Our [`../examples/client.py`](../examples/client.py) does exactly steps 1–3 by hand,
so you can watch it happen without an LLM in the loop.

## 6. Using a server from a real host

Claude Desktop (and most hosts) launch stdio servers from a JSON config. Example
entry for our notes server:

```json
{
  "mcpServers": {
    "sticky-notes": {
      "command": "python",
      "args": ["/absolute/path/to/examples/server.py"]
    }
  }
}
```

The host spawns that command, speaks MCP over stdio, and surfaces the tools/resources
to the model. That config block *is* the "how do I plug my server into Claude" answer.

## 7. Security (the part interviewers probe)

- **Servers run with the user's privileges** — a malicious or buggy server can do real
  damage. Only install servers you trust.
- **Confused-deputy / prompt injection** — data pulled through a resource can contain
  instructions that hijack the model. Treat tool output as untrusted input.
- **Least privilege** — scope what a server can reach (see **roots**); don't hand it
  broad filesystem or network access it doesn't need.
- **Human-in-the-loop** — hosts should confirm consequential tool calls with the user.
- **Auth for remote servers** — HTTP transports need real authorization (OAuth-style),
  not just an open port.

## 8. What I can say I know (talking points)

- MCP is an open standard that replaces M×N model-tool integrations with M+N; the
  "USB-C for AI" analogy.
- The host / client / server split, and that servers expose capabilities but never
  call the model themselves.
- The three primitives — **tools** (model-controlled actions), **resources**
  (read-only context), **prompts** (user-triggered templates) — plus the names roots,
  sampling, and elicitation.
- It's **JSON-RPC 2.0** over **stdio** (local) or **streamable HTTP** (remote), starting
  with an **initialize** capability handshake.
- I've built a server with the official SDK *and* implemented the raw JSON-RPC
  underneath, so I understand both the ergonomics and the wire format.
- The core security concerns: server privilege, prompt injection via resource data,
  least privilege, and human-in-the-loop confirmation.
