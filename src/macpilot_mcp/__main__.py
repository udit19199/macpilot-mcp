"""macpilot-mcp CLI — runtime-independent: stdio (default) or loopback HTTP."""

from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(prog="macpilot-mcp")
    sub = parser.add_subparsers(dest="cmd")

    serve = sub.add_parser("serve", help="run the MCP server (default)")
    serve.add_argument("--transport", default="stdio", choices=["stdio", "streamable-http"])
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--read-only", action="store_true")

    sub.add_parser("index", help="build FTS5 index from disk now")
    sub.add_parser("status", help="print index stats as JSON")
    rebuild = sub.add_parser("rebuild", help="force full re-index")
    rebuild.add_argument("--mailbox", default=None)

    args, _ = parser.parse_known_args(sys.argv[1:] or ["serve"])
    if args.cmd in (None, "serve"):
        import os

        if getattr(args, "read_only", False):
            os.environ["APPLE_MAIL_READ_ONLY"] = "true"
            os.environ["MACPILOT_SAFETY_PROFILE"] = "safe_readonly"
        from .server import mcp
        from .vendor_common.runtime import require_loopback_host

        if args.transport == "streamable-http":
            mcp.run(
                transport="streamable-http",
                host=require_loopback_host("127.0.0.1"),
                port=args.port,
            )
        else:
            mcp.run()
    elif args.cmd == "index":
        from . import config as _cfg
        from .vendor_imdinu.index.manager import IndexManager

        _cfg.mirror_env_for_vendors()
        mgr = IndexManager()
        try:
            n = mgr.build_from_disk()
            print(f"indexed {n} emails -> {_cfg.get_index_path()}")
        finally:
            mgr.close()
    elif args.cmd == "status":
        import json

        from . import config as _cfg
        from .vendor_imdinu.index.manager import IndexManager

        _cfg.mirror_env_for_vendors()
        mgr = IndexManager()
        try:
            s = mgr.get_stats()
            print(json.dumps(s.__dict__, indent=2, default=str))
        finally:
            mgr.close()
    elif args.cmd == "rebuild":
        from . import config as _cfg
        from .vendor_imdinu.index.manager import IndexManager

        _cfg.mirror_env_for_vendors()
        mgr = IndexManager()
        try:
            n = mgr.rebuild(mailbox=args.mailbox)
            print(f"rebuilt {n} emails")
        finally:
            mgr.close()


if __name__ == "__main__":
    main()
