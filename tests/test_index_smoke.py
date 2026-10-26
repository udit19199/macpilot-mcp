"""Index smoke — schema + FTS5 work without touching real Mail."""

from macpilot_mcp.vendor_imdinu.index.schema import init_database


def test_schema_init_and_fts(tmp_path):
    db = tmp_path / "t.db"
    conn = init_database(db)
    conn.execute(
        "INSERT INTO emails (message_id, account, mailbox, subject, sender, content,"
        " date_received, emlx_path) VALUES (1,'a','INBOX','hello','b@c','world body',"
        " '2026-01-01', '/tmp/x.emlx')"
    )
    conn.commit()
    row = conn.execute(
        "SELECT subject FROM emails_fts WHERE emails_fts MATCH 'hello'"
    ).fetchone()
    assert row and row[0] == "hello"
    conn.close()
