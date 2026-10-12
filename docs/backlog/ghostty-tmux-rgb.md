---
status: open
priority: medium
acceptance:
  - Inside tmux in Ghostty on the Mac, `tmux display -p '#{client_termfeatures}'` lists RGB
  - `python scripts/tokyonight-colors.py` inside tmux shows the same colours as outside tmux
---

# Check that tmux passes Ghostty's 24-bit colours through

On foot, tmux mapped every 24-bit colour to the nearest of 256, because
Debian's foot terminfo has no RGB or Tc flag; `tmux/tmux.conf` now declares
`foot*:RGB` (commit b94a13d).

Ghostty should not need that line: its terminfo (`xterm-ghostty`, from
`src/terminfo/ghostty.zig` in the Ghostty repo) declares `Tc`, which tmux reads
as RGB. That was checked in the source only, not on the Mac.

If RGB is missing from the client features, add
`set -as terminal-features ',xterm-ghostty:RGB'` next to the foot line.
