---
priority: low
assignee: none
due: none
acceptance criteria: herdr's agent sidebar shows the current Claude model for each Claude pane, follows /model switches, and a second deploy run reports zero changes
---

# Show the Claude model in herdr's agent sidebar

Undecided whether this is needed at all. The model already shows in the
Claude Code status line (`~/.claude/settings.json`, untracked).

## How it would work

herdr 0.9.5 supports custom `$name` tokens in `ui.sidebar.agents.rows`,
filled by `herdr pane report-metadata "$HERDR_PANE_ID" --source … --token
model=…`. herdr's configuration docs use `$model` as their own example.
Claude panes carry `HERDR_PANE_ID`.

## Options analysed (2026-11-16)

| Approach                     | Model source                                           | Follows /model | Effort | Weak spot                                                                                         |
| ---------------------------- | ------------------------------------------------------ | -------------- | ------ | ------------------------------------------------------------------------------------------------- |
| A. Plugin hooks in this repo | `SessionStart.model`, then `PostModelSwitch.to_model`  | yes            | no     | `SessionStart.model` can be absent (after /clear, recovery); raw IDs need shortening               |
| B. Status line reports too   | `model.display_name`, `effort.level` on each refresh   | yes            | yes    | lives in untracked `~/.claude/settings.json` (see ADR 0003); a herdr call per refresh unless cached |
| C. Both                      | hooks for model, status line for effort                | yes            | yes    | two moving parts for one display                                                                  |

Leaning towards A: a second plugin in the `claude/` marketplace next to
`herdr-tab-label`, installed by `deploy.py`, same pattern as ADR 0003.
Unverified: falling back to the `model` field of the transcript's last
assistant message when `SessionStart.model` is missing.

## Open decisions

- Approach: A, B or C
- Format: `opus-5-5`, `opus`, or the full model ID
- Position: after the agent name in row 2, or a row of its own

## Sources

- herdr v0.9.5 docs: `configuration.mdx`, `cli-reference.mdx` (report-metadata)
- Claude Code hooks docs: SessionStart input, PostModelSwitch (needs v2.1.251+)
- `~/.claude/hooks/herdr-agent-state.sh` is herdr-managed and overwritten on
  reinstall, so it is not the place for this
