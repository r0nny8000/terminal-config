"""
Sources fish/functions/signal.fish in a clean fish whose PATH holds only fake
nmcli, iw and ip, so the tests never scan the real air and prove the function
needs no other external command.

The office/office-g rows are a live scan from 2026-11-08. The neighbour rows
are made up on the documentation MAC range 00:00:5E:00:53:xx (RFC 7042); never
put real neighbour SSIDs or BSSIDs here.
"""

import shutil
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "fish" / "functions" / "signal.fish"
FISH = shutil.which("fish")

# Deliberately not in signal order, so the test proves the sort.
NMCLI_WIFI = r""" :00\:AB\:CD\:77\:88\:C0:office:6:2437 MHz:67:540 Mbit/s
*:0A\:11\:22\:33\:44\:51:office:40:5200 MHz:95:270 Mbit/s
 :00\:00\:5E\:00\:53\:02::36:5180 MHz:35:540 Mbit/s
 :0A\:11\:22\:33\:44\:52:office-g:40:5200 MHz:94:270 Mbit/s
 :08\:11\:22\:33\:44\:51:office:6:2437 MHz:82:270 Mbit/s
 :00\:AB\:CD\:55\:66\:C1:office:6:2437 MHz:81:270 Mbit/s
 :00\:00\:5E\:00\:53\:01:Nachbar-WLAN:1:2412 MHz:59:130 Mbit/s
 :02\:AB\:CD\:77\:88\:C0:office:40:5200 MHz:50:540 Mbit/s"""

NMCLI_DEVICE = """eth0:ethernet:unavailable
wlan0:wifi:connected
lo:loopback:connected (externally)"""

IW_LINK = """Connected to 0a:11:22:33:44:51 (on wlan0)
\tSSID: office
\tfreq: 5200.0
\tsignal: -43 dBm
\trx bitrate: 1200.9 MBit/s VHT-MCS 9 80MHz short GI VHT-NSS 2
\ttx bitrate: 1200.9 MBit/s VHT-MCS 9 80MHz short GI VHT-NSS 2"""

# No block for 00:ab:cd:55:66:c1, as seen live.
IW_SCAN = """BSS 0a:11:22:33:44:51(on wlan0) -- associated
\tfreq: 5200.0
\tsignal: -43.00 dBm
BSS 0a:11:22:33:44:52(on wlan0)
\tfreq: 5200.0
\tsignal: -44.00 dBm
BSS 08:11:22:33:44:51(on wlan0)
\tfreq: 2437.0
\tsignal: -51.00 dBm
BSS 00:ab:cd:77:88:c0(on wlan0)
\tfreq: 2437.0
\tsignal: -60.00 dBm
BSS 00:00:5e:00:53:01(on wlan0)
\tfreq: 2412.0
\tsignal: -65.00 dBm
BSS 02:ab:cd:77:88:c0(on wlan0)
\tfreq: 5200.0
\tsignal: -70.00 dBm
BSS 00:00:5e:00:53:02(on wlan0)
\tfreq: 5180.0
\tsignal: -79.00 dBm"""

# The IPv6 line shares the router's lladdr and must not count as a second match.
IP_NEIGH = """10.9.8.37 lladdr 08:11:22:33:44:41 STALE
10.9.8.1 lladdr 00:ab:cd:77:88:d0 REACHABLE
fe80::1 lladdr 00:ab:cd:77:88:d0 router STALE"""

DIAGRAM = """Signal of all visible networks:

  office        0A:11:22:33:44  5 GHz    connected    95 %  ███████████████████
  office-g      0A:11:22:33:44  5 GHz                 94 %  ███████████████████
  office        08:11:22:33:44  2.4 GHz               82 %  ████████████████
  office        00:AB:CD:55:66  2.4 GHz               81 %  ████████████████
  office        00:AB:CD:77:88  2.4 GHz               67 %  █████████████
  Nachbar-WLAN  00:00:5E:00:53  2.4 GHz               59 %  ████████████
  office        02:AB:CD:77:88  5 GHz                 50 %  ██████████
  (hidden)      00:00:5E:00:53  5 GHz                 35 %  ███████
"""

TABLE = """Signal of all visible networks:

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
"""

# Each fake appends its name and arguments to $FAKE_LOG and prints the
# fixture for the call it recognises.
FAKES = {
    "nmcli": """#!/bin/sh
echo "nmcli $*" >> "$FAKE_LOG"
case "$*" in
    *"wifi list"*) printf '%s\\n' "$FAKE_NMCLI_WIFI" ;;
    *DEVICE,TYPE,STATE*) printf '%s\\n' "$FAKE_NMCLI_DEVICE" ;;
    *) exit 2 ;;
esac
""",
    "iw": """#!/bin/sh
echo "iw $*" >> "$FAKE_LOG"
case "$*" in
    "dev wlan0 link") printf '%s\\n' "$FAKE_IW_LINK" ;;
    "dev wlan0 scan dump") printf '%s\\n' "$FAKE_IW_SCAN" ;;
    *) exit 2 ;;
esac
""",
    "ip": """#!/bin/sh
echo "ip $*" >> "$FAKE_LOG"
case "$*" in
    "neigh show dev wlan0") printf '%s\\n' "$FAKE_IP_NEIGH" ;;
    *) exit 2 ;;
esac
""",
}


def run(tmp_path, *args, tools=("nmcli", "iw", "ip"), ip_neigh=IP_NEIGH):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in tools:
        fake = bin_dir / name
        fake.write_text(FAKES[name])
        fake.chmod(0o755)

    log = tmp_path / "calls.log"
    env = {
        "PATH": str(bin_dir),
        "HOME": str(tmp_path),
        "FAKE_LOG": str(log),
        "FAKE_NMCLI_WIFI": NMCLI_WIFI,
        "FAKE_NMCLI_DEVICE": NMCLI_DEVICE,
        "FAKE_IW_LINK": IW_LINK,
        "FAKE_IW_SCAN": IW_SCAN,
        "FAKE_IP_NEIGH": ip_neigh,
    }
    command = f"source {SCRIPT}; signal " + " ".join(args)
    result = subprocess.run(
        [FISH, "--no-config", "-c", command],
        env=env,
        capture_output=True,
        text=True,
    )
    calls = log.read_text().splitlines() if log.exists() else []
    return result, calls


def table_rows(stdout):
    """Data rows of the table as lists of stripped cells."""
    lines = [line for line in stdout.splitlines() if line.startswith("|")]
    return [[cell.strip() for cell in line.strip("|").split("|")] for line in lines[2:]]


def test_plain_prints_diagram_only(tmp_path):
    result, _ = run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout == DIAGRAM


def test_table_flag_prints_table_only(tmp_path):
    for i, flag in enumerate(("-t", "--table")):
        sub = tmp_path / str(i)
        sub.mkdir()
        result, _ = run(sub, flag)
        assert result.returncode == 0, result.stderr
        assert result.stdout == TABLE


def test_every_bssid_appears_hidden_as_placeholder(tmp_path):
    result, _ = run(tmp_path, "-t")
    rows = table_rows(result.stdout)
    # Field 2 of a terse line, with nmcli's "\:" escapes undone.
    listed = [line.replace("\\:", "-").split(":")[1].replace("-", ":")
              for line in NMCLI_WIFI.splitlines()]
    assert len(listed) == 8
    assert sorted(row[2] for row in rows) == sorted(listed)
    assert [row[0] for row in rows if row[2] == "00:00:5E:00:53:02"] == ["(hidden)"]


def test_ip_needs_a_unique_ipv4_match(tmp_path):
    # A second IPv4 entry sharing bytes 2-5 with 10.9.8.37 makes it ambiguous.
    neigh = IP_NEIGH + "\n10.9.8.38 lladdr 0a:11:22:33:44:42 STALE"
    result, _ = run(tmp_path, "-t", ip_neigh=neigh)
    assert result.returncode == 0, result.stderr
    ips = {row[2]: row[1] for row in table_rows(result.stdout)}
    for bssid in ("0A:11:22:33:44:51", "0A:11:22:33:44:52", "08:11:22:33:44:51"):
        assert ips[bssid] == "?"
    # The router keeps its IP: its IPv6 line is not a second match.
    assert ips["00:AB:CD:77:88:C0"] == "10.9.8.1"
    assert ips["00:AB:CD:55:66:C1"] == "?"


def test_bssid_missing_from_scan_dump_shows_unknown_dbm(tmp_path):
    result, _ = run(tmp_path, "-t")
    dbm = {row[2]: row[6] for row in table_rows(result.stdout)}
    assert dbm["00:AB:CD:55:66:C1"] == "?"
    assert dbm["0A:11:22:33:44:51"] == "-43"


def test_without_nmcli_errors_linux_only(tmp_path):
    result, calls = run(tmp_path, tools=("iw", "ip"))
    assert result.returncode == 1
    assert result.stderr == "signal: Linux only (needs nmcli)\n"
    assert result.stdout == ""
    assert calls == []


def test_help_follows_wifi_speedtest_layout(tmp_path):
    result, calls = run(tmp_path, "-h")
    assert result.returncode == 0
    assert calls == []
    lines = result.stdout.splitlines()
    assert lines[0].startswith("Usage: signal")
    assert any(line.startswith("Runs: nmcli ") for line in lines)
    assert "Options:" in lines
    assert any(line.startswith("  -t, --table") for line in lines)
    assert lines[-1] == "  -h, --help  Show this help message and exit"


def test_makes_no_connection_changes(tmp_path):
    _, calls = run(tmp_path)
    assert calls
    for call in calls:
        assert " connect" not in call and " set " not in call
