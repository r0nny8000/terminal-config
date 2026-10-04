---
status: planned
priority: medium
acceptance:
  - In foot on tty1, `echo $COLORTERM` prints truecolor and `colors` shows a smooth gradient.
  - In tmux inside foot, `colors` shows a smooth gradient and fish's own colours are 24-bit.
  - The German layout works in foot without typing any XKB variable.
  - `./bootstrap.sh --dry` is clean and a second full run reports zero changes.
  - `fish_indent --check fish/**/*.fish` passes.
---

# Full-colour terminal on the Pi's monitor: cage + foot

## Goal

On the Pi's own screen, typing `term` after the console login opens a
full-screen terminal with 24-bit colour and the Tokyo Night theme, German
keyboard layout included, with tmux keeping those colours. Installed and
configured by `deploy.py`, like everything else here.

## What was found (2026-10-04, on this Pi)

| Fact                                                 | Checked with                               |
| ---------------------------------------------------- | ------------------------------------------ |
| Kernel console is limited to 16 colours              | `tmux list-clients` shows tty1, TERM=linux |
| cage 0.3.1 and foot 1.21.0 work, installed by hand   | `dpkg -l`, the user's test at the monitor  |
| foot sets `COLORTERM=truecolor`                      | `man foot`, ENVIRONMENT section            |
| fish uses 24-bit only when `COLORTERM` says so       | `set_color 7dcfff` with and without it     |
| tmux 3.5a has no config; no RGB for any terminal     | `tmux show -s terminal-features`           |
| tmux does not pass `COLORTERM` into panes by default | `tmux show -g update-environment`          |
| `foot-themes` 1.21.0 ships `tokyonight-night`        | `apt-get download foot-themes`, `dpkg -c`  |
| foot.ini can `include=` an absolute path             | `man 5 foot.ini`                           |
| cage ignores `/etc/default/keyboard`; it reads XKB_* | wlroots behaviour; untested without them   |
| Keyboard here: layout de, options compose:lwin       | `/etc/default/keyboard`                    |

## Changes

| File                       | Change                                                                                                                |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `deploy.py`                | TOOLS rows `cage`, `foot`, `foot-themes`, all `(None, …)`: Wayland, Linux only                                        |
| `deploy.py`                | link `~/.config/foot` to `foot/` in the repo (copied first for non-local hosts); skip on macOS                        |
| `foot/foot.ini`            | `include=/usr/share/foot/themes/tokyonight-night`; font left at foot's default                                        |
| `fish/functions/term.fish` | reads XKBLAYOUT, XKBVARIANT, XKBOPTIONS from `/etc/default/keyboard`, exports them as XKB_DEFAULT_*, runs `cage foot` |
| `tmux/tmux.conf` + link    | `terminal-features` RGB for `foot*`; `COLORTERM` passed into panes                                                    |
| `README.md`                | What it does, Layout: the foot and tmux entries                                                                       |

Commits, one concern each: tools; foot config + link; launcher; tmux config +
link; README. The tmux commit carries a `Decision:` trailer if the repo starts
owning more than fish config.

## Decisions (2026-10-04)

| Question      | Chosen                                                  | Rejected                            |
| ------------- | ------------------------------------------------------- | ----------------------------------- |
| Start         | `term` typed after login; auto-start can be added later | automatic start on login on tty1    |
| Theme         | `include=` from the `foot-themes` package               | colours copied into `foot/foot.ini` |
| Launcher name | `term`                                                  | `kiosk`, `foot-full`                |

## Risks

| Risk                                                                   | Mitigation                                                                    |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| cage and foot pull Wayland libraries onto headless Debian machines too | accept: small, and TOOLS has no per-machine gating besides the Pi model check |
| tmux started outside foot keeps 256 colours                            | expected; RGB is declared for `foot*` only                                    |
| Whether tmux 3.5a sets `COLORTERM` itself is unverified                | test first; add it to `update-environment` only if needed                     |
| Second user andre gets the same links on a fresh bootstrap             | push before he tests (Claude cannot read his home)                            |

## Checklist

- [x] Decide the three open points.
- [ ] Reproduce first: tmux in foot shows a striped gradient in `colors`.
- [ ] TOOLS rows; deploy installs foot-themes.
- [ ] `foot/foot.ini` and the `~/.config/foot` link.
- [ ] Launcher function `term` with the keyboard values.
- [ ] tmux config and link.
- [ ] README.
- [ ] All acceptance criteria in the header pass; the monitor checks by the user.
