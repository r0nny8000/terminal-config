"""
Sets the herdr tab label to the Claude Code session's /rename name.

/rename fires no hook of its own; it appends a custom-title line to the session
transcript. So this runs on SessionStart and UserPromptSubmit and reads the last
such line: a rename shows up in the tab on the next prompt or resume.

Standard library only, and it always exits 0: a broken label must never block a
prompt or a session start.
"""

import json
import os
import subprocess
import sys


def session_name(transcript_path):
    name = None
    with open(transcript_path, encoding="utf-8") as transcript:
        for line in transcript:
            # The substring test skips parsing every message of a long session.
            if '"custom-title"' not in line:
                continue
            entry = json.loads(line)
            if entry.get("type") == "custom-title" and entry.get("customTitle"):
                name = entry["customTitle"]
    return name


def main():
    tab_id = os.environ.get("HERDR_TAB_ID")
    if not tab_id:
        return
    name = session_name(json.load(sys.stdin)["transcript_path"])
    if not name:
        return
    tab = subprocess.run(
        ["herdr", "tab", "get", tab_id], capture_output=True, text=True, check=True
    )
    if json.loads(tab.stdout)["result"]["tab"]["label"] == name:
        return
    subprocess.run(["herdr", "tab", "rename", tab_id, name], capture_output=True, check=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
