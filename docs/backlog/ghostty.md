---
status: planned
priority: low
depends-on: cage-foot.md (generalised config-link code in deploy.py)
acceptance:
  - On the Mac, `./bootstrap.sh` installs Ghostty and the 0xProto Nerd Font and links `~/.config/ghostty` into the repo.
  - The Application Support symlink into ghostty-config is gone; `readlink ~/.config/ghostty/config` points into terminal-config.
  - Ghostty looks as before the migration (font, TokyoNight Night, transparency, blur); `colors` shows a smooth gradient.
  - On Debian nothing Ghostty-related is installed or linked.
  - `./bootstrap.sh --dry` is clean and a second full run reports zero changes, on both machines.
  - Only then, and on the user's explicit go: GitHub repo r0nny8000/ghostty-config archived, local clones removed.
---

# Ghostty as the Mac's terminal, taken over from ghostty-config

## Goal

The Mac gets Ghostty, installed and configured by `deploy.py`, with Tokyo
Night referenced by name rather than copied in as hex values. The config
moves here from the separate ghostty-config repo, which is then archived.
foot remains the terminal for the Pi and other Debian machines (see
`cage-foot.md`).

## What was found (2026-10-04)

| Fact                                                                                                                                                | Checked with                                 |
| --------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| Ghostty is a Homebrew cask, version 1.3.1; there is no formula                                                                                      | formulae.brew.sh API (cask 200, formula 404) |
| The config's font comes from cask `font-0xproto-nerd-font` 3.5.1                                                                                    | formulae.brew.sh API                         |
| pyinfra 3.10.0 has `brew.casks`                                                                                                                     | `dir(pyinfra.operations.brew)`               |
| `TOOLS` in `deploy.py` installs formulae only                                                                                                       | `deploy.py`, `brew.packages` call            |
| Ghostty reads `~/.config/ghostty/config` on macOS, then Application Support; later wins                                                             | ghostty.org/docs/config                      |
| Built-in theme `TokyoNight Night` exists                                                                                                            | iTerm2-Color-Schemes repo, `ghostty/` folder |
| Ghostty does not run on the Pi 5: needs OpenGL 4.3, the Pi has 3.1                                                                                  | `eglinfo`; ghostty discussion #13907         |
| ghostty-config: `config` (17 lines), `install.sh`, `update_docs.py`, a 4,732-line generated `CONFIG_REFERENCE.md`; 11 commits; public, not archived | `ls`, `git log`, `gh repo view`              |
| Its `install.sh` links Application Support's `config` into that repo                                                                                | `install.sh`                                 |

## Decisions (2026-10-04)

| Question                     | Chosen                                                        | Rejected                                      |
| ---------------------------- | ------------------------------------------------------------- | --------------------------------------------- |
| Where Ghostty's config lives | `ghostty/` in this repo, linked to `~/.config/ghostty`        | keeping the separate ghostty-config repo      |
| `update_docs.py`, reference  | dropped; `ghostty +show-config --default --docs` prints it    | moving the script, with or without its output |
| Old history                  | copy the config; archive the GitHub repo, which keeps history | merging the 11 commits with git subtree       |

## Changes

| File             | Change                                                                                                          |
| ---------------- | --------------------------------------------------------------------------------------------------------------- |
| `deploy.py`      | a `CASKS` list next to `TOOLS`: `ghostty`, `font-0xproto-nerd-font`; one `brew.casks` call on macOS only        |
| `deploy.py`      | link `~/.config/ghostty` to `ghostty/` in the repo on macOS, using the link code from cage-foot                 |
| `deploy.py`      | remove `~/Library/Application Support/com.mitchellh.ghostty/config` only if it is a symlink into ghostty-config |
| `ghostty/config` | copied unchanged from ghostty-config, then its first-line path comment updated in a second commit               |
| `README.md`      | What it does, Layout: Ghostty on macOS                                                                          |

Commits: cask support; copy config (body names the archived repo); update
the path comment; link + old-symlink removal; README.

## Theme ownership

| Layer                           | Owner   | Kept as                                      |
| ------------------------------- | ------- | -------------------------------------------- |
| terminal palette, Pi and Debian | foot    | `include=` of the `foot-themes` file         |
| terminal palette, Mac           | Ghostty | `theme = TokyoNight Night`                   |
| fish highlighting               | fish    | the 20 hex lines in `config.fish`, unchanged |

Ruled out: letting fish set the terminal palette with escape codes at
startup. It only applies once fish runs, tmux interferes, and the Linux
console needs different codes. Also ruled out: fisher for the fish theme,
a second package manager to replace 20 working lines.

## Risks

| Risk                                                                     | Mitigation                                                          |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| Old Application Support link overrides or dangles after the repo is gone | deploy removes it, but only when it points into ghostty-config      |
| A real file sits there instead (not a link)                              | left alone and reported; the user decides                           |
| The font cask may not include the Mono variant the config names          | check the installed files before the config commit                  |
| A cask install may need the macOS password or a Gatekeeper prompt        | run once interactively; later runs see it installed                 |
| Theme names follow iTerm2-Color-Schemes and could be renamed             | Ghostty prints an error for an unknown theme; fix the one line      |
| Archiving or deleting the old repo is public or hard to undo             | only after the Mac check passes, and only on the user's explicit go |

## Checklist

- [x] Decide reference script and history handling.
- [ ] cage-foot.md done, so the generalised link code exists.
- [ ] `CASKS` list and `brew.casks` call, font included.
- [ ] Copy `config`, then update its path comment.
- [ ] `~/.config/ghostty` link and old-symlink removal.
- [ ] README.
- [ ] Mac run and visual check by the user.
- [ ] On the user's go: archive r0nny8000/ghostty-config, remove local clones.
- [ ] All acceptance criteria in the header pass.
