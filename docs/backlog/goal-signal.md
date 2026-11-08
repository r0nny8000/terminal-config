---
status: goal-ready
priority: medium
acceptance: fish/functions/signal.fish shows every access point of the connected SSID on both bands as a bar diagram labelled BSSID, IP, band and a details table; `uv run --with pytest pytest -q` passes, including the new tests/test_signal.py
---

# Goal: signal fish function

## Goal

A `signal` fish function shows every access point (BSSID) of the connected
SSID on both bands, strongest first, as a bar diagram labelled with BSSID, IP
and band, then a details table, so it is obvious which device and band the
Pi is on without any name mapping.

## Context

- Repo state: `main`, clean tree, last commit `docs: show both bands in goal
  signal`; 4 commits ahead of origin, not pushed.
- Source item: `docs/backlog/signal-fish.md`. Read it in full; its data
  sources, IP heuristic and risks apply, but its names (`signal_names`), its
  Device column, its connected-band-only filter and its example output are
  replaced by this file (see "Decisions made while defining this goal").
- Relevant files: `fish/functions/speedtest.fish` and `fish/functions/wifi.fish`
  for the help layout; `tests/test_speedtest.py` for the pattern (fish by
  absolute path via `shutil.which`, `--no-config`, env built from scratch with
  PATH holding only the fakes, a fake that logs its arguments).
- Deploy: `deploy.py` symlinks `~/.config/fish/functions` to the repo, so a
  new function needs no deploy change. nmcli, iw and ip ship with Raspberry
  Pi OS; no `TOOLS` row.
- Decisions to respect: CLAUDE.md (commit format, one concern per commit,
  done means verified). No ADR or `Decision:` commit applies.
- Decisions made while defining this goal (user, 2026-11-08):
  - No name mapping: `signal_names` is dropped entirely, so
    `config.local.fish` plays no part.
  - Both bands: list every BSSID of the connected SSID, 5 GHz and 2.4 GHz
    together, sorted by signal. Each device broadcasts the SSID with its own
    BSSID per band, so `office` has 6 BSSIDs here.
  - Diagram label: `<BSSID>, <IP>, <band>`, with `, connected` appended on
    the connected row. Band is `5 GHz` or `2.4 GHz`, derived from FREQ.
    The header line names no band: `Signal for network <SSID>:`.
  - IP: from `ip neigh`, with the backlog's heuristic (unique match on
    BSSID bytes 2-5), else `?`. The LAN MAC is only used for matching and is
    not shown.
  - Table columns: BSSID, IP, Band, Ch, Signal, dBm, Rx Mbit/s, Tx Mbit/s.
    The backlog's Device column is gone.
  - Interface: take the connected wifi device from
    `nmcli -t -f DEVICE,TYPE,STATE device`, not from /sys. The wifi.fish loop
    calls `ls` and reads the real /sys, which a fake-only PATH can't control
    and the Mac doesn't have. This overrides the backlog's "copy the loop".
  - README: add a new section listing the fish functions `wifi`, `cpu`,
    `speedtest`, `signal`, one line each.
  - Style check: `fish_indent --check (git ls-files "fish/*.fish")` instead
    of the backlog's `fish/**/*.fish`, which also matches the user's ignored
    `fish/config.local.fish` and fails on it today.
- Target output for the fixture, exactly (the 4-space Markdown indent below
  is not part of it): header line, blank line, diagram rows indented 2
  spaces, blank line, table at column 0. Measured: the diagram's label column
  is longest label + 4 (here 46 + 4 = 50, the same rule as the backlog
  example); every table row is 90 characters, columns as wide as their
  widest cell except dBm, which is 6 as in the backlog; text columns are
  left-aligned, Ch, Signal, dBm, Rx and Tx right-aligned; bars are one block
  per 5 % rounded: 17, 14, 11, 9, 8, 7 for 84, 70, 55, 47, 42, 33 %.

      Signal for network office:

        0A:11:22:33:44:51, 10.9.8.37, 5 GHz, connected    84 %  █████████████████
        0A:11:22:33:44:50, 10.9.8.37, 2.4 GHz             70 %  ██████████████
        02:AB:CD:55:66:C1, ?, 5 GHz                       55 %  ███████████
        02:AB:CD:77:88:C0, 10.9.8.1, 5 GHz                47 %  █████████
        02:AB:CD:55:66:C2, ?, 2.4 GHz                     42 %  ████████
        02:AB:CD:77:88:C1, 10.9.8.1, 2.4 GHz              33 %  ███████

      | BSSID             | IP        | Band    | Ch | Signal |    dBm | Rx Mbit/s | Tx Mbit/s |
      | ----------------- | --------- | ------- | -- | ------ | ------ | --------- | --------- |
      | 0A:11:22:33:44:51 | 10.9.8.37 | 5 GHz   | 40 |   84 % |    -50 |    1200.9 |    1200.9 |
      | 0A:11:22:33:44:50 | 10.9.8.37 | 2.4 GHz |  6 |   70 % |    -58 |     (130) |     (130) |
      | 02:AB:CD:55:66:C1 | ?         | 5 GHz   | 40 |   55 % |    -67 |     (270) |     (270) |
      | 02:AB:CD:77:88:C0 | 10.9.8.1  | 5 GHz   | 40 |   47 % |    -72 |     (540) |     (540) |
      | 02:AB:CD:55:66:C2 | ?         | 2.4 GHz |  6 |   42 % |    -76 |     (130) |     (130) |
      | 02:AB:CD:77:88:C1 | 10.9.8.1  | 2.4 GHz |  6 |   33 % |    -81 |     (130) |     (130) |

- Fixture values: SSID `office`; connected to `0A:11:22:33:44:51` on
  5200 MHz. The three 5 GHz rows (5200 MHz, channel 40) are the real
  2026-11-08 scan from the backlog. The three 2.4 GHz rows (2437 MHz,
  channel 6, rate 130 Mbit/s) are made up for the fixture; their BSSIDs keep
  each device's bytes 2-5 so the IP heuristic maps them to the same IP.
  Values per row are in the target output (nmcli SIGNAL and RATE, iw scan
  `signal: <dBm>.00 dBm`). `iw link` rx and tx 1200.9 MBit/s. `ip neigh`:
  `10.9.8.37 lladdr 08:11:22:33:44:41` (real, from the backlog) and
  `10.9.8.1 lladdr 00:ab:cd:77:88:c1` (made up; only bytes 2-5 are known).
  No entry matches the Repeater R2's bytes `ab:cd:55:66`. Add `office-g` APs
  on both bands to the nmcli fixture so the exact-SSID filter is tested.
- Verified facts (2026-11-08, on the Pi):
  - Tools: `/usr/bin/nmcli` 1.52.1, `/usr/sbin/iw`, `/usr/sbin/ip`, fish
    4.0.2. Wi-Fi interface `wlan0`. All commands below run without sudo.
  - `nmcli -t -f IN-USE,BSSID,SSID,CHAN,FREQ,SIGNAL,RATE dev wifi list --rescan yes`
    exits 0 in about 7.5 s. Sample line:
    `*:0A\:11\:22\:XX\:XX\:XX:office:40:5200 MHz:87:270 Mbit/s`. BSSIDs
    uppercase with `\:` escapes; FREQ ends in ` MHz`, RATE in ` Mbit/s`.
  - SSID `office` has 3 APs on 5 GHz (5200 MHz) and 3 on 2.4 GHz
    (2437 MHz), and a separate SSID `office-g` exists: match the SSID
    exactly.
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
- [ ] With fake nmcli, iw and ip fed the fixture, `signal` prints the target output in this file's Context exactly (header, diagram strongest first labelled `<BSSID>, <IP>, <band>` with `, connected` on the connected row and one block per 5 % rounded, then the table sorted by signal) — proven by `uv run --with pytest pytest -q tests/test_signal.py` passing
- [ ] Both bands of the connected SSID appear, and only that SSID: the `office-g` APs are left out — proven by the same pytest run
- [ ] IP comes from a unique `ip neigh` match on BSSID bytes 2-5; with no unique match (none, or two entries sharing bytes 2-5) it shows `?` — proven by the same pytest run, including a case with two matching entries
- [ ] Without nmcli on PATH, `signal` prints `signal: Linux only (needs nmcli)` to stderr and returns 1 — proven by the same pytest run
- [ ] `signal -h` follows the wifi/speedtest layout (`Usage:`, description, `Runs:`, `Options:` ending with `  -h, --help  Show this help message and exit`) — proven by pytest and by `fish -c 'signal -h'` output shown
- [ ] Live run on the Pi works — proven by `fish -c signal` output shown, listing the real `office` BSSIDs on both bands with BSSID, IP, band labels and plausible values
- [ ] README has a section listing `wifi`, `cpu`, `speedtest` and `signal` — proven by `grep -n -E 'wifi|cpu|speedtest|signal' README.md` output shown
- [ ] Style — proven by `fish -c 'fish_indent --check (git ls-files "fish/*.fish") fish/functions/signal.fish; echo $status'` printing 0
- [ ] Whole suite passes — proven by `uv run --with pytest pytest -q` (18 or more passed, 0 failed)
- [ ] Deploy is clean — proven by `./bootstrap.sh --dry` showing no changes and `./bootstrap.sh -y` reporting zero changes
- [ ] Committed on `main`, not pushed, with `docs/backlog/signal-fish.md` deleted in the completing commit — proven by `git status --short` (empty) and `git log --oneline -4`

## Verification

Run, in order, and show each output in the transcript:
`uv run --with pytest pytest -q`,
`fish -c 'fish_indent --check (git ls-files "fish/*.fish") fish/functions/signal.fish; echo $status'`,
`fish -c 'signal -h'`, `fish -c signal`,
`grep -n -E 'wifi|cpu|speedtest|signal' README.md`, `./bootstrap.sh --dry`,
`./bootstrap.sh -y`, `git status --short`, `git log --oneline -4`.

## Guardrails

- No test is deleted, skipped, or weakened to make a check pass.
- No edits outside `fish/functions/signal.fish`, `tests/test_signal.py` and
  `README.md`, except deleting `docs/backlog/signal-fish.md` in the completing
  commit and this goal file (see "When done").
- `~/.config/fish/config.local.fish` (and its repo symlink) is not modified,
  and `signal` does not read any variable from it.
- No change to `deploy.py` or `fish/functions/wifi.fish`.
- Commit on `main` following CLAUDE.md (`type: what changed`, body says why,
  one concern per commit). No push, no amend, no force operations.
- Tests never call the real nmcli, iw or ip; only the live run does. The live
  run makes no connection changes (no `nmcli connect`, no `iw ... set`).

## Out of scope

- Any change to `wifi.fish`, including extracting shared interface code.
- Mapping BSSIDs or MACs to device names (`signal_names`).
- Showing the LAN MAC.

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
fish/functions/signal.fish exists and `uv run --with pytest pytest -q` passes (0 failed), including a new tests/test_signal.py that was run and failed once before the function was written. The tests put only fake nmcli, iw and ip on PATH, fed with the fixture from the goal file, and prove: output equals the target output in the goal file's Context exactly (header, diagram strongest first labelled `<BSSID>, <IP>, <band>` with `, connected` on the connected row and one block per 5 % rounded, then the table with columns BSSID, IP, Band, Ch, Signal, dBm, Rx, Tx sorted by signal); both bands of the connected SSID appear and office-g APs are left out; IP comes from a unique ip neigh match on BSSID bytes 2-5, else `?`; without nmcli, `signal: Linux only (needs nmcli)` goes to stderr with return 1; `-h` follows the wifi/speedtest help layout. Also: `fish -c 'signal -h'` and one live `fish -c signal` on the Pi print sensible output; README has a section listing wifi, cpu, speedtest and signal, shown by grep; `fish -c 'fish_indent --check (git ls-files "fish/*.fish") fish/functions/signal.fish; echo $status'` prints 0; `./bootstrap.sh --dry` and `./bootstrap.sh -y` report no changes; work is committed on main per CLAUDE.md with docs/backlog/signal-fish.md deleted in the completing commit, `git status --short` empty, nothing pushed. Guardrails: no test deleted, skipped or weakened; edits only to signal.fish, tests/test_signal.py, README.md, deleting the backlog item, and this goal file; config.local.fish, deploy.py and wifi.fish untouched; no signal_names or other name mapping; tests never call the real tools; no connection changes; no push. Out of scope: any change to wifi.fish, name mapping, showing the LAN MAC. Show the output of each check in the transcript. Or stop after 25 turns and report what remains.
```
