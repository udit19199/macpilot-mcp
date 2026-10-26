"""File-guard tests — denylist must hold even if allowlists widen."""

from macpilot_mcp.safety import validate_write_path


def test_ssh_always_denied():
    resolved, err = validate_write_path("~/.ssh/config")
    assert resolved is None and err is not None


def test_env_dotfile_denied():
    resolved, err = validate_write_path("~/.env")
    assert resolved is None and err is not None


def test_downloads_allowed():
    resolved, err = validate_write_path("~/Downloads/macpilot-test.txt")
    assert err is None and resolved is not None
