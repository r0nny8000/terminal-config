# 1. Terminal emulators: foot on the Pi, Ghostty on the Mac

Status: accepted
Date: 2026-10-04

## Context

The repo sets up two terminal emulators: foot inside cage on the Raspberry
Pi 5's monitor (`term`), and Ghostty on the Mac. One emulator on both
machines would mean one config instead of two, so WezTerm was checked as a
replacement for both.

What was checked on 2026-10-04, on the Pi 5 (Debian 13 trixie, Mesa 26.2):

| Fact                                                                 | Checked with                                               |
| -------------------------------------------------------------------- | ---------------------------------------------------------- |
| The Pi 5 offers OpenGL ES 3.1 (V3D 7.1)                              | cage's log when starting                                   |
| Ghostty needs OpenGL 4.3, so it cannot run on the Pi                 | earlier research, commit 31b7cbe                           |
| WezTerm is not packaged for trixie                                   | `apt-cache policy wezterm`                                 |
| WezTerm's nightly arm64 .deb runs in cage with all three renderers   | headless cage, `front_end` OpenGL, WebGpu and Software     |
| WezTerm's OpenGL and WebGpu renderers use the Pi's GPU               | process maps: Mesa and `libvulkan_broadcom`, `/dev/dri`    |
| The shell inside WezTerm sees `COLORTERM=truecolor`                  | the same test                                              |
| WezTerm's last stable release is 20240203 (Feb 2024)                 | GitHub releases                                            |
| WezTerm's Homebrew cask is that Feb 2024 build                       | formulae.brew.sh cask API                                  |
| WezTerm's newest arm64 nightly .deb was built 2026-01-17             | GitHub nightly release assets                              |
| WezTerm was on hold until its author returned in June 2026           | issues #7825 and #6341 on wezterm/wezterm                  |
| Ghostty released v1.2.0 to v1.3.1 between 2025-09 and 2026-03        | git tags on ghostty-org/ghostty                            |

Activity from June to September 2026:

| Project | Commits | Open issues + PRs | Releases in the last 13 months |
| ------- | ------- | ----------------- | ------------------------------ |
| Ghostty | 1,728   | 256               | 6                              |
| WezTerm | 148     | 1,903             | 0                              |

Not checked: WezTerm on the real monitor, the German keyboard layout in
WezTerm, and WezTerm on the Mac itself.

## Decision

Keep foot inside cage on the Pi and Ghostty on the Mac. Do not adopt
WezTerm.

## Alternatives

| Alternative                    | Why not                                                                                                           |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| WezTerm on both machines       | Runs on both, but the Pi needs a hand-managed .deb or a third-party apt repo, and both builds are stale           |
| Ghostty on both machines       | Needs OpenGL 4.3; the Pi 5 offers OpenGL ES 3.1                                                                   |
| kitty on the Pi                | Would run, but costs 22 MB plus Python and depends on the GPU drivers (commit 31b7cbe)                            |

## Rationale

- The repo installs tools from the distribution's package manager: one row
  in `TOOLS` in `deploy.py`. foot and cage come from apt, Ghostty from a
  Homebrew cask. WezTerm has no trixie package, so the Pi would need an
  install outside that rule.
- WezTerm's only gain is a shared config. It comes with a stable release
  from Feb 2024, a Pi nightly from January 2026, and a project that has
  only just restarted after about a year on hold.
- Ghostty is actively developed and its cask tracks the current release,
  so the Mac side is in good shape.
- Two small configs, `foot/` and `ghostty/`, cost little to keep in sync.

## Revisit when

- WezTerm publishes a new stable release and the Homebrew cask picks it up,
  or Debian packages WezTerm, or
- Ghostty runs on OpenGL ES 3.1 or Vulkan, which would allow Ghostty on
  both machines.
