"""Apple Mail MCP - Modular package."""

__version__ = "3.2.1"

from macpilot_mcp.vendor_freyer.server import mcp

# UI availability flag
try:
    from ui import create_inbox_dashboard_ui

    UI_AVAILABLE = True
except ImportError:
    UI_AVAILABLE = False

# Import all tool modules to register @mcp.tool() decorators
from macpilot_mcp.vendor_freyer.tools import inbox  # noqa: F401  (5 tools)
from macpilot_mcp.vendor_freyer.tools import search  # noqa: F401  (2 tools)
from macpilot_mcp.vendor_freyer.tools import compose  # noqa: F401  (5 tools)
from macpilot_mcp.vendor_freyer.tools import manage  # noqa: F401  (5 tools)
from macpilot_mcp.vendor_freyer.tools import analytics  # noqa: F401  (4 tools)
from macpilot_mcp.vendor_freyer.tools import smart_inbox  # noqa: F401  (3 tools)
from macpilot_mcp.vendor_freyer.tools import raw_source  # noqa: F401  (1 tool)
