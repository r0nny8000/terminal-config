# 2. Release installs on Debian: pinned, updated by bumping the constant

Status: accepted
Date: 2026-10-18

## Context

The repo installs tools from the distribution's package manager, even when the
distribution lags upstream (commit 0b59022). Three things on Debian have no
package and come from GitHub releases instead, each pinned by a constant in
`deploy.py`:

| Item         | Constant     | Why no package                      |
| ------------ | ------------ | ----------------------------------- |
| herdr        | `HERDR`      | Debian has no herdr package         |
| bandwhich    | `BANDWHICH`  | packaged in sid only, not in stable |
| 0xProto font | `NERD_FONTS` | Debian packages no Nerd Font        |

Each install was guarded by "is it there?": `Which` for the binaries, a font
file for the font. Once installed, every later run skipped it, so bumping a
constant changed nothing on an existing machine; only a fresh bootstrap got
the new version. On 2026-10-15 the Pi had herdr 0.9.4 while 0.9.5 was out,
and a dry run with `HERDR = "0.9.5"` listed no install.

macOS is not affected: all three come from Homebrew there, and `brew upgrade`
updates them.

## Decision

Each release install compares the installed version with its constant and
installs when they differ. Updating is: bump the constant, run the deploy,
commit.

- herdr and bandwhich: `<binary> --version`, compared with `herdr <HERDR>` and
  `bandwhich <BANDWHICH>`, read from `/usr/local/bin` where the deploy puts
  them.
- The font has no version command, so the install writes `NERD_FONTS` into a
  `VERSION` file in its directory.
- A new binary is written to `<path>.new` and renamed over the old one.
  Writing into a running binary fails with "Text file busy", and the herdr
  server runs from `/usr/local/bin/herdr`. The rename leaves the running
  server on the old copy until it restarts.
- A new font release is unpacked into `0xProto.new` and swapped in whole, so a
  failed download leaves the old font working and files a release dropped do
  not linger.

## Alternatives

| Alternative                        | Why not                                                                                           |
| ---------------------------------- | ------------------------------------------------------------------------------------------------- |
| `herdr update`, herdr's own update | Moves the installed version away from `HERDR` unseen, needs sudo for `/usr/local/bin`, herdr only |
| Always fetch the latest release    | Runs stop being reproducible, and a second run would no longer report zero changes                |
| Leave the guards as they were      | A bumped constant reaches fresh machines only, so the Pi and a new bootstrap drift apart          |

## Rationale

- The repo states which version every Debian machine has, the same way
  `TOOLS` states which package it has.
- Bumping by hand is the cost of these three being outside the package
  manager. It stays limited to what Debian cannot supply; anything Debian
  packages still comes from apt (commit 0b59022).

## Revisit when

- Debian packages herdr, bandwhich (in stable) or a Nerd Font: move that item
  to `TOOLS` and drop its constant.
