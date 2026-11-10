# macpilot-mcp

Unified local Apple Mail + Calendar + Reminders + Contacts MCP. Python, stdio + loopback HTTP, FTS5 mail search from day one.

- Mail read/search: vendored `imdinu/apple-mail-mcp` 3-layer stack (`.emlx` disk-first, Envelope-Index direct, FTS5 BM25). Exact code in `src/macpilot_mcp/vendor_imdinu/`.
- Mail write guard + rich drafts: vendored `patrickfreyer/apple-mail-mcp` denylist (`vendor_freyer/paths.py`).
- Calendar/Reminders/Contacts + safety profiles + loopback guard: vendored `JonathanRReed/Apple-MCPs` (`vendor_reed/`, `vendor_common/`).
- License: GPL-3.0-or-later (strictest vendored license wins).

## Run

```
uv sync
uv run macpilot-mcp index     # build FTS5 once (do this now, mail grows later)
uv run macpilot-mcp status
uv run macpilot-mcp serve     # stdio, for opencode/claude/codex/pi
uv run macpilot-mcp serve --transport streamable-http --port 8765
```

## Clients

```
# Claude Code
claude mcp add --transport stdio macpilot -- uv run --directory ~/Workspace/projects/macpilot-mcp macpilot-mcp serve
# Codex: [mcp_servers.macpilot] command="uv" args=["run","--directory","/Users/uditagarwal19199/Workspace/projects/macpilot-mcp","macpilot-mcp","serve"]
# OpenCode opencode.json: "mcp": {"macpilot": {"type": "local", "command": ["uv","run","--directory","/Users/uditagarwal19199/Workspace/projects/macpilot-mcp","macpilot-mcp","serve"]}}
```

## Checks

```
uv run ruff check src tests
uv run pytest -q
```
