"""
A real MCP server using the official Python SDK (FastMCP).

Theme: a tiny in-memory "sticky notes" service. It's deliberately trivial so the
*protocol* is what you notice, not the business logic. This one file demonstrates
all three MCP primitives:

    • Tools     — actions the model can CALL      (add_note, clear_notes)
    • Resources — data the model can READ         (notes://all, note://{name})
    • Prompts   — reusable message templates       (summarize_notes)

Run it standalone for a smoke test:

    python examples/server.py

...but normally you don't run it by hand. A *host* (Claude Desktop, an IDE, or
our examples/client.py) launches it and talks to it over stdio. See the bottom of
this file and docs/LEARN.md for how that wiring works.
"""

from mcp.server.fastmcp import FastMCP

# The server object. The name is what shows up in the client's UI/logs.
mcp = FastMCP("Sticky Notes")

# Our "database" is just a dict. Real servers would hit a DB, an API, the filesystem…
_notes: dict[str, str] = {}


# ─────────────────────────────────────────────────────────────────────────────
# TOOLS — things the model can DO. The function signature + docstring become the
# tool's schema automatically, which is how the model knows when and how to call it.
# Write docstrings for the model, not just for humans: they are the tool's "prompt".
# ─────────────────────────────────────────────────────────────────────────────

@mcp.tool()
def add_note(name: str, content: str) -> str:
    """Save a note under a short name. Overwrites any existing note with that name."""
    _notes[name] = content
    return f"Saved note '{name}' ({len(content)} chars)."


@mcp.tool()
def clear_notes() -> str:
    """Delete every saved note. Returns how many were removed."""
    count = len(_notes)
    _notes.clear()
    return f"Cleared {count} note(s)."


# ─────────────────────────────────────────────────────────────────────────────
# RESOURCES — read-only data the model (or user) can pull into context. Think of
# them like GET endpoints, addressed by a URI. Unlike tools, reading a resource
# should have no side effects.
# ─────────────────────────────────────────────────────────────────────────────

@mcp.resource("notes://all")
def all_notes() -> str:
    """A plain-text dump of every note."""
    if not _notes:
        return "(no notes yet)"
    return "\n".join(f"- {name}: {body}" for name, body in _notes.items())


@mcp.resource("note://{name}")
def one_note(name: str) -> str:
    """A single note by name. The {name} in the URI becomes a function argument."""
    return _notes.get(name, f"(no note named '{name}')")


# ─────────────────────────────────────────────────────────────────────────────
# PROMPTS — reusable, parameterized message templates the user can invoke (e.g. a
# slash-command in the host). They return the text that gets sent to the model.
# ─────────────────────────────────────────────────────────────────────────────

@mcp.prompt()
def summarize_notes(style: str = "bullet points") -> str:
    """Ask the model to summarize all saved notes in a given style."""
    return (
        f"Here are my notes:\n\n{all_notes()}\n\n"
        f"Summarize them as {style}. Be concise."
    )


if __name__ == "__main__":
    # transport="stdio" means: read JSON-RPC from stdin, write it to stdout.
    # That's exactly what a host launches this process expecting to speak.
    mcp.run(transport="stdio")
