# terminal-config

My terminal environment as code: the tools, the fish configuration and the login
shell. `deploy.py` is a [pyinfra](https://pyinfra.com) deploy that makes a machine
match this repo — macOS via Homebrew, Debian via apt, locally or over SSH.

## What it does

1. Keeps `~/.config/fish` a real directory and links `config.fish`, `conf.d` and
   `functions` inside it into this repo, so editing a function here is live.
   Anything already at those paths is moved aside to `<name>.<timestamp>`.
2. Creates an empty `config.local.fish` if nothing is there — untracked, for
   secrets and machine-specific values.
3. Installs the tools the fish functions call, from the `TOOLS` table in
   `deploy.py`. On Debian, bandwhich comes from its release archive and
   `vcgencmd` only on a Raspberry Pi.
4. Reports the tools no package manager has: claude, nerdctl, pyenv.
5. Lists fish in `/etc/shells` and makes it the login shell.

Re-running completes whatever is missing and touches nothing already in place.

## Bootstrap

pyinfra is the one prerequisite — unlike the bash installer this replaces, the
target needs Python first. A stock Debian or Raspberry Pi OS has neither uv nor
pipx, and its Python is marked externally managed, so `pip install` is refused:

    curl -LsSf https://astral.sh/uv/install.sh | sh    # uv, into ~/.local/bin
    uv tool install pyinfra                            # or: pipx install pyinfra

Both land in `~/.local/bin`, which fish only has on PATH via
`config.local.fish` — so bootstrap from bash, or add it first.

## Run

    pyinfra @local deploy.py --dry          # preview, changes nothing
    pyinfra @local deploy.py                # this machine; shows the changes, then asks
    pyinfra @local deploy.py -y             # the same, without the confirmation prompt
    pyinfra username@pi.local deploy.py     # a machine over SSH
    pyinfra @docker/debian:13 deploy.py     # clean Debian, end to end

`-y` is needed wherever there is no TTY — without it pyinfra exits with
`EOFError` at the prompt. Do not combine it with `--dry`: `-y` skips change
detection, so the preview reports `Skipping change detection` and nothing else.

A run with nothing to install needs no sudo at all. One that does — a missing
package, or `/etc/shells` on a fresh machine — needs the password, and pyinfra
decides to ask by matching sudo's own output against the English `sudo: a
password is required`. On a system with another locale nothing matches, so
instead of a prompt the host is dropped with `could not load fact`. Force the
locale for the run:

    env LC_ALL=C pyinfra @local deploy.py   # any non-English system

Only pyinfra's own messages change. In fish this needs `env`; there is no
inline `VAR=value command`.

## Verify

    pyinfra @local deploy.py --dry -vv      # the exact shell commands
    pyinfra @local deploy.py                # apply, then run it again:
    pyinfra @local deploy.py                # every operation must no-op
    fish_indent --check fish/**/*.fish

The Docker run prints an image ID; `pyinfra @docker/<id> deploy.py` then proves
idempotency on a machine that started empty. Finally open a new terminal and
check `l`, `ll`, `c README.md`, `g`, `z`, Ctrl-R, and that
`readlink ~/.config/fish/functions` resolves into this repo.

## Layout

    deploy.py    the whole installer; the TOOLS table is the part you edit
    fish/        config.fish, conf.d/, functions/ — linked into ~/.config/fish
    CLAUDE.md    conventions for working in here

Why anything is the way it is: `git log --grep='^Decision:'`.
