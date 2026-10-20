---
status: goal-ready
priority: medium
acceptance: On the Pi, a `claude -p --resume` of a named session inside herdr sets the tab label to the session name, pytest is green, and a second full deploy run reports zero changes
---

# Goal: herdr tab label follows the Claude Code session name

## Goal

On every machine with Claude Code, this repo installs a Claude Code plugin whose
hook keeps the herdr tab label equal to the session's `/rename` name, and
installs herdr's own Claude integration in the same step.

## Context

- Repo state: `main`, clean, `57bb1f6` (reworked plan, pushed). Work on branch
  `feat/herdr-tab-label`.
- Relevant files: `deploy.py` (`MANUAL` already checks `Which claude`; the herdr
  section links `herdr/config.toml`; remote hosts copy files under `link_base`),
  `README.md`, `docs/adr/` (0001, 0002 exist; next is 0003).
- Decisions to respect: `CLAUDE.md` (paths from the `Home` fact, never `~`; one
  concern per commit; `Decision:` trailer; done means a clean `--dry` and a
  zero-change second run). ADR 0002: release installs are pinned. Commit
  4d96847: only herdr's `config.toml` is linked, not `~/.config/herdr`.
- Verified facts (2026-10-20, Pi, herdr 0.9.5, Claude Code 2.1.304):
  - `/rename` writes `{"type":"custom-title","customTitle":"…","sessionId":"…"}`
    to the session `.jsonl` transcript, once per rename.
  - Panes get `HERDR_TAB_ID` (e.g. `w9:t1`); `herdr tab get <id>` returns JSON
    with `result.tab.label`; `herdr tab rename <id> <label>` sets it.
  - `~/.claude/settings.json` has no hooks; Claude rewrites it itself, so
    deploy.py must not own or merge it.
  - `herdr integration status` reports `claude: not installed
    (~/.claude/hooks/herdr-agent-state.sh)` on the Pi. The Mac is outdated
    (v10 < v11).
  - `claude plugin marketplace add|list` and `claude plugin install|list|validate`
    exist; goal-definer already runs from a local directory marketplace.
  - `uv run --with pytest pytest -q` runs and finds no tests (exit 5).
  - `pyinfra @local deploy.py --dry` is clean today.
- Not verified, check first: that plugin `hooks/hooks.json` runs on this
  version with `${CLAUDE_PLUGIN_ROOT}`; whether `claude -p --resume` fires
  `SessionStart`/`UserPromptSubmit`; whether `/rename` fires any hook; what
  `herdr integration status` prints when the integration is current.
- Files left by validation runs: none.

## Acceptance checklist

- [ ] Plugin is valid — proven by `claude plugin validate claude` exiting 0
- [ ] Hook script behaves — proven by `uv run --with pytest pytest -q` exiting 0, with tests for: named session renames; matching label makes no rename call; unnamed session, unset `HERDR_TAB_ID` and failing herdr all exit 0 without renaming; last `custom-title` wins
- [ ] Deploy installs plugin and integration — proven by `claude plugin list` showing `herdr-tab-label` enabled and `herdr integration status` reporting claude installed
- [ ] End to end on the Pi — proven by `claude -p --resume <id> "ok"` in a herdr pane, on a session whose transcript has a `custom-title`, followed by `herdr tab get "$HERDR_TAB_ID"` showing that label
- [ ] Idempotent — proven by `pyinfra @local deploy.py --dry` clean and a second `pyinfra @local deploy.py` reporting zero changes
- [ ] Decision recorded — proven by `ls docs/adr/0003-*` and `git log --grep='^Decision:' -1` naming the plugin approach

## Verification

Run, in order, and show each output in the transcript: `claude plugin validate
claude`, `uv run --with pytest pytest -q`, `pyinfra @local deploy.py`, then
`pyinfra @local deploy.py` again (zero changes), `claude plugin list`,
`herdr integration status`, the `claude -p --resume` run and `herdr tab get
"$HERDR_TAB_ID"`.

## Guardrails

- No test is deleted, skipped, or weakened to make a check pass.
- No edits outside `claude/`, `tests/`, `deploy.py`, `README.md`, `docs/adr/`,
  except this goal file (see "When done").
- deploy.py never writes `~/.claude/settings.json` itself; herdr's and Claude's
  own installers may.
- The hook script uses the Python standard library only and always exits 0.
- Git: commits on `feat/herdr-tab-label` only, one concern per commit, CLAUDE.md
  commit style. No push, no merge, no rebase of existing commits.
- If `claude -p` fires no hooks, use a direct call of the installed script with
  a hook JSON as the end-to-end check, and say so in the report.

## Out of scope

- The Mac check and the fresh bootstrap as andre: the user runs them after
  pushing the branch.
- Pushing or merging the branch.
- Other herdr integrations, bumping `HERDR`, cleaning up tmux leftovers.
- Preserving manually named tabs: the `/rename` name always wins.

## Approach hints

- Marketplace at `claude/.claude-plugin/marketplace.json`, plugin at
  `claude/herdr-tab-label/` with `hooks/hooks.json` and the script.
- Gate each deploy operation on a fact (`claude plugin marketplace list`,
  `claude plugin list`, `herdr integration status`) so the second run declares
  nothing.
- Settle the unverified points with a throwaway hook before writing deploy code.

## When done

Report what is done and what the user still has to check on the Mac and as
andre. Ask the user whether to delete this file. Deleting is fine: it stays in
git history if it was committed.

## Open questions

None

## Condition

```text
On branch feat/herdr-tab-label, this repo ships a Claude Code plugin (claude/herdr-tab-label, local marketplace in claude/) whose hook sets the herdr tab label to the session's last /rename name, and deploy.py installs it plus herdr's Claude integration only when Claude Code is present. Done when all hold, each shown by its command's output in the transcript: `claude plugin validate claude` exits 0; `uv run --with pytest pytest -q` exits 0 with tests for rename, no-op on matching label, unnamed session, unset HERDR_TAB_ID, failing herdr, last custom-title wins; after `pyinfra @local deploy.py`, `claude plugin list` shows herdr-tab-label enabled and `herdr integration status` reports claude installed; `claude -p --resume <id> "ok"` in a herdr pane on a session with a custom-title, then `herdr tab get "$HERDR_TAB_ID"`, shows that label (if -p fires no hooks, a direct call of the installed script instead, stated as such); `pyinfra @local deploy.py --dry` is clean and a second full run reports zero changes; docs/adr/0003-* exists and a commit carries a Decision: trailer for the plugin approach. Guardrails: no test deleted, skipped or weakened; edits only in claude/, tests/, deploy.py, README.md, docs/adr/ and docs/backlog/goal-herdr-tab-label.md; deploy.py never writes ~/.claude/settings.json; hook script is stdlib-only and always exits 0; commits on the branch only, one concern each, no push, merge or rebase. Out of scope: Mac check, andre bootstrap, pushing, other herdr integrations, preserving manual tab names. Read docs/backlog/goal-herdr-tab-label.md first. Or stop after 30 turns and report what remains.
```
