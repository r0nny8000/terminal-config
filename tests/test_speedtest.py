"""
Sources fish/functions/speedtest.fish in a clean fish whose PATH holds only a
fake curl, so the tests never touch the network and prove the function needs
no other external command.
"""

import shutil
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "fish" / "functions" / "speedtest.fish"
FISH = shutil.which("fish")
BASE = "https://nbg1-speed.hetzner.com/"

# Appends its arguments to $FAKE_LOG, prints $FAKE_SPEED the way
# `-w '%{speed_download}'` does, and exits with $FAKE_EXIT.
FAKE_CURL = """#!/bin/sh
echo "$*" >> "$FAKE_LOG"
printf '%s' "$FAKE_SPEED"
exit "${FAKE_EXIT:-0}"
"""


def run(tmp_path, *args, speed="12345678", exit_code=0):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    curl = bin_dir / "curl"
    curl.write_text(FAKE_CURL)
    curl.chmod(0o755)

    log = tmp_path / "curl.log"
    env = {
        "PATH": str(bin_dir),
        "HOME": str(tmp_path),
        "FAKE_LOG": str(log),
        "FAKE_SPEED": speed,
        "FAKE_EXIT": str(exit_code),
    }
    command = f"source {SCRIPT}; speedtest " + " ".join(args)
    result = subprocess.run(
        [FISH, "--no-config", "-c", command],
        env=env,
        capture_output=True,
        text=True,
    )
    calls = log.read_text().splitlines() if log.exists() else []
    return result, calls


def fetched_url(calls):
    assert len(calls) == 1
    return calls[0].split()[-1]


def test_no_argument_fetches_100mb(tmp_path):
    result, calls = run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert fetched_url(calls) == BASE + "100MB.bin"


def test_1g_fetches_1gb(tmp_path):
    result, calls = run(tmp_path, "1G")
    assert result.returncode == 0, result.stderr
    assert fetched_url(calls) == BASE + "1GB.bin"


def test_10g_fetches_10gb(tmp_path):
    result, calls = run(tmp_path, "10G")
    assert result.returncode == 0, result.stderr
    assert fetched_url(calls) == BASE + "10GB.bin"


def test_unknown_size_errors_naming_valid_sizes(tmp_path):
    result, calls = run(tmp_path, "10M")
    assert result.returncode == 1
    assert calls == []
    assert result.stderr.startswith("speedtest: ")
    for size in ("100M", "1G", "10G"):
        assert size in result.stderr


def test_speed_is_converted_with_decimal_units(tmp_path):
    # 12,345,678 bytes/s: decimal gives 12.3 MB/s and 98.8 Mbit/s; binary
    # units would give 11.8 and 94.2, so this tells the two apart.
    result, _ = run(tmp_path, speed="12345678")
    assert result.returncode == 0, result.stderr
    assert "12.3 MB/s" in result.stdout
    assert "98.8 Mbit/s" in result.stdout


def test_curl_failure_errors_and_returns_1(tmp_path):
    result, _ = run(tmp_path, speed="0", exit_code=56)
    assert result.returncode == 1
    assert result.stderr.startswith("speedtest: ")
    assert "MB/s" not in result.stdout


def test_help_follows_wifi_cpu_layout(tmp_path):
    result, calls = run(tmp_path, "-h")
    assert result.returncode == 0
    assert calls == []
    lines = result.stdout.splitlines()
    assert lines[0].startswith("Usage: speedtest")
    assert any(line.startswith("Runs: curl ") for line in lines)
    assert "Options:" in lines
    assert lines[-1] == "  -h, --help  Show this help message and exit"
    for size in ("100M", "1G", "10G"):
        assert size in result.stdout
