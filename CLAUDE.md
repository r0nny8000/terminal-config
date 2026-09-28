# Guidelines

Conventions for working in this repo. What the project is and how to run it:
`README.md`. Why anything is the way it is: `git log`.

## Before changing anything

Check whether the choice was already settled, and by which commit:

    git log --grep='^Decision:' --format='%h %s%n  %b'

If a change contradicts one, say so and argue the reversal in the commit body.
Do not quietly undo it.

## Commits

- Subject: `type: what changed`. Body: why — the problem, the reasoning, and the
  experience that led here.
- `Ruled out: …` for an alternative that looks better at a glance.
- `Decision: …` as a one-line trailer when the commit settles something
  non-obvious. That trailer is what keeps the history searchable.
- Routine changes need a subject only. Adding a tool is not a decision.
- One concern per commit. Copying files and editing them are two commits, so the
  deliberate change stays visible in the diff.

## Code

- Adding a tool is one row in `TOOLS` in `deploy.py`: `"name": (brew, apt)`.
  `None` means that platform cannot supply it or already has it.
- Never use `~` in a pyinfra path. Paths are single-quoted and never expanded;
  build them from the `Home` fact.
- Runtime tool probing (`bat` vs `batcat`) belongs in the fish function that needs
  it, not in `deploy.py`. The installer does not track binary names.
- Tool initialisation goes in `fish/conf.d/`, guarded with `command -q`.
- Machine-specific values and secrets go in `~/.config/fish/config.local.fish`,
  which is outside this repo and never tracked.

## Done means verified

Not done until `pyinfra @local deploy.py --dry` is clean and a second full run
reports zero changes. The commands are in `README.md`.
