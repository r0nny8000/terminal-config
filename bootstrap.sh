#!/bin/sh
# Get pyinfra, then hand over to it. Obtaining pyinfra is the one thing deploy.py
# cannot do for itself; everything else belongs in deploy.py, not in here.
#
#     ./bootstrap.sh --dry    preview, changes nothing
#     ./bootstrap.sh          apply
#
# Python's own venv module, so there is nothing to install first and nothing new
# on PATH: the absolute path below works in a shell whose fish config this repo
# has not linked yet. To move pyinfra forward, delete the directory and re-run.
#
# LC_ALL=C because pyinfra decides whether to prompt for a sudo password by
# matching sudo's output against the English "sudo: a password is required".
# Under any other locale nothing matches and the run dies with "could not load
# fact" instead of asking. Drop this once pyinfra compares something stabler.
set -eu

venv="${XDG_DATA_HOME:-$HOME/.local/share}/terminal-config-venv"

# The venv's python links to the interpreter it was built from. When pyenv
# uninstalls that version, pyinfra is still there but can no longer start, so
# test that it imports rather than that the file exists, and rebuild otherwise.
if ! "$venv/bin/python" -c 'import pyinfra' 2>/dev/null; then
    python3 -m venv --clear "$venv" 2>/dev/null || {
        echo "bootstrap: python3 -m venv failed; on Debian: sudo apt install python3-venv" >&2
        exit 1
    }
    "$venv/bin/pip" install --quiet --disable-pip-version-check pyinfra
fi

cd "$(dirname "$0")"
exec env LC_ALL=C "$venv/bin/pyinfra" @local deploy.py "$@"
