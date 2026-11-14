"""macpilot-mcp unified server.

Read path (mail): exact vendored imdinu 3-layer stack — .emlx disk-first,
Envelope-Index direct reads, FTS5 BM25 search.
Write path (mail): vendored reed mail bridge with safety profiles.
Calendar / Reminders / Contacts: vendored reed bridges.
File guard: vendored freyer denylist.
"""

from __future__ import annotations

import dataclasses
import logging
from typing import Any, Literal

from fastmcp import FastMCP

from . import config as _cfg

_cfg.mirror_env_for_vendors()

from .vendor_imdinu import server as _mail

logger = logging.getLogger(__name__)

mcp = FastMCP("macpilot-mcp")


def _dump(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return {"__bytes_base64__": True, "length": len(value)}
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return dataclasses.asdict(value)
    if isinstance(value, (list, tuple)):
        return [_dump(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _dump(v) for k, v in value.items()}
    return str(value)


# --- mail: read/search via imdinu stack ---


@mcp.tool()
async def mail_status() -> dict:
    """FTS5 index health + stats."""
    from .vendor_imdinu.index.manager import IndexManager

    mgr = IndexManager()
    try:
        stats = mgr.get_stats()
    finally:
        mgr.close()
    return _dump(stats)


@mcp.tool()
async def mail_list_accounts() -> list:
    """List configured Mail accounts."""
    return _dump(await _mail.list_accounts())


@mcp.tool()
async def mail_list_mailboxes(account: str | None = None) -> list:
    """List mailboxes, optionally for one account."""
    return _dump(await _mail.list_mailboxes(account))


@mcp.tool()
async def mail_get_emails(
    account: str | None = None,
    mailbox: str | None = None,
    filter: Literal["all", "unread", "flagged", "today", "last_7_days"] = "all",
    limit: int = 20,
) -> list:
    """List emails from one mailbox (disk-first, no full scan)."""
    return _dump(await _mail.get_emails(account, mailbox, filter, min(limit, 200)))


@mcp.tool()
async def mail_get_email(message_id: str) -> dict:
    """Single email with full content + attachments (disk-first ~3ms)."""
    return _dump(await _mail.get_email(message_id))


@mcp.tool()
async def mail_search(
    query: str,
    scope: Literal["all", "subject", "sender", "body", "attachments"] = "all",
    account: str | None = None,
    mailbox: str | None = None,
    limit: int = 20,
    before: str | None = None,
    after: str | None = None,
) -> Any:
    """FTS5 full-mailbox search with BM25 ranking. Index required for body scope."""
    return _dump(
        await _mail.search(
            query, account, mailbox, scope, min(limit, 200), 0, None, before, after, False
        )
    )


@mcp.tool()
async def mail_get_links(message_id: str) -> list:
    """Extract hyperlinks from one email."""
    return _dump(await _mail.get_email_links(message_id))


@mcp.tool()
async def mail_index_rebuild(mailbox: str | None = None) -> dict:
    """(Re)build the FTS5 index from disk. Run again when the index is stale."""
    from .vendor_imdinu.index.manager import IndexManager

    mgr = IndexManager()
    try:
        n = mgr.build_from_disk(mailbox=mailbox)
        stats = mgr.get_stats()
    finally:
        mgr.close()
    return {"indexed": n, "stats": _dump(stats)}


# --- mail write path via reed bridge (safety-profile gated) ---


def _reed_mail_settings():
    from .vendor_reed.mail.config import load_settings

    return load_settings()


@mcp.tool()
def mail_send_message(
    to: list[str], subject: str, body: str, from_account: str | None = None
) -> dict:
    """Send email (full_access safety profile required)."""
    from .vendor_reed.mail import tools as _t

    s = _reed_mail_settings()
    return _dump(_t.mail_send_message_tool(s, _t.AppleMailBridge(), to, subject, body, from_account))


@mcp.tool()
def mail_move_message(message_id: str, target_mailbox: str) -> dict:
    """Move/archive a message."""
    from .vendor_reed.mail import tools as _t

    s = _reed_mail_settings()
    return _dump(_t.mail_move_message_tool(s, _t.AppleMailBridge(), message_id, target_mailbox))


@mcp.tool()
def mail_mark_message(message_id: str, is_read: bool = True) -> dict:
    """Mark read/unread."""
    from .vendor_reed.mail import tools as _t

    s = _reed_mail_settings()
    return _dump(_t.mail_mark_message_tool(s, _t.AppleMailBridge(), message_id, is_read))


# --- calendar / reminders / contacts (reed bridges, lazy) ---


@mcp.tool()
def calendar_list_events(start_iso: str, end_iso: str, limit: int = 50) -> Any:
    """Events in window (ISO datetimes)."""
    from .vendor_reed.calendar import tools as _t

    return _dump(_t._list_visible_events(start_iso, end_iso, None, min(limit, 200)))


@mcp.tool()
def reminders_list(list_id: str | None = None, limit: int = 50) -> Any:
    """Open reminders, optionally in one list."""
    from .vendor_reed.reminders import tools as _t

    return _dump(_t._scoped_reminders(list_id=list_id, limit=min(limit, 200)))


@mcp.tool()
def contacts_search(query: str, limit: int = 20) -> Any:
    """Search contacts by name/email/phone."""
    from .vendor_reed.contacts import tools as _t

    return _dump(_t.contacts_search_contacts(query, min(limit, 100)))


@mcp.tool()
def macpilot_health() -> dict:
    """Server health across domains."""
    out: dict[str, Any] = {"server": "macpilot-mcp"}
    try:
        from .vendor_imdinu.index.manager import IndexManager

        mgr = IndexManager()
        try:
            out["mail_index"] = _dump(mgr.get_stats())
        finally:
            mgr.close()
    except Exception as e:  # noqa: BLE001
        out["mail_index"] = {"ok": False, "error": str(e)}
    for domain in ("calendar", "reminders", "contacts"):
        try:
            mod = __import__(
                f"macpilot_mcp.vendor_reed.{domain}.tools", fromlist=["x"]
            )
            fn = getattr(mod, f"{domain}_health", None)
            out[domain] = _dump(fn()) if fn else {"ok": True}
        except Exception as e:  # noqa: BLE001
            out[domain] = {"ok": False, "error": str(e)[:200]}
    return out
