"""
Runs the herdr-tab-label hook as Claude Code does — a hook JSON on stdin — with
a fake herdr first on PATH that records its calls.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "claude" / "herdr-tab-label" / "hooks" / "tab_label.py"

# Answers `tab get` with the label in $FAKE_LABEL, appends every call to
# $FAKE_LOG, and fails everything when $FAKE_FAIL is set.
FAKE_HERDR = """#!/bin/sh
echo "$*" >> "$FAKE_LOG"
[ -n "$FAKE_FAIL" ] && { echo '{"error":{"code":"boom"}}'; exit 1; }
if [ "$1 $2" = "tab get" ]; then
    printf '{"result":{"tab":{"label":"%s","tab_id":"%s"}}}\\n' "$FAKE_LABEL" "$3"
fi
"""


def run(tmp_path, titles, label="old", tab_id="w1:t1", fail=False):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    herdr = bin_dir / "herdr"
    herdr.write_text(FAKE_HERDR)
    herdr.chmod(0o755)

    transcript = tmp_path / "session.jsonl"
    lines = [{"type": "user", "message": {"content": "hi"}}]
    lines += [{"type": "custom-title", "customTitle": t, "sessionId": "s"} for t in titles]
    transcript.write_text("".join(json.dumps(line) + "\n" for line in lines))

    log = tmp_path / "herdr.log"
    env = {
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "FAKE_LOG": str(log),
        "FAKE_LABEL": label,
    }
    if tab_id:
        env["HERDR_TAB_ID"] = tab_id
    if fail:
        env["FAKE_FAIL"] = "1"

    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps({"session_id": "s", "transcript_path": str(transcript)}),
        env=env,
        capture_output=True,
        text=True,
    )
    calls = log.read_text().splitlines() if log.exists() else []
    return result, calls


def test_named_session_renames_the_tab(tmp_path):
    result, calls = run(tmp_path, ["my session"])
    assert result.returncode == 0
    assert calls == ["tab get w1:t1", "tab rename w1:t1 my session"]


def test_matching_label_makes_no_rename_call(tmp_path):
    result, calls = run(tmp_path, ["same"], label="same")
    assert result.returncode == 0
    assert calls == ["tab get w1:t1"]


def test_unnamed_session_leaves_the_tab_alone(tmp_path):
    result, calls = run(tmp_path, [])
    assert result.returncode == 0
    assert calls == []


def test_unset_herdr_tab_id_leaves_the_tab_alone(tmp_path):
    result, calls = run(tmp_path, ["my session"], tab_id=None)
    assert result.returncode == 0
    assert calls == []


def test_failing_herdr_exits_zero_without_renaming(tmp_path):
    result, calls = run(tmp_path, ["my session"], fail=True)
    assert result.returncode == 0
    assert not any(call.startswith("tab rename") for call in calls)


def test_last_custom_title_wins(tmp_path):
    result, calls = run(tmp_path, ["first", "second", "third"])
    assert result.returncode == 0
    assert calls[-1] == "tab rename w1:t1 third"
