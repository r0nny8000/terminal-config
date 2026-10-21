"""
Sources fish/conf.d/herdr-tab.fish in a clean fish and fires one prompt event,
with a fake herdr first on PATH that records its calls.
"""

import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "fish" / "conf.d" / "herdr-tab.fish"

# Answers `tab get` with the label in $FAKE_LABEL, appends every call to
# $FAKE_LOG, and fails everything when $FAKE_FAIL is set.
FAKE_HERDR = """#!/bin/sh
echo "$*" >> "$FAKE_LOG"
[ -n "$FAKE_FAIL" ] && { echo '{"error":{"code":"boom"}}'; echo boom >&2; exit 1; }
if [ "$1 $2" = "tab get" ]; then
    printf '{"result":{"tab":{"label":"%s","tab_id":"%s"}}}\\n' "$FAKE_LABEL" "$3"
fi
"""


def run(tmp_path, label="old", tab_id="w1:t1", fail=False):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    herdr = bin_dir / "herdr"
    herdr.write_text(FAKE_HERDR)
    herdr.chmod(0o755)
    project = tmp_path / "my-project"
    project.mkdir()

    log = tmp_path / "herdr.log"
    # Built from scratch, not os.environ: the tests may run inside a real herdr
    # pane, whose HERDR_TAB_ID must not leak in.
    env = {
        "PATH": f"{bin_dir}:/usr/bin:/bin:/opt/homebrew/bin",
        "HOME": str(tmp_path),
        "FAKE_LOG": str(log),
        "FAKE_LABEL": label,
    }
    if tab_id:
        env["HERDR_TAB_ID"] = tab_id
    if fail:
        env["FAKE_FAIL"] = "1"

    result = subprocess.run(
        ["fish", "--no-config", "-c", f"source {SCRIPT}; emit fish_prompt"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
    )
    calls = log.read_text().splitlines() if log.exists() else []
    return result, calls


def test_prompt_renames_the_tab_to_the_folder_name(tmp_path):
    result, calls = run(tmp_path)
    assert result.returncode == 0
    assert calls == ["tab get w1:t1", "tab rename w1:t1 my-project"]


def test_matching_label_makes_no_rename_call(tmp_path):
    result, calls = run(tmp_path, label="my-project")
    assert result.returncode == 0
    assert calls == ["tab get w1:t1"]


def test_outside_herdr_leaves_tabs_alone(tmp_path):
    result, calls = run(tmp_path, tab_id=None)
    assert result.returncode == 0
    assert calls == []


def test_failing_herdr_prints_nothing(tmp_path):
    result, calls = run(tmp_path, fail=True)
    assert result.stdout == ""
    assert result.stderr == ""
