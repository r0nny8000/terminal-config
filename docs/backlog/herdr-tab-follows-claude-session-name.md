---
status: needs-rework
priority: medium
acceptance:
  - deploy.py installs the hook together with herdr, only when Claude Code is on the system
  - After `/rename foo` and one prompt, `herdr tab get $HERDR_TAB_ID` shows `"label":"foo"`
  - `pyinfra @local deploy.py --dry` is clean and a second full run reports zero changes
---

# herdr tab label follows the Claude Code session name

> REWORK THIS PLAN BEFORE STARTING. It was drafted as a one-off change to
> `~/.claude/` on one machine. The hook must instead be installed by this repo,
> together with herdr, whenever Claude Code is available on the system. Files,
> deploy steps and tests below still assume the one-off version.

## Goal

When a Claude session is renamed with `/rename`, the herdr tab it runs in gets
the same label automatically. No manual `prefix+shift+t`.

## Findings (checked with herdr 0.9.5, 2026-10-20)

| Check                                  | Result                                                                                                                       |
|----------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| herdr docs (`llms-full.txt`), CLI help | No setting to derive a tab label from the agent. Tabs are renamed manually or via `herdr tab rename <tab_id> <label>`.       |
| Where `/rename` is stored              | Claude Code appends `{"type":"custom-title","customTitle":"…"}` to the session `.jsonl` transcript.                          |
| Pane environment                       | Panes get `HERDR_TAB_ID` (e.g. `wJ:t2`), so a hook knows its own tab.                                                        |
| Claude's terminal title (OSC 0/2)      | Auto-generated topic summary, not the `/rename` name. herdr's `{terminal_title}` token cannot be used.                       |

## Draft plan (one-off version, to be reworked)

- Script `~/.claude/hooks/herdr-tab-from-session-name.py`: read hook JSON from
  stdin, take the last `custom-title` entry from `transcript_path`, run
  `herdr tab rename $HERDR_TAB_ID "<name>"` when it differs from the current
  label. No-op outside herdr or for unnamed sessions.
- Register it in `~/.claude/settings.json` under `UserPromptSubmit` and
  `SessionStart` (so a resumed named session also syncs).
- Tests: pytest, herdr call mocked.

## Open points for the rework

- Where the script lives in this repo, and how `deploy.py` detects Claude Code
  and merges the hook into `~/.claude/settings.json` without clobbering hooks
  that are already there (including herdr's own `herdr-agent-state.sh`).
- Idempotency: a second deploy run must report zero changes.

## Risks

| Risk                                        | Effect                                                   |
|---------------------------------------------|----------------------------------------------------------|
| `/rename` likely fires no hook (unverified) | Tab updates on the next prompt, not instantly.           |
| Several Claude panes in one tab             | The last pane to fire wins.                              |
| Manually named tab                          | Overwritten as soon as the session has a `/rename` name. |

## Related

- `herdr integration status` reported the Claude integration as outdated
  (v10 < v11) on the work Mac. `herdr integration install claude` fixes it;
  worth handling in the same deploy step.
