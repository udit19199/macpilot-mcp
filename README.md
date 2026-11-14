# macpilot-mcp

One local MCP server for Apple Mail, Calendar, Reminders and Contacts on macOS. It reads the same data the Apple apps show, keeps a full-text search index of your mail on disk, and gives an AI client a small set of tools for those four apps.

Version 0.1.0. macOS only.

## What it does

- Searches all mail with SQLite FTS5 and BM25 ranking, including message bodies.
- Lists accounts, mailboxes and messages, and opens one message with its attachments.
- Moves, marks and sends mail, gated by a safety profile.
- Lists calendar events in a time window.
- Lists open reminders.
- Searches contacts by name, email address or phone number.
- Reports index and domain health.

Mail reads go to the files in `~/Library/Mail` first, so opening a message does not start Mail or AppleScript. Calendar, Reminders and Contacts go through a small Swift helper that uses EventKit.

## Tools

| Tool | What it does | Writes |
| --- | --- | --- |
| `mail_status` | Index health and counts | No |
| `mail_list_accounts` | Mail accounts | No |
| `mail_list_mailboxes` | Mailboxes, optionally for one account | No |
| `mail_get_emails` | Messages in a mailbox, with an unread/flagged/today filter | No |
| `mail_get_email` | One message with full body and attachments | No |
| `mail_search` | FTS5 search over subject, sender, body or attachments | No |
| `mail_get_links` | Links found in one message | No |
| `mail_index_rebuild` | Rebuild the FTS5 index | Local index only |
| `mail_send_message` | Send a new message | Yes, needs `full_access` |
| `mail_move_message` | Move or archive a message | Yes |
| `mail_mark_message` | Mark read or unread | Yes |
| `calendar_list_events` | Events between two ISO datetimes | No |
| `reminders_list` | Open reminders, optionally in one list | No |
| `contacts_search` | Search contacts | No |
| `macpilot_health` | Index and domain health | No |

## Requirements

- macOS with Mail, Calendar, Reminders and Contacts set up.
- Python 3.11 or newer.
- [uv](https://docs.astral.sh/uv/).
- Xcode Command Line Tools, for `swiftc`. The Calendar, Reminders and Contacts helper compiles on first use. Install with `xcode-select --install`.

## Install

```sh
git clone <repo-url> macpilot-mcp
cd macpilot-mcp
uv sync
uv run macpilot-mcp index    # build the search index once
uv run macpilot-mcp status   # print index counts
```

`index` prints how many messages it wrote and the database path. The first run reads your whole Mail folder, so expect it to take a while on a large mailbox.

Start the server:

```sh
uv run macpilot-mcp serve
```

By default it speaks MCP over stdio. To use HTTP on loopback:

```sh
uv run macpilot-mcp serve --transport streamable-http --port 8765
```

The HTTP transport refuses any host other than `127.0.0.1`.

## Configure a client

Claude Code:

```sh
claude mcp add --transport stdio macpilot -- uv run --directory /path/to/macpilot-mcp macpilot-mcp serve
```

OpenCode, in `opencode.json`:

```json
{
  "mcp": {
    "macpilot": {
      "type": "local",
      "command": [
        "uv",
        "run",
        "--directory",
        "/path/to/macpilot-mcp",
        "macpilot-mcp",
        "serve"
      ],
      "enabled": true
    }
  }
}
```

Replace `/path/to/macpilot-mcp` with the folder you cloned into.

## macOS permissions

- Full Disk Access. The app that starts the server, such as Terminal, iTerm2 or your editor, needs this to read `~/Library/Mail` without prompts. Add it in System Settings > Privacy & Security > Full Disk Access. Quit and reopen the app after adding it.
- Automation. macOS asks whether the app may control Mail. Allow it. Mail writes use AppleScript, so the prompt appears on the first write.
- Calendar, Reminders and Contacts. The first call that needs the Swift helper triggers a system prompt for that app. Allow it. The helper is an ad-hoc signed bundle in `~/.apple-mcps/build`.
- If a prompt never appears, run the server once from Terminal so macOS knows which app is asking.

## Safety

The default profile is `safe_manage`.

- `mail_send_message` needs `MACPILOT_SAFETY_PROFILE=full_access`. At lower profiles it returns a policy error and sends nothing. Set the profile in the server environment before start.
- `mail_move_message` and `mail_mark_message` work under `safe_manage`. They change your mailbox.
- `serve --read-only` sets the profile to `safe_readonly` and blocks all three write tools. Read tools keep working.
- `calendar_list_events`, `reminders_list` and `contacts_search` do not write. The server registers no calendar, reminder or contact write tool.
- No tool deletes mail.

Data handling:

- The index lives in `~/.macpilot-mcp/index.db` and holds sender, subject, date and body text for indexed messages. It is not encrypted. Treat it like a copy of your mail.
- Everything runs locally. The server makes no network calls and sends no telemetry.
- The HTTP transport listens on loopback only.

## Limitations

- macOS only. There is no Linux or Windows support.
- The index does not update itself. Listing and opening messages read the Mail folder directly, but body search only sees messages written by the last `index` or `mail_index_rebuild` call. Run `uv run macpilot-mcp index` again to catch up.
- Only the 15 tools in the table are exposed. The vendored projects contain more tools that this server does not register.
- Sending needs an account already configured in Mail. The server does not manage accounts or credentials.
- The first Calendar, Reminders or Contacts call can take a few seconds while the helper compiles.
- Large mailboxes produce a large index file and a slow first build.

## Development

```sh
uv sync
uv run ruff check src tests
uv run pytest -q
```

## License

GPL-3.0-or-later. The mail index code comes from [imdinu/apple-mail-mcp](https://github.com/imdinu/apple-mail-mcp), which is GPL-3.0-or-later. The mail write guard comes from [patrickfreyer/apple-mail-mcp](https://github.com/patrickfreyer/apple-mail-mcp), and the Calendar, Reminders and Contacts bridges come from [JonathanRReed/Apple-MCPs](https://github.com/JonathanRReed/Apple-MCPs); both are MIT. See `NOTICE.md` for the versions used.
