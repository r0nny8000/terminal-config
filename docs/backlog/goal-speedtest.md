---
status: goal-ready
priority: low
acceptance: fish/functions/speedtest.fish measures download speed from Hetzner nbg1 in MB/s and Mbit/s; `uv run --with pytest pytest -q` passes, including the new tests/test_speedtest.py
---

# Goal: speedtest fish function

## Goal

A `speedtest` fish function downloads a Hetzner test file to /dev/null with
curl and prints the speed in MB/s and Mbit/s, on the Pi and the Mac.

## Context

- Repo state: `main`, clean tree, last commit `ab98e8f docs: backlog a
  speedtest fish function`. Origin is in sync.
- Source item: `docs/backlog/speedtest-fish.md` (read it; its note that
  `10MB.bin` exists is wrong, see Verified facts).
- Relevant files: `fish/functions/wifi.fish` and `fish/functions/cpu.fish`
  for the help style; `tests/test_fish_tab_label.py` for the pattern of
  running fish with a fake binary first on PATH.
- Deploy: `deploy.py` symlinks `~/.config/fish/functions` to the repo's
  `fish/functions`, so a new file needs no deploy change. curl is already in
  `TOOLS` (`deploy.py:29`, apt only; macOS ships it). wget is not.
- Decisions to respect: CLAUDE.md (commit format, one concern per commit,
  runtime probing belongs in the fish function, done means verified). No ADR
  applies.
- Help style (wifi/cpu): `argparse h/help ... -- $argv; or return`, then on
  `_flag_h`: `Usage:` lines, blank line, one-line description, `Runs: ...`
  line, blank line, `Options:` block ending in
  `  -h, --help  Show this help message and exit`, `return 0`. Errors go to
  stderr as `<name>: ...` with `return 1`.
- Verified facts (2026-11-05, on the Pi):
  - `https://nbg1-speed.hetzner.com/` lists only `100MB.bin`, `1GB.bin`,
    `10GB.bin`. `10MB.bin` does not exist (connection is cut, curl exit 56).
  - The server cuts HEAD requests (`curl -I` fails); a GET works.
  - `curl -s -o /dev/null -w '%{speed_download}' .../100MB.bin` returned
    11978858 bytes/s (about 12.0 MB/s, 96 Mbit/s) in 8.8 s.
  - `uv run --with pytest pytest -q`: 10 passed.
  - `fish_indent --check fish/**/*.fish` fails only on the untracked,
    ignored `fish/config.local.fish`; check the new file on its own.
  - Passwordless sudo is available; a deploy run with nothing to install
    needs no sudo anyway.
- Files left by validation runs: only ignored caches (`.pytest_cache/`,
  `__pycache__/`).

## Acceptance checklist

- [ ] Tests come first: `tests/test_speedtest.py` exists and fails before
      the function exists — proven by running `uv run --with pytest pytest -q tests/test_speedtest.py` once before writing the function, output shown
- [ ] `speedtest` with no argument downloads `https://nbg1-speed.hetzner.com/100MB.bin`; `speedtest 1G` and `speedtest 10G` select `1GB.bin` and `10GB.bin` — proven by `uv run --with pytest pytest -q tests/test_speedtest.py` passing (a fake curl records its URL)
- [ ] An unknown size prints an error to stderr that names the valid sizes and returns 1 — proven by the same pytest run
- [ ] Output shows MB/s and Mbit/s, converted from curl's bytes/s with decimal units (1 MB = 1,000,000 bytes, 1 Mbit = 1,000,000 bits) — proven by the same pytest run, with a fake curl returning a fixed speed and exact expected numbers
- [ ] Portable by design: the function calls no external command except curl — proven by the same pytest run, where fish runs with a PATH that contains only the fake curl
- [ ] `speedtest -h` follows the wifi/cpu layout (`Usage:`, description, `Runs:`, `Options:` with `-h, --help`) and lists the sizes — proven by pytest, and by `fish -c 'speedtest -h'` output shown in the transcript
- [ ] Real download works on the Pi — proven by `fish -c speedtest` output shown in the transcript with plausible MB/s and Mbit/s
- [ ] Style — proven by `fish_indent --check fish/functions/speedtest.fish` exiting 0
- [ ] Whole suite still passes — proven by `uv run --with pytest pytest -q` (11 or more passed, 0 failed)
- [ ] Deploy is clean — proven by `./bootstrap.sh --dry` showing no changes and `./bootstrap.sh -y` reporting zero changes
- [ ] Committed on `main`, not pushed — proven by `git status --short` (empty) and `git log --oneline -3`

## Verification

Run, in order, and show each output in the transcript:
`uv run --with pytest pytest -q`, `fish_indent --check fish/functions/speedtest.fish; echo $status`,
`fish -c 'speedtest -h'`, `fish -c speedtest`, `./bootstrap.sh --dry`,
`./bootstrap.sh -y`, `git status --short`, `git log --oneline -3`.

## Guardrails

- No test is deleted, skipped, or weakened to make a check pass.
- No edits outside `fish/functions/speedtest.fish`, `tests/test_speedtest.py`
  and `README.md` (only if it needs a mention), except deleting
  `docs/backlog/speedtest-fish.md` when done and this goal file (see "When
  done").
- No change to `deploy.py`: no new tools, no wget.
- Commit on `main` following CLAUDE.md (`type: what changed`, body says why).
  Deleting `docs/backlog/speedtest-fish.md` goes in the commit that completes
  it. No push, no amend of existing commits, no force operations.
- Tests never hit the network; only the one live run does.

## Out of scope

- The Wi-Fi line (access point and signal next to the result).
- Other servers, a free URL argument, a 10 MB size.
- Upload speed, latency, or repeated runs.
- Running anything on the Mac; the user tests there after pushing.
- Fixing `fish/config.local.fish` indentation (untracked, the user's file).

## Approach hints

- `curl -s -o /dev/null -w '%{speed_download}' <url>` prints bytes/s;
  fish's `math` does the conversion, so no `bc` or `awk` is needed.
- Fail cleanly when curl fails (non-zero exit): message to stderr, return 1.
- In the test, call fish by absolute path and set PATH to a temp dir holding
  only the fake curl.

## When done

Ask the user whether to delete this file. Deleting is fine: it stays in git
history if it was committed.

## Open questions

None

## Condition

```text
fish/functions/speedtest.fish exists and `uv run --with pytest pytest -q` passes (0 failed), including a new tests/test_speedtest.py that was run and failed once before the function was written. The tests use a fake curl on a PATH containing nothing else and prove: no argument fetches https://nbg1-speed.hetzner.com/100MB.bin, `1G` and `10G` fetch 1GB.bin and 10GB.bin; an unknown size errors on stderr naming the valid sizes and returns 1; output shows MB/s and Mbit/s with exact decimal conversion of curl's bytes/s; `-h` follows the wifi/cpu help layout (Usage:, Runs:, Options: with -h, --help). Also: `fish -c 'speedtest -h'` and one live `fish -c speedtest` on the Pi print sensible output; `fish_indent --check fish/functions/speedtest.fish` exits 0; `./bootstrap.sh --dry` and `./bootstrap.sh -y` report no changes; work is committed on main per CLAUDE.md with docs/backlog/speedtest-fish.md deleted in the completing commit, `git status --short` empty, nothing pushed. Guardrails: no test deleted, skipped or weakened; edits only to speedtest.fish, tests/test_speedtest.py, README.md if needed, deleting the backlog item, and this goal file; no deploy.py change; no push. Out of scope: Wi-Fi info, other servers or sizes, upload/latency, anything on the Mac. Show the output of each check in the transcript. Or stop after 15 turns and report what remains.
```
