---
status: open
priority: low
acceptance:
  - `speedtest` downloads a Hetzner test file to /dev/null and prints the speed in MB/s and Mbit/s
  - `speedtest -h` prints help in the same style as `wifi -h` and `cpu -h`
  - Works on the Pi and on the Mac
  - `pyinfra @local deploy.py --dry` is clean and a second full run reports zero changes
---

# Add a `speedtest` fish function

Measuring the line speed has so far meant typing this by hand, and nobody
remembers the URL:

    wget -O /dev/null https://nbg1-speed.hetzner.com/100MB.bin

Put it in `fish/functions/speedtest.fish`.

## Notes

- Server: Hetzner Nuremberg, `https://nbg1-speed.hetzner.com/`. It also has
  `10MB.bin` (quick check) and `1GB.bin` (fast lines). The old
  `speed.hetzner.de` address in the shell history is no longer used.
- Size option, e.g. `speedtest 10` / `speedtest 1G`, with 100 MB as the default.
- Print Mbit/s as well as MB/s, because that's the unit ISP plans use. `wget`
  only prints MB/s.
- `curl -o /dev/null -s -w '%{speed_download}'` returns bytes per second and is
  available on both macOS and Debian, while `wget` is not installed on macOS by
  default. So `curl` is probably the better choice, and its output is easier to
  convert to Mbit/s. If `wget` is kept instead, probe for it in the function
  (see CLAUDE.md, under Code).
- Optional: show the Wi-Fi access point and signal next to the result, because
  that's usually the first question when a result is slow (Linux:
  `iw dev <iface> link`; reuse the interface detection from `wifi.fish`).

## Reference measurement

2026-11-05, Pi on Wi-Fi via the close repeater (−42 dBm, 5 GHz):
100MB.bin at 12.4 MB/s ≈ 99 Mbit/s, which is probably the internet line's limit,
not the Wi-Fi's.
