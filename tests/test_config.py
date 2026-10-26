"""Config must mirror MACPILOT_* onto APPLE_MAIL_* before vendor use.

Regression: instantiating IndexManager without mirror silently targets the
vendor-default path instead of ~/.macpilot-mcp/index.db.
"""

import os

from macpilot_mcp import config as C


def test_mirror_sets_vendor_path(tmp_path, monkeypatch):
    monkeypatch.setenv("MACPILOT_INDEX_PATH", str(tmp_path / "m.db"))
    monkeypatch.delenv("APPLE_MAIL_INDEX_PATH", raising=False)
    C.mirror_env_for_vendors()
    assert os.environ["APPLE_MAIL_INDEX_PATH"] == str(tmp_path / "m.db")
    assert C.get_index_path() == tmp_path / "m.db"


def test_default_path_is_macpilot(monkeypatch):
    monkeypatch.delenv("MACPILOT_INDEX_PATH", raising=False)
    monkeypatch.delenv("APPLE_MAIL_INDEX_PATH", raising=False)
    assert C.get_index_path().parent.name == ".macpilot-mcp"
