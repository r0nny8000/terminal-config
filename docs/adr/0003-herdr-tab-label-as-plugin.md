# 3. herdr tab label: a repo-installed Claude Code plugin

Status: accepted
Date: 2026-10-20

## Context

Each Claude Code session runs in its own herdr tab, and the tabs should be
told apart by the name given with `/rename`. herdr does not know that name.

What the pieces offer, checked on the Pi with herdr 0.9.5 and Claude Code
2.1.304:

- `/rename` appends `{"type":"custom-title","customTitle":"…"}` to the
  session's `.jsonl` transcript. It fires no hook of its own.
- Hooks receive `transcript_path` on stdin, and `SessionStart` and
  `UserPromptSubmit` fire in interactive sessions and under `claude -p`,
  including `--resume`. Panes carry `HERDR_TAB_ID`.
- `herdr tab get <id>` returns the label as JSON; `herdr tab rename <id>
  <label>` sets it.
- Claude Code rewrites `~/.claude/settings.json` itself, so a deploy that
  owns or merges that file fights with it.

herdr's own Claude integration (`herdr integration install claude`) reports
agent state to herdr; it does not set labels. It is installed in the same step
because the deploy is where Claude-related setup now lives.

## Decision

This repo ships a local marketplace in `claude/` with one plugin,
`herdr-tab-label`. Its hook runs on `SessionStart` and `UserPromptSubmit`,
reads the last `custom-title` from the transcript and renames the tab when
the label differs. `deploy.py`, only where `claude` is installed, adds the
marketplace, installs the plugin and runs `herdr integration install claude`,
each gated on its listing so a second run declares nothing.

A rename reaches the tab on the next prompt or resume, not instantly. The
`/rename` name always wins over a tab named by hand.

## Alternatives

| Alternative                                     | Why not                                                                                  |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Hook entry in `~/.claude/settings.json`         | deploy.py would have to merge a file Claude rewrites; every run risks clobbering it     |
| Link `~/.claude/settings.json` into the repo    | Claude's own writes would dirty the checkout, and machine settings would become shared   |
| Fish wrapper that renames the tab at launch     | Only sees the name before the session starts; a `/rename` later never reaches the tab    |
| Set the label from the status line command      | Runs on every redraw and is meant for display, not side effects                          |

## Rationale

- A plugin is Claude Code's own unit for shipping hooks: it installs, lists
  and uninstalls through `claude plugin`, and its hooks live in the repo,
  not in a settings file Claude owns.
- Under `@local` the marketplace is read from this checkout in place, so an
  edit to the hook is live, like the fish functions.

## Revisit when

- Claude Code fires a hook on `/rename`: add it to `hooks.json` so the label
  follows at once.
- herdr's Claude integration starts setting labels itself.
