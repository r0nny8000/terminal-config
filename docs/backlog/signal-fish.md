---
status: open
priority: medium
acceptance:
  - `signal` is its own fish function in `fish/functions/signal.fish`; `wifi` stays unchanged
  - It covers every access point of the connected SSID on the connected band, strongest first
  - First a diagram, one row per access point with a bar of one block per 5 % signal (rounded), connected row marked `connected`
  - Below it a table with the details per access point: name, BSSID, IP, channel, signal %, dBm, rx and tx bitrate, rows sorted by Signal from high to low
  - An access point gets its device name when its BSSID matches `signal_names` in `config.local.fish`; without a match it shows its IP and MAC (BSSID) instead, `?` when the IP is unknown
  - On macOS, or on Linux without nmcli, `signal` prints `signal: Linux only (needs nmcli)` and exits 1
  - `signal -h` prints help in the same style as `wifi -h` and `speedtest -h`
  - `uv run --with pytest pytest -q` passes, `fish_indent --check fish/**/*.fish` is clean, `pyinfra @local deploy.py --dry` is clean and a second full run reports zero changes
---

# Add a `signal` fish function: connected access point and signal strength

With two repeaters and the router all broadcasting the same SSID, the first
question when the Pi is slow is which one it is on. Answering that has meant
reading raw `nmcli` and `iw` output and knowing which BSSID belongs to which
device. On 2026-11-08 the Pi sat on the far repeater at -63 dBm (510 Mbit/s)
while the near one offered -46 dBm (1201 Mbit/s).

Target output, with names for two devices and none for the third (values from
the 2026-11-08 scan):

    Signal on 5 GHz for network office:

      Repeater R1, connected        84 %  █████████████████
      Repeater R2                   55 %  ███████████
      10.9.8.1 02:AB:CD:77:88:C0    47 %  █████████

    | Device      | BSSID             | IP        | Ch | Signal |    dBm | Rx Mbit/s | Tx Mbit/s |
    | ----------- | ----------------- | --------- | -- | ------ | ------ | --------- | --------- |
    | Repeater R1 | 0A:11:22:33:44:51 | 10.9.8.37 | 40 |   84 % |    -50 |    1200.9 |    1200.9 |
    | Repeater R2 | 02:AB:CD:55:66:C1 | ?         | 40 |   55 % |    -67 |     (270) |     (270) |
    | -           | 02:AB:CD:77:88:C0 | 10.9.8.1  | 40 |   47 % |    -72 |     (540) |     (540) |

In this example the router has no entry in `signal_names`, so the diagram
shows its IP and MAC instead of a name.

Rx and tx are the real link bitrates for the connected access point only. For
the others nothing is measured, so the table shows the maximum rate the access
point advertises, in brackets.

## Plan

Files:

| File                          | Change                                                                 |
| ----------------------------- | ---------------------------------------------------------------------- |
| `tests/test_signal.py`        | New, written first: fake `nmcli`, `iw` and `ip` on a clean PATH, like `test_speedtest.py`, fed with the 2026-11-08 scan |
| `fish/functions/signal.fish`  | New function                                                           |
| `README.md`                   | Mention `signal` and the `signal_names` variable                       |

Data sources, all of them work without sudo (checked on the Pi on 2026-11-08):

| Value                       | Command                                                          |
| --------------------------- | ---------------------------------------------------------------- |
| Access points, signal %, max rate, connected marker | `nmcli -t -f IN-USE,BSSID,SSID,CHAN,FREQ,SIGNAL,RATE dev wifi list --rescan yes` (terse mode escapes `:` in BSSIDs as `\:`) |
| dBm per access point        | `iw dev <iface> scan dump`                                       |
| Real rx and tx bitrate      | `iw dev <iface> link`                                            |
| IP per access point         | `ip neigh show dev <iface>`                                      |

- Names come from a fish list in `~/.config/fish/config.local.fish`, entries
  `BSSID-part=Name`, matched as a case-insensitive substring of the BSSID:

      set -g signal_names '77:88=router' '55:66=Repeater R2' '33:44=Repeater R1'

  Kept out of the repo because the MAC addresses are machine-specific and the
  repo is public (CLAUDE.md, under Code).
- IP lookup: a device's LAN MAC is not its BSSID. They differ in the first byte
  (the locally administered bit) and the last byte, e.g. BSSID
  `0A:11:22:33:44:51` and LAN MAC `08:11:22:33:44:41` for 10.9.8.37. So match the
  neighbour table on bytes 2 to 5 of the BSSID. This is a heuristic based on how
  the devices here number their interfaces.
- Interface detection: copy the small `/sys/class/net/*/wireless` loop from
  `wifi.fish`. Fish autoloads one function per file, and sharing four lines is
  not worth a helper file.
- Linux-only check: `command -q nmcli`, not an OS test, so a Linux box without
  NetworkManager gets the same clear message.

Risks:

- The IP column is empty (`?`) for a device the Pi has not talked to recently,
  because the neighbour table only holds recent contacts. On 2026-11-08 the
  Repeater R2 was missing from it. The fallback name is then `? 02:AB:CD:55:66:C1`.
- The IP heuristic can fail for other vendors. A wrong IP is worse than none,
  so a match must be unique on bytes 2 to 5, otherwise show `?`.
- `--rescan yes` takes a few seconds and may be refused when NetworkManager
  scanned recently; nmcli then returns the cached list, which is fine.
- No new tool in `TOOLS`: `nmcli`, `iw` and `ip` ship with Raspberry Pi OS.

## Checklist

- [ ] Failing tests in `tests/test_signal.py` for each acceptance line
- [ ] `fish/functions/signal.fish`
- [ ] Help text and README
- [ ] `signal_names` in the Pi's `config.local.fish`
- [ ] Acceptance: all tests green, `fish_indent` clean, deploy re-run reports zero changes
