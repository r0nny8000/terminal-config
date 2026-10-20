---
status: open
priority: medium
acceptance: On the Mac, inside herdr, `/rename <name>` in a Claude session followed by one prompt sets the herdr tab label to <name>; pytest stays green; a second `./bootstrap.sh` reports zero changes
---

# Fix: herdr tab label does not follow /rename on the Mac

Handover for a Claude session on the Mac. Read this file, then work through
"Next steps" in order. Show each command's output.

## Goal

The `herdr-tab-label` plugin works on the Mac as it does on the Pi: after
`/rename <name>` and one more prompt, the herdr tab reads `<name>`.

## Background

- Branch `feat/herdr-tab-label`, pushed, not merged. Why the plugin exists and
  how it works: `docs/adr/0003-herdr-tab-label-as-plugin.md`.
- Plugin: `claude/herdr-tab-label/`. Hook script:
  `claude/herdr-tab-label/hooks/tab_label.py`, run by `hooks/hooks.json` as
  `python "${CLAUDE_PLUGIN_ROOT}/hooks/tab_label.py"` on `SessionStart` and
  `UserPromptSubmit`.
- What the script does: reads `HERDR_TAB_ID` from the environment and
  `transcript_path` from the hook JSON on stdin, takes the last
  `{"type":"custom-title","customTitle":…}` line from the transcript, runs
  `herdr tab get <id>`, reads `result.tab.label`, and runs
  `herdr tab rename <id> <name>` when they differ.
- It catches every exception and always exits 0, so a failure on the Mac is
  silent. That is deliberate (a broken label must never block a prompt); do
  not remove it to debug, call `main()` directly instead (step 3).
- Tests: `tests/test_tab_label.py`, run with `uv run --with pytest pytest -q`
  (6 tests, fake `herdr` on PATH).

## History

| When       | Where | What                                                                                           |
| ---------- | ----- | ---------------------------------------------------------------------------------------------- |
| 2026-10-20 | Pi    | Probed: plugin hooks fire with `${CLAUDE_PLUGIN_ROOT}`, also under `claude -p --resume`         |
| 2026-10-20 | Pi    | Probed: `/rename` fires no hook; it appends a `custom-title` line to the transcript             |
| 2026-10-20 | Pi    | Plugin, tests, deploy step built; end to end passed: tab went `terminal-conf` -> `probe-title`  |
| 2026-10-20 | Mac   | User ran the deploy: plugin `herdr-tab-label@terminal-config` enabled                           |
| 2026-10-20 | Mac   | `herdr integration status` reports `claude: current (v11)`; second run had zero changes         |
| 2026-10-20 | Mac   | New Claude session in herdr, `/rename mac-test`, one prompt: tab label did not change           |

Verified on the Pi only (herdr 0.9.5, Claude Code 2.1.304, Debian):

| Fact                                                                            | Checked on the Mac |
| ------------------------------------------------------------------------------- | ------------------ |
| Panes get `HERDR_TAB_ID`, e.g. `w9:t1`                                          | no                 |
| `herdr tab get <id>` prints `{"result":{"tab":{"label":…}}}`, exit 0            | no                 |
| `herdr tab rename <id> <label>` sets the label                                  | no                 |
| `/rename` writes `{"type":"custom-title","customTitle":"…"}` to the transcript  | no                 |
| `python` and `herdr` are on PATH for hooks                                      | no                 |

## Hypotheses

Ranked by likelihood; none is verified.

| Hypothesis                                                              | Why suspected                                                     | Test in step |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------- | ------------ |
| Mac herdr is older than 0.9.5: no `HERDR_TAB_ID`, or other `tab` JSON   | Commit 4d96847 recorded herdr 0.9.3 on the Mac; Homebrew, not pinned | 1, 3         |
| `python` not found by the hook                                          | Mac Python is pyenv; hooks run via a non-interactive shell        | 1, 4         |
| `herdr` not on the hook's PATH                                          | Homebrew's bin may be missing from Claude's environment           | 1, 4         |
| Mac Claude Code writes `/rename` differently                            | Version may differ from 2.1.304                                   | 2            |
| Hook does not fire at all                                               | Plugin enabled, but untested on the Mac                           | 4            |

## Next steps

Run in fish, inside a herdr pane. A Claude session running in herdr inherits
`HERDR_TAB_ID`, so its Bash tool can run these too. Note: every successful
rename changes the tab of the session you are in.

1. Environment facts:

       echo "tab=$HERDR_TAB_ID"
       herdr --version; claude --version
       command -v python herdr
       herdr tab get "$HERDR_TAB_ID"; echo "exit=$status"

2. The rename reached the transcript:

       grep -l mac-test ~/.claude/projects/*/*.jsonl
       grep -h '"custom-title"' ~/.claude/projects/*/*.jsonl | tail -3

3. The hook logic without its error wrapper, so a traceback shows. Run from
   the repo root:

       set t (grep -l mac-test ~/.claude/projects/*/*.jsonl | head -1)
       echo "{\"transcript_path\":\"$t\"}" | python -c 'import sys; sys.path.insert(0, "claude/herdr-tab-label/hooks"); import tab_label; tab_label.main()'
       herdr tab get "$HERDR_TAB_ID"

4. Only if step 3 renames the tab: check whether the hook runs inside Claude.

       claude --debug-file ~/hooks.log --debug=hooks

   In it: `/rename x2`, send `ok`, quit. Then:

       grep -i -B2 -A5 tab_label ~/hooks.log

   Delete `~/hooks.log` afterwards.

How to read the results:

| Result                                              | Fix direction                                                                 |
| --------------------------------------------------- | ----------------------------------------------------------------------------- |
| `tab=` empty, or `tab get` JSON differs             | herdr version: upgrade via `brew upgrade herdr`, or adapt the script to both  |
| No `custom-title` line                              | Find how this Claude version stores the name; adapt `session_name()`          |
| Step 3 traceback                                    | The traceback names the failing assumption; fix that                          |
| Step 3 works, step 4 shows `command not found`      | PATH in the hook: use an absolute interpreter or fix PATH, decide with user   |
| Step 3 works, step 4 shows no hook run              | Check `claude plugin list`, restart Claude, look at `/hooks`                  |

## Constraints

- Follow `CLAUDE.md` (repo) and the user's global instructions: test-first,
  plan before non-trivial edits, one concern per commit, `Decision:` trailer
  for anything non-obvious.
- If the script must change: first add a failing test in
  `tests/test_tab_label.py` that reproduces the Mac's behaviour (e.g. the
  Mac's `tab get` JSON in the fake herdr), then fix. Existing tests stay as
  they are; they encode the Pi's verified behaviour, which must keep working.
- The script stays stdlib-only and always exits 0.
- deploy.py never writes `~/.claude/settings.json`.
- If the fix is "upgrade herdr on the Mac" and needs no repo change, record
  that in this file's resolution and ask the user before deleting it.
- Commit on `feat/herdr-tab-label`. Ask before pushing; no merge.

## Done when

- [ ] Cause identified, shown by the output of the step that exposed it
- [ ] Fix in place (repo change with a new failing-then-green test, or a
      documented Mac-side change)
- [ ] `uv run --with pytest pytest -q` green
- [ ] Mac: new Claude session in herdr, `/rename <name>`, one prompt, then
      `herdr tab get "$HERDR_TAB_ID"` shows `<name>`
- [ ] Mac: `./bootstrap.sh` twice, the second run reports zero changes
- [ ] The user then re-checks the Pi end to end after pulling, if the script
      changed
