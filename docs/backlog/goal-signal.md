---
status: goal-ready
priority: medium
acceptance: fish/functions/signal.fish shows every visible Wi-Fi access point as a bar diagram labelled SSID, IP, short BSSID, band, and a details table; `uv run --with pytest pytest -q` passes, including the new tests/test_signal.py
---

# Goal: signal fish function

## Goal

A `signal` fish function shows every visible Wi-Fi access point (one row per
BSSID), strongest first, as a bar diagram labelled with SSID, IP, short
BSSID and band, then a details table with channel and band, so it is obvious
which device, band and channel the Pi is on and what else is around.

## Context

- Repo state: `main`, clean tree, last commit `docs: show all visible
  networks in goal signal`; 5 commits ahead of origin, not pushed.
- Source item: `docs/backlog/signal-fish.md`. Read it in full; its data
  sources, IP heuristic and risks apply, but its names (`signal_names`), its
  Device column, its connected-SSID-and-band filter and its example output
  are replaced by this file (see "Decisions made while defining this goal").
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
  - All visible networks: one row per BSSID nmcli lists, every SSID,
    neighbours included, sorted by signal. Header line:
    `Signal of all visible networks:`.
  - Hidden networks (empty SSID) are shown with SSID `(hidden)`.
  - Diagram label: `<SSID>, <IP>, <short BSSID>, <band>`, with
    `, connected` appended on the connected row. Short BSSID is the first 5
    bytes of the BSSID (`0A:11:22:33:44`); the user identifies devices by it.
    It differs per band on these devices (first byte `26`/`24`, `02`/`00`).
  - Band is `5 GHz` or `2.4 GHz`, derived from FREQ.
  - Table columns: SSID, IP, BSSID, Band, Ch, Signal, dBm, Rx Mbit/s,
    Tx Mbit/s. The table shows the full BSSID, because short BSSIDs can
    collide (different radios, same first 5 bytes).
  - IP: from `ip neigh`, with the backlog's heuristic (unique match on
    BSSID bytes 2-5), else `?`. The LAN MAC is only used for matching and is
    not shown.
  - dBm: from `iw ... scan dump`; `?` when the BSSID is missing there (seen
    live on 2026-11-08 for one nmcli entry).
  - No name mapping: `signal_names` is dropped entirely, so
    `config.local.fish` plays no part.
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
  is longest label + 4 (here 51 + 4 = 55, the same rule as the backlog
  example), signal right-aligned in 2 characters; every table row is 105
  characters, columns as wide as their widest cell except dBm, which is 6 as
  in the backlog; SSID, IP, BSSID and Band left-aligned, Ch, Signal, dBm, Rx
  and Tx right-aligned; bars are one block per 5 % rounded:
  19, 19, 16, 16, 13, 12, 10, 7.

      Signal of all visible networks:

        office, 10.9.8.37, 0A:11:22:33:44, 5 GHz, connected    95 %  ███████████████████
        office-g, 10.9.8.37, 0A:11:22:33:44, 5 GHz             94 %  ███████████████████
        office, 10.9.8.37, 08:11:22:33:44, 2.4 GHz             82 %  ████████████████
        office, ?, 00:AB:CD:55:66, 2.4 GHz                     81 %  ████████████████
        office, 10.9.8.1, 00:AB:CD:77:88, 2.4 GHz              67 %  █████████████
        Nachbar-WLAN, ?, 00:00:5E:00:53, 2.4 GHz               59 %  ████████████
        office, 10.9.8.1, 02:AB:CD:77:88, 5 GHz                50 %  ██████████
        (hidden), ?, 00:00:5E:00:53, 5 GHz                     35 %  ███████

      | SSID         | IP        | BSSID             | Band    | Ch | Signal |    dBm | Rx Mbit/s | Tx Mbit/s |
      | ------------ | --------- | ----------------- | ------- | -- | ------ | ------ | --------- | --------- |
      | office       | 10.9.8.37 | 0A:11:22:33:44:51 | 5 GHz   | 40 |   95 % |    -43 |    1200.9 |    1200.9 |
      | office-g     | 10.9.8.37 | 0A:11:22:33:44:52 | 5 GHz   | 40 |   94 % |    -44 |     (270) |     (270) |
      | office       | 10.9.8.37 | 08:11:22:33:44:51 | 2.4 GHz |  6 |   82 % |    -51 |     (270) |     (270) |
      | office       | ?         | 00:AB:CD:55:66:C1 | 2.4 GHz |  6 |   81 % |      ? |     (270) |     (270) |
      | office       | 10.9.8.1  | 00:AB:CD:77:88:C0 | 2.4 GHz |  6 |   67 % |    -60 |     (540) |     (540) |
      | Nachbar-WLAN | ?         | 00:00:5E:00:53:01 | 2.4 GHz |  1 |   59 % |    -65 |     (130) |     (130) |
      | office       | 10.9.8.1  | 02:AB:CD:77:88:C0 | 5 GHz   | 40 |   50 % |    -70 |     (540) |     (540) |
      | (hidden)     | ?         | 00:00:5E:00:53:02 | 5 GHz   | 36 |   35 % |    -79 |     (540) |     (540) |

- Fixture values, all in the target output above:
  - nmcli: one terse line per row (SIGNAL, RATE in ` Mbit/s`, CHAN, FREQ
    5200 MHz for channel 40, 5180 MHz for 36, 2437 MHz for 6, 2412 MHz for
    1). The hidden network has an empty SSID field. Connected row marked `*`.
  - The `office`/`office-g` BSSIDs, channels, rates and signals are the live
    scan of 2026-11-08, except `00:AB:CD:55:66:C1`, nudged from 82 to 81 %
    to avoid a sort tie.
  - The neighbour rows are made up, on the documentation MAC range
    `00:00:5E:00:53:xx` (RFC 7042). Their two BSSIDs share a short form on
    purpose. Never put real neighbour SSIDs or BSSIDs in the repo.
  - `iw link`: connected to `0a:11:22:33:44:51`, rx and tx 1200.9 MBit/s.
  - `iw scan dump`: `signal: <dBm>.00 dBm` per BSSID, lowercase, with no
    block for `00:ab:cd:55:66:c1`.
  - `ip neigh`: `10.9.8.37 lladdr 08:11:22:33:44:41` (from the backlog) and
    `10.9.8.1 lladdr 00:ab:cd:77:88:d0` (live, 2026-11-08), plus an IPv6
    `fe80::...` line for the router, which must not count as a match.
- Verified facts (2026-11-08, on the Pi):
  - Tools: `/usr/bin/nmcli` 1.52.1, `/usr/sbin/iw`, `/usr/sbin/ip`, fish
    4.0.2. Wi-Fi interface `wlan0`. All commands below run without sudo.
  - `nmcli -t -f IN-USE,BSSID,SSID,CHAN,FREQ,SIGNAL,RATE dev wifi list --rescan yes`
    exits 0 in about 7.5 s and listed 20 BSSIDs, 5 of them hidden. Sample
    line: `*:0A\:11\:22\:33\:44\:51:office:40:5200 MHz:95:270 Mbit/s`.
    BSSIDs uppercase with `\:` escapes.
  - `iw dev wlan0 link`: `Connected to <bssid> (on wlan0)`, `freq: 5200.0`,
    `signal: -43 dBm`, `rx bitrate: 1200.9 MBit/s ...`, `tx bitrate: ...`.
  - `iw dev wlan0 scan dump`: blocks start `BSS <bssid>(on wlan0)`, lowercase
    BSSIDs, `signal: -43.00 dBm`. Match BSSIDs case-insensitively. One nmcli
    BSSID had no block.
  - `ip neigh show dev wlan0`: `10.9.8.1 lladdr 00:ab:cd:77:88:d0 REACHABLE`
    and an IPv6 line with the same lladdr. The repeaters were not in it, so
    a live run shows `?` for their IPs.
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
- [ ] With fake nmcli, iw and ip fed the fixture, `signal` prints the target output in this file's Context exactly (header, diagram strongest first labelled `<SSID>, <IP>, <short BSSID>, <band>` with `, connected` on the connected row and one block per 5 % rounded, then the table with the full BSSID, sorted by signal) — proven by `uv run --with pytest pytest -q tests/test_signal.py` passing
- [ ] Every BSSID nmcli lists appears, including other SSIDs and hidden networks as `(hidden)` — proven by the same pytest run
- [ ] IP comes from a unique IPv4 `ip neigh` match on BSSID bytes 2-5; with no unique match (none, or two entries sharing bytes 2-5) it shows `?`; a BSSID missing from the iw scan dump shows dBm `?` — proven by the same pytest run, including a case with two matching entries
- [ ] Without nmcli on PATH, `signal` prints `signal: Linux only (needs nmcli)` to stderr and returns 1 — proven by the same pytest run
- [ ] `signal -h` follows the wifi/speedtest layout (`Usage:`, description, `Runs:`, `Options:` ending with `  -h, --help  Show this help message and exit`) — proven by pytest and by `fish -c 'signal -h'` output shown
- [ ] Live run on the Pi works — proven by `fish -c signal` output shown, listing the visible networks with SSID, IP, short BSSID and band labels and plausible values
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
- No real neighbour SSIDs or BSSIDs in any committed file; the fixture uses
  the made-up ones above.
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
- Filtering or grouping networks (by SSID, band or owner).

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
fish/functions/signal.fish exists and `uv run --with pytest pytest -q` passes (0 failed), including a new tests/test_signal.py that was run and failed once before the function was written. The tests put only fake nmcli, iw and ip on PATH, fed with the fixture from the goal file, and prove: output equals the target output in the goal file's Context exactly (header, diagram strongest first labelled `<SSID>, <IP>, <short BSSID>, <band>` with `, connected` on the connected row and one block per 5 % rounded, then the table with columns SSID, IP, full BSSID, Band, Ch, Signal, dBm, Rx, Tx sorted by signal); every BSSID nmcli lists appears, hidden ones as `(hidden)`; IP comes from a unique IPv4 ip neigh match on BSSID bytes 2-5, else `?`; dBm missing from the scan dump shows `?`; without nmcli, `signal: Linux only (needs nmcli)` goes to stderr with return 1; `-h` follows the wifi/speedtest help layout. Also: `fish -c 'signal -h'` and one live `fish -c signal` on the Pi print sensible output; README has a section listing wifi, cpu, speedtest and signal, shown by grep; `fish -c 'fish_indent --check (git ls-files "fish/*.fish") fish/functions/signal.fish; echo $status'` prints 0; `./bootstrap.sh --dry` and `./bootstrap.sh -y` report no changes; work is committed on main per CLAUDE.md with docs/backlog/signal-fish.md deleted in the completing commit, `git status --short` empty, nothing pushed. Guardrails: no test deleted, skipped or weakened; edits only to signal.fish, tests/test_signal.py, README.md, deleting the backlog item, and this goal file; no real neighbour SSIDs or BSSIDs committed; config.local.fish, deploy.py and wifi.fish untouched; no name mapping; tests never call the real tools; no connection changes; no push. Out of scope: any change to wifi.fish, name mapping, showing the LAN MAC, filtering networks. Show the output of each check in the transcript. Or stop after 25 turns and report what remains.
```
