"""Tests for tools/vault_write.py. Run with: python -m pytest tests/"""

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "vault_write.py"
sys.path.insert(0, str(SCRIPT.parent))
import vault_write  # noqa: E402


def run(vault, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        env={"HERMES_VAULT": str(vault), "PATH": ""},
        capture_output=True, text=True,
    )


def note_id(stdout):
    return stdout.strip().split("id=")[1].rstrip(")")


@pytest.fixture
def vault(tmp_path):
    return tmp_path / "vault"


def test_create_writes_frontmatter(vault):
    r = run(vault, "create", "--folder", "Goals", "--title", "Learn basic color theory",
            "--field", "goal=DaVinci mastery", "--field", "status=not-started",
            "--field", "priority=med", "--agent", "task-manager", "--body", "First step.")
    assert r.returncode == 0, r.stderr
    fields, body = vault_write.parse_note(vault / "Goals" / "learn-basic-color-theory.md")
    assert fields["status"] == "not-started"
    assert fields["agent"] == "task-manager"
    assert fields["created"] == fields["updated"]
    assert body.strip() == "First step."


def test_create_rejects_missing_required_fields(vault):
    r = run(vault, "create", "--folder", "Goals", "--title", "Incomplete",
            "--field", "goal=Something", "--agent", "task-manager")
    assert r.returncode != 0
    assert "priority" in r.stderr and "status" in r.stderr
    assert not (vault / "Goals" / "incomplete.md").exists()


def test_create_refuses_duplicates(vault):
    args = ("create", "--folder", "Research", "--title", "Same topic",
            "--field", "topic=x", "--agent", "researcher")
    assert run(vault, *args).returncode == 0
    r = run(vault, *args)
    assert r.returncode != 0 and "use 'update'" in r.stderr


def test_update_changes_only_given_fields_and_keeps_lists(vault):
    r = run(vault, "create", "--folder", "Goals", "--title", "Grade a short scene",
            "--field", "goal=DaVinci mastery", "--field", "status=not-started",
            "--field", "priority=high", "--field", "blocked_by=a1b2c3d4,e5f6a7b8",
            "--agent", "task-manager", "--body", "Use the node graph.")
    nid = note_id(r.stdout)
    r = run(vault, "update", "--folder", "Goals", "--id", nid,
            "--field", "status=in-progress", "--agent", "secretary")
    assert r.returncode == 0, r.stderr
    fields, body = vault_write.parse_note(vault / "Goals" / "grade-a-short-scene.md")
    assert fields["status"] == "in-progress"
    assert fields["priority"] == "high"
    assert fields["blocked_by"] == ["a1b2c3d4", "e5f6a7b8"]
    assert fields["agent"] == "secretary"
    assert body.strip() == "Use the node graph."


def test_values_with_colons_and_quotes_round_trip(vault):
    reason = 'Source says "2024": not 2023'
    r = run(vault, "create", "--folder", "Validation", "--title", "Check claim",
            "--field", "verdict=rejected", "--field", "target=abcd1234",
            "--field", f"reasons={reason}", "--agent", "validator")
    assert r.returncode == 0, r.stderr
    fields, _ = vault_write.parse_note(vault / "Validation" / "check-claim.md")
    assert fields["reasons"] == reason


def test_unknown_folder_is_rejected(vault):
    r = run(vault, "create", "--folder", "Random", "--title", "x", "--agent", "coder")
    assert r.returncode != 0
