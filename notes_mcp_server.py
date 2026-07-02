import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# ── CREATE MCP SERVER ─────────────────────────────────────────────────────────
mcp = FastMCP("notes-server")

# ── WHERE NOTES ARE SAVED ─────────────────────────────────────────────────────
NOTES_FILE = "notes.txt"


# ── TOOL 1: Save a note ───────────────────────────────────────────────────────
# When agent calls save_note("buy groceries"):
# → appends "buy groceries" with timestamp to notes.txt
@mcp.tool()
def save_note(text: str) -> str:
    """Save a note to the local notes file."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {text}\n")
        return f"Note saved: {text}"
    except Exception as e:
        return f"Could not save note: {str(e)}"


# ── TOOL 2: Read all notes ────────────────────────────────────────────────────
# When agent calls read_notes():
# → reads everything from notes.txt and returns it
@mcp.tool()
def read_notes() -> str:
    """Read all saved notes from the notes file."""
    try:
        if not os.path.exists(NOTES_FILE):
            return "No notes saved yet."
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return "No notes saved yet."
        return f"Your notes: {content}"
    except Exception as e:
        return f"Could not read notes: {str(e)}"


# ── START SERVER ──────────────────────────────────────────────────────────────
# mcp.run() starts the MCP server using stdio transport
# stdio means it communicates through standard input/output
# This is how the agent.py client will talk to this server
if __name__ == "__main__":
    import sys
    print("📝 Notes MCP Server running...", file=sys.stderr)  # ← safe
    mcp.run(transport="stdio")