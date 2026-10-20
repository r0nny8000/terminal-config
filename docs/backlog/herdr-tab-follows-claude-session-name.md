---
status: planned
priority: medium
acceptance:
  - deploy.py installs the herdr-tab-label plugin and herdr's Claude integration, only when Claude Code is on the system
  - After `/rename foo` and one prompt, `herdr tab get $HERDR_TAB_ID` shows `"label":"foo"`
  - A fresh bootstrap as andre, without Claude Code, installs no plugin and deploys cleanly
  - On the Mac, the user runs the `/rename` check from a pushed commit and the tab follows
  - `uv run --with pytest pytest` is green
  - `pyinfra @local deploy.py --dry` is clean and a second full run reports zero changes
---

# herdr tab label follows the Claude Code session name

## Goal

When a Claude session is renamed with `/rename`, the herdr tab it runs in gets
the same label automatically. No manual `prefix+shift+t`. This repo installs the
hook together with herdr, on every machine that has Claude Code.

## Findings

Checked on the Pi with herdr 0.9.5 and Claude Code 2.1.304, 2026-10-20.

| Check                                  | Result                                                                                                                 |
|----------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| herdr docs (`llms-full.txt`), CLI help | No setting to derive a tab label from the agent. Tabs are renamed manually or via `herdr tab rename <tab_id> <label>`. |
| Where `/rename` is stored              | The session `.jsonl` transcript gets `{"type":"custom-title","customTitle":"…","sessionId":"…"}`, once per rename.     |
| Pane environment                       | Panes get `HERDR_TAB_ID` (e.g. `w9:t1`). `herdr tab get` returns the tab's current `label`.                            |
| Claude's terminal title (OSC 0/2)      | Auto-generated topic summary, not the `/rename` name. herdr's `{terminal_title}` token cannot be used.                 |
| `~/.claude/settings.json` on the Pi    | No hooks at all. Claude writes this file itself (`model`, `theme`, `enabledPlugins`), so the repo must not own it.     |
| herdr's Claude integration             | Pi: "not installed" (`~/.claude/hooks/herdr-agent-state.sh`). Work Mac: outdated (v10 < v11).                          |
| Claude Code plugins                    | `claude plugin marketplace add <path>` and `claude plugin install` exist; goal-definer already runs from a local path. |
| Test setup in this repo                | None yet: no `tests/`, no pytest config.                                                                               |

## Approach

Ship the hook as a Claude Code plugin from a local marketplace inside this repo.
Claude loads the plugin's hooks itself, so deploy.py never edits
`~/.claude/settings.json` and cannot clobber hooks that are already there.

Ruled out: merging the hook into `~/.claude/settings.json` from deploy.py. Claude
rewrites that file on its own, so an idempotent merge needs custom JSON code and
still races with Claude and with herdr's own installer.

Record this choice as `docs/adr/0003-claude-hooks-ship-as-a-plugin.md`.

## Step 1: verify before building

- A plugin's `hooks/hooks.json` runs on this Claude Code version, and
  `${CLAUDE_PLUGIN_ROOT}` resolves in its command. Check with a throwaway hook
  and `claude plugin validate`.
- Whether `/rename` fires any hook. If one does, add it to the hook events and
  drop the "next prompt" risk. If not, keep `UserPromptSubmit` and `SessionStart`.
- What `herdr integration status` prints for an installed, current Claude
  integration, so deploy.py can gate on it.

## Files

| File                                                | Purpose                                                                  |
|-----------------------------------------------------|--------------------------------------------------------------------------|
| `claude/.claude-plugin/marketplace.json`            | Local marketplace listing the plugin                                     |
| `claude/herdr-tab-label/.claude-plugin/plugin.json` | Plugin manifest                                                          |
| `claude/herdr-tab-label/hooks/hooks.json`           | Registers the script on `UserPromptSubmit` and `SessionStart`            |
| `claude/herdr-tab-label/hooks/herdr-tab-label.py`   | Reads hook JSON from stdin, renames the tab                              |
| `tests/test_herdr_tab_label.py`                     | pytest, herdr call mocked                                                |
| `deploy.py`                                         | Copies the marketplace for remote hosts, installs plugin and integration |
| `README.md`                                         | Mention the plugin and how to run the tests                              |
| `docs/adr/0003-claude-hooks-ship-as-a-plugin.md`    | Why a plugin, not a settings.json merge                                  |

## Script behaviour

- Read `transcript_path` from the hook JSON and take the last `custom-title`
  entry.
- Run `herdr tab rename $HERDR_TAB_ID "<name>"` when it differs from the label
  `herdr tab get` reports. A tab named by hand is overwritten; that is accepted.
- No-op, exit 0, outside herdr (`HERDR_TAB_ID` unset), for unnamed sessions, or
  when herdr fails. A hook must never block a prompt.

## Deploy steps

All gated on the existing `Which claude` fact; without Claude nothing here runs.

- Marketplace source: `DEPLOY_DIR/claude` under `@local`, otherwise copied to
  `link_base/claude` with `files.sync`, like the fish entries.
- `claude plugin marketplace add` and `claude plugin install`, each declared only
  when `claude plugin marketplace list` and `claude plugin list` do not already
  show it. That keeps the second run at zero changes.
- `herdr integration install claude`, declared only when
  `herdr integration status` does not report it installed and current. Works for
  both Homebrew herdr (Mac) and the release binary (Debian).

## Tests

- pytest in `tests/`, run with `uv run --with pytest pytest`.
- Cases: named session renames the tab; same label already set makes no call;
  unnamed session, missing `HERDR_TAB_ID` and a failing herdr all exit 0 without
  renaming; with several renames the last `custom-title` wins.

## Risks

| Risk                                    | Effect                                                                         |
|-----------------------------------------|--------------------------------------------------------------------------------|
| `/rename` fires no hook (step 1 checks) | Tab updates on the next prompt, not instantly.                                 |
| Several Claude panes in one tab         | The last pane to fire wins.                                                    |
| Manually named tab                      | Overwritten as soon as the session has a `/rename` name. Accepted.             |
| Mac: `python` comes from pyenv          | The hook fails if pyenv's shims are not on Claude's PATH. Mac check covers it. |
| Plugin hooks unsupported or changed     | Step 1 catches it before any deploy code is written.                           |

## Checklist

- [ ] Step 1 verifications done, plan adjusted to the results
- [ ] Failing tests written in `tests/`
- [ ] Plugin and script written, tests green
- [ ] deploy.py steps added
- [ ] ADR 0003 and README updated
- [ ] Pi: `/rename foo` plus one prompt shows `"label":"foo"`
- [ ] andre: fresh bootstrap without Claude Code deploys cleanly, no plugin
- [ ] Mac: user check from a pushed commit
- [ ] `pyinfra @local deploy.py --dry` clean, second full run zero changes
