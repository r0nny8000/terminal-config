---
status: goal-ready
priority: medium
acceptance: fish/functions/signal.fish shows the access points of the connected SSID and band as a bar diagram and a details table; `uv run --with pytest pytest -q` passes, including the new tests/test_signal.py
---

# Goal: signal fish function

## Goal

A `signal` fish function shows every access point of the connected SSID on
the connected band, strongest first, as a bar diagram and then a details
table, so it is obvious which repeater the Pi is on.

## Context

- Repo state: `main`, clean tree, in sync with origin, last commit
  `959f0d0 docs: backlog a signal fish function`.
- Source item: `docs/backlog/signal-fish.md`. Read it in full; its target
  output, data sources, IP heuristic and risks apply, except where this file
  overrides them (see "Decisions made while defining this goal").
- Relevant files: `fish/functions/speedtest.fish` and `fish/functions/wifi.fish`
  for the help layout; `tests/test_speedtest.py` for the pattern (fish by
  absolute path via `shutil.which`, `--no-config`, env built from scratch with
  PATH holding only the fakes, a fake that logs its arguments).
- Deploy: `deploy.py` symlinks `~/.config/fish/functions` to the repo, so a
  new function needs no deploy change. nmcli, iw and ip ship with Raspberry
  Pi OS; no `TOOLS` row.
- Decisions to respect: CLAUDE.md (commit format, one concern per commit,
  machine-specific values only in the untracked `config.local.fish`, done
  means verified). No ADR or `Decision:` commit applies.
- Decisions made while defining this goal (user, 2026-11-08):
  - Interface: take the connected wifi device from
    `nmcli -t -f DEVICE,TYPE,STATE device`, not from /sys. The wifi.fish loop
    calls `ls` and reads the real /sys, which a fake-only PATH can't control
    and the Mac doesn't have. This overrides the backlog's "copy the loop".
  - Test fixture: the 2026-11-08 scan with
    `signal_names` = `'55:66=Repeater R2' '33:44=Repeater R1'` (no router
    entry). The backlog's sample list includes `77:88=router`, which
    contradicts its own example output; the example output wins.
  - `config.local.fish` is not touched; the user adds `signal_names` later.
  - README: add a new section listing the fish functions `wifi`, `cpu`,
    `speedtest`, `signal` (one line each) and noting that `signal_names`
    lives in `config.local.fish`.
  - No name fallback: an access point without a `signal_names` match shows
    its BSSID as the diagram label, not `<IP> <BSSID>` or `? <BSSID>`. This
    overrides the backlog's acceptance line on names and its example's third
    diagram row. The table is unchanged: `-` in Device, and the IP column
    still comes from the bytes 2-5 heuristic (`?` when not unique).
  - Style check: `fish_indent --check (git ls-files "fish/*.fish")` instead
    of the backlog's `fish/**/*.fish`, which also matches the user's ignored
    `fish/config.local.fish` and fails on it today.
- Target output for the fixture, exactly (the 4-space Markdown indent below
  is not part of it). It is the backlog example with the no-fallback diagram:
  header line, blank line, diagram rows indented 2 spaces, blank line, table
  at column 0. Measured: every table row is 98 characters; the diagram's
  label column is longest label + 4 (here 22 + 4 = 26, as the backlog's 30
  was 26 + 4); bars are 17, 11, 9 blocks for 84, 55, 47 %.

      Signal on 5 GHz for network office:

        Repeater R1, connected    84 %  █████████████████
        Repeater R2               55 %  ███████████
        02:AB:CD:77:88:C0         47 %  █████████

      | Device      | BSSID             | IP        | Ch | Signal |    dBm | Rx Mbit/s | Tx Mbit/s |
      | ----------- | ----------------- | --------- | -- | ------ | ------ | --------- | --------- |
      | Repeater R1 | 0A:11:22:33:44:51 | 10.9.8.37 | 40 |   84 % |    -50 |    1200.9 |    1200.9 |
      | Repeater R2 | 02:AB:CD:55:66:C1 | ?         | 40 |   55 % |    -67 |     (270) |     (270) |
      | -           | 02:AB:CD:77:88:C0 | 10.9.8.1  | 40 |   47 % |    -72 |     (540) |     (540) |
- Fixture values: SSID `office`, 5200 MHz, channel 40. APs (nmcli
  signal % / rate, iw scan dBm): R1 `0A:11:22:33:44:51` 84 % / -50.00,
  connected; R2 `02:AB:CD:55:66:C1` 55 % / 270 Mbit/s / -67.00; router
  `02:AB:CD:77:88:C0` 47 % / 540 Mbit/s / -72.00. `iw link` rx and tx
  1200.9 MBit/s. `ip neigh`: 10.9.8.37 lladdr `08:11:22:33:44:41`, 10.9.8.1
  lladdr with bytes 2-5 `ab:cd:77:88`; no entry for R2.
- Verified facts (2026-11-08, on the Pi):
  - Tools: `/usr/bin/nmcli` 1.52.1, `/usr/sbin/iw`, `/usr/sbin/ip`, fish
    4.0.2. Wi-Fi interface `wlan0`. All commands below run without sudo.
  - `nmcli -t -f IN-USE,BSSID,SSID,CHAN,FREQ,SIGNAL,RATE dev wifi list --rescan yes`
    exits 0 in about 7.5 s. Sample line:
    `*:0A\:11\:22\:XX\:XX\:XX:office:40:5200 MHz:87:270 Mbit/s`. BSSIDs
    uppercase with `\:` escapes; FREQ ends in ` MHz`, RATE in ` Mbit/s`.
  - SSID `office` has 3 APs on 5 GHz and 3 on 2.4 GHz, and a separate SSID
    `office-g` exists: filter by band and match the SSID exactly.
  - `iw dev wlan0 link`: `Connected to <bssid> (on wlan0)`, `freq: 5200.0`,
    `signal: -46 dBm`, `rx bitrate: 1200.9 MBit/s ...`, `tx bitrate: ...`.
  - `iw dev wlan0 scan dump`: blocks start `BSS <bssid>(on wlan0)`, lowercase
    BSSIDs, `signal: -48.00 dBm`. Match BSSIDs case-insensitively.
  - `ip neigh show dev wlan0`: `10.9.8.1 lladdr <mac> REACHABLE`, lowercase.
  - nmcli prints German messages here, but terse field values are unchanged.
    fish's `printf` uses the German locale live (`1200,9`); tests run in the C
    locale (`1200.9`), as with speedtest.
  - README has no list of functions today; "## Layout" and "## Verify" exist.
  - `uv run --with pytest pytest -q`: 17 passed.
    `fish_indent --check (git ls-files "fish/*.fish")`: exit 0.
- Files left by validation runs: only ignored caches (`.pytest_cache/`,
  `__pycache__/`).

## Acceptance checklist

- [ ] Tests come first: `tests/test_signal.py` exists and fails before the function exists — proven by `uv run --with pytest pytest -q tests/test_signal.py` run once before writing signal.fish, output shown
- [ ] With fake nmcli, iw and ip fed the fixture, `signal` prints the target output in this file's Context exactly (header, diagram strongest first with `connected` marker and one block per 5 % rounded, then the table sorted by signal) — proven by `uv run --with pytest pytest -q tests/test_signal.py` passing
- [ ] Only the connected SSID on the connected band appears: the fixture's 2.4 GHz `office` APs and the `office-g` APs are left out — proven by the same pytest run
- [ ] Names come from `signal_names` (case-insensitive BSSID substring); without a match the diagram label is the BSSID alone (no IP, no `?`) and the table's Device shows `-`; the IP column shows the unique bytes 2-5 match from `ip neigh`, else `?` — proven by the same pytest run, including a case where R2 is unnamed and absent from `ip neigh`
- [ ] Without nmcli on PATH, `signal` prints `signal: Linux only (needs nmcli)` to stderr and returns 1 — proven by the same pytest run
- [ ] `signal -h` follows the wifi/speedtest layout (`Usage:`, description, `Runs:`, `Options:` ending with `  -h, --help  Show this help message and exit`) — proven by pytest and by `fish -c 'signal -h'` output shown
- [ ] Live run on the Pi works — proven by `fish -c signal` output shown, listing the real `office` APs on the connected band with plausible values (labels are BSSIDs, since `signal_names` is not set yet)
- [ ] README has a section listing `wifi`, `cpu`, `speedtest` and `signal`, and mentions `signal_names` in `config.local.fish` — proven by `grep -n -E 'signal_names|speedtest|signal' README.md` output shown
- [ ] Style — proven by `fish -c 'fish_indent --check (git ls-files "fish/*.fish") fish/functions/signal.fish; echo $status'` printing 0
- [ ] Whole suite passes — proven by `uv run --with pytest pytest -q` (18 or more passed, 0 failed)
- [ ] Deploy is clean — proven by `./bootstrap.sh --dry` showing no changes and `./bootstrap.sh -y` reporting zero changes
- [ ] Committed on `main`, not pushed, with `docs/backlog/signal-fish.md` deleted in the completing commit — proven by `git status --short` (empty) and `git log --oneline -4`

## Verification

Run, in order, and show each output in the transcript:
`uv run --with pytest pytest -q`,
`fish -c 'fish_indent --check (git ls-files "fish/*.fish") fish/functions/signal.fish; echo $status'`,
`fish -c 'signal -h'`, `fish -c signal`,
`grep -n -E 'signal_names|speedtest|signal' README.md`, `./bootstrap.sh --dry`,
`./bootstrap.sh -y`, `git status --short`, `git log --oneline -4`.

## Guardrails

- No test is deleted, skipped, or weakened to make a check pass.
- No edits outside `fish/functions/signal.fish`, `tests/test_signal.py` and
  `README.md`, except deleting `docs/backlog/signal-fish.md` in the completing
  commit and this goal file (see "When done").
- `~/.config/fish/config.local.fish` (and its repo symlink) is not modified.
- No change to `deploy.py` or `fish/functions/wifi.fish`.
- Commit on `main` following CLAUDE.md (`type: what changed`, body says why,
  one concern per commit). No push, no amend, no force operations.
- Tests never call the real nmcli, iw or ip; only the live run does. The live
  run makes no connection changes (no `nmcli connect`, no `iw ... set`).

## Out of scope

- Any change to `wifi.fish`, including extracting shared interface code.

## Approach hints

- Prefix nmcli with `LC_ALL=C` (fish 3.1+ syntax) so the units stay stable.
- Split nmcli terse lines on unescaped `:` only, e.g. replace `\:` first.
- Not connected to Wi-Fi: a short `signal: ...` stderr message and return 1 is
  enough.

## When done

Ask the user whether to delete this file. Deleting is fine: it stays in git
history if it was committed.

## Open questions

None

## Condition

```text
fish/functions/signal.fish exists and `uv run --with pytest pytest -q` passes (0 failed), including a new tests/test_signal.py that was run and failed once before the function was written. The tests put only fake nmcli, iw and ip on PATH, fed with the 2026-11-08 fixture from the goal file, and prove: output equals the target output in the goal file's Context exactly (header, diagram strongest first with `connected` marker and one block per 5 % rounded, then the table sorted by signal); only the connected SSID on the connected band appears (2.4 GHz and office-g APs left out); names come from signal_names, an unnamed AP shows only its BSSID in the diagram (no IP fallback) and `-` in the table, while the table's IP column keeps the bytes 2-5 match or `?`; without nmcli, `signal: Linux only (needs nmcli)` goes to stderr with return 1; `-h` follows the wifi/speedtest help layout. Also: `fish -c 'signal -h'` and one live `fish -c signal` on the Pi print sensible output; README lists wifi, cpu, speedtest and signal and mentions signal_names in config.local.fish, shown by grep; `fish -c 'fish_indent --check (git ls-files "fish/*.fish") fish/functions/signal.fish; echo $status'` prints 0; `./bootstrap.sh --dry` and `./bootstrap.sh -y` report no changes; work is committed on main per CLAUDE.md with docs/backlog/signal-fish.md deleted in the completing commit, `git status --short` empty, nothing pushed. Guardrails: no test deleted, skipped or weakened; edits only to signal.fish, tests/test_signal.py, README.md, deleting the backlog item, and this goal file; config.local.fish, deploy.py and wifi.fish untouched; tests never call the real tools; no connection changes; no push. Out of scope: any change to wifi.fish. Show the output of each check in the transcript. Or stop after 25 turns and report what remains.
```
