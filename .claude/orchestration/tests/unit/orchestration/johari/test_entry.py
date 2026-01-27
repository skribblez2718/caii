"""
Unit tests for johari/entry.py

Tests the Johari Window protocol entry point.
"""

import sys

import pytest


class TestJohariLoadProtocolContent:
    """Tests for load_protocol_content() function."""

    @pytest.mark.unit
    def test_returns_string(self):
        """Should return a string."""
        from orchestration.johari.entry import load_protocol_content

        result = load_protocol_content()

        assert isinstance(result, str)

    @pytest.mark.unit
    def test_returns_protocol_content_when_exists(self, tmp_path, monkeypatch):
        """Should return content from protocol.md when it exists."""
        from orchestration.johari import entry

        # Create mock protocol file
        protocol_file = tmp_path / "protocol.md"
        protocol_file.write_text("# Johari Protocol Content")

        monkeypatch.setattr(entry, "CONTENT_DIR", tmp_path)

        result = entry.load_protocol_content()

        assert "Johari Protocol Content" in result

    @pytest.mark.unit
    def test_returns_empty_when_missing(self, tmp_path, monkeypatch):
        """Should return empty string when protocol.md doesn't exist."""
        from orchestration.johari import entry

        monkeypatch.setattr(entry, "CONTENT_DIR", tmp_path)

        result = entry.load_protocol_content()

        assert result == ""


class TestJohariEntryMain:
    """Tests for main() function."""

    @pytest.mark.unit
    def test_exits_without_args(self, monkeypatch, capsys):
        """Should exit with error when no arguments provided."""
        from orchestration.johari.entry import main

        monkeypatch.setattr(sys, "argv", ["entry.py"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Usage" in captured.err

    @pytest.mark.unit
    def test_prints_johari_header(self, tmp_path, monkeypatch, capsys):
        """Should print JOHARI WINDOW DISCOVERY header."""
        from orchestration.johari import entry

        monkeypatch.setattr(entry, "CONTENT_DIR", tmp_path)
        monkeypatch.setattr(sys, "argv", ["entry.py", "Test context"])

        entry.main()

        captured = capsys.readouterr()
        assert "JOHARI WINDOW DISCOVERY" in captured.out

    @pytest.mark.unit
    def test_prints_context(self, tmp_path, monkeypatch, capsys):
        """Should print the provided context."""
        from orchestration.johari import entry

        monkeypatch.setattr(entry, "CONTENT_DIR", tmp_path)
        monkeypatch.setattr(
            sys, "argv", ["entry.py", "Build an API with REST endpoints"]
        )

        entry.main()

        captured = capsys.readouterr()
        assert "Build an API" in captured.out

    @pytest.mark.unit
    def test_prints_share_probe_map_deliver(self, tmp_path, monkeypatch, capsys):
        """Should print the SHARE/PROBE/MAP/DELIVER framework."""
        from orchestration.johari import entry

        monkeypatch.setattr(entry, "CONTENT_DIR", tmp_path)
        monkeypatch.setattr(sys, "argv", ["entry.py", "Context"])

        entry.main()

        captured = capsys.readouterr()
        assert "SHARE:" in captured.out
        assert "PROBE:" in captured.out
        assert "MAP:" in captured.out
        assert "DELIVER:" in captured.out

    @pytest.mark.unit
    def test_includes_ask_user_question_instruction(
        self, tmp_path, monkeypatch, capsys
    ):
        """Should instruct to use AskUserQuestion tool."""
        from orchestration.johari import entry

        monkeypatch.setattr(entry, "CONTENT_DIR", tmp_path)
        monkeypatch.setattr(sys, "argv", ["entry.py", "Context"])

        entry.main()

        captured = capsys.readouterr()
        assert "AskUserQuestion" in captured.out

    @pytest.mark.unit
    def test_truncates_long_context(self, tmp_path, monkeypatch, capsys):
        """Should truncate very long context strings."""
        from orchestration.johari import entry

        monkeypatch.setattr(entry, "CONTENT_DIR", tmp_path)
        long_context = "x" * 500
        monkeypatch.setattr(sys, "argv", ["entry.py", long_context])

        entry.main()

        captured = capsys.readouterr()
        # Context should be truncated (300 chars + "...")
        assert "..." in captured.out
