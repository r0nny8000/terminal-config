# terminal-config

My terminal environment as code: the tools, the fish configuration and the login
shell. `deploy.py` is a [pyinfra](https://pyinfra.com) deploy that makes a machine
match this repo — macOS via Homebrew, Debian via apt.

## What it does

1. Keeps `~/.config/fish` a real directory and links `config.fish`, `conf.d` and
   `functions` inside it into this repo, so editing a function here is live.
   Anything already at those paths is moved aside to `<name>.<timestamp>`.
2. Creates an empty `config.local.fish` if nothing is there — untracked, for
   secrets and machine-specific values. Under `@local`, `fish/config.local.fish`
   and `fish/fish_variables` in this checkout link back to the real files in
   `~/.config/fish`, so every fish config is visible here; both are gitignored.
3. Links `~/.config/tmux` into this repo, plus `~/.config/foot` on Linux and
   `~/.config/ghostty` on macOS. On macOS it also removes the old link that the
   retired ghostty-config repo left in Ghostty's Application Support folder.
4. Installs the tools the fish functions call, from the `TOOLS` table in
   `deploy.py`. On Debian, bandwhich comes from its release archive and
   `vcgencmd` only on a Raspberry Pi. On macOS, Ghostty and its font come
   from the `CASKS` list.
5. Reports the tools no package manager has: claude, pyenv.
6. Lists fish in `/etc/shells` and makes it the login shell.

Re-running completes whatever is missing and touches nothing already in place.

## Run

    ./bootstrap.sh --dry     # preview, changes nothing
    ./bootstrap.sh           # apply; shows the changes, then asks

Nothing has to be installed first. On its first run `bootstrap.sh` puts pyinfra
in a virtualenv under `~/.local/share/terminal-config-venv` using Python's own
`venv` — no package manager, no sudo, and nothing added to `PATH`, so it also
works in a shell whose fish config this repo has not linked yet. Debian needs
`python3-venv` present; the script says so if it is missing. To move pyinfra
forward, delete that directory and run again.

A run with nothing to install needs no sudo. One that does — a missing package,
or `/etc/shells` on a fresh machine — asks for the password. `bootstrap.sh`
forces `LC_ALL=C` so that it can: pyinfra decides whether to prompt by matching
sudo's own output against the English `sudo: a password is required`, and under
any other locale it never asks, dropping the host with `could not load fact`
instead.

On macOS, an app or font from `CASKS` that was installed by hand rather than by
Homebrew makes every run fail on it, because Homebrew will not overwrite files
it did not install. Hand it over to Homebrew once, then run again:

    brew install --cask --adopt <cask>    # files identical to the cask's
    brew install --cask --force <cask>    # otherwise: replace them

## Verify

    ./bootstrap.sh --dry -vv    # the exact shell commands
    ./bootstrap.sh              # apply, then run it again:
    ./bootstrap.sh              # every operation must no-op
    fish_indent --check fish/**/*.fish

Then open a new terminal and check `l`, `ll`, `c README.md`, `g`, `z`, Ctrl-R,
and that `readlink ~/.config/fish/functions` resolves into this repo.

On the Pi's own screen, log in and type `term`: foot opens full-screen with
24-bit colour, and `colors` shows a smooth gradient, also inside tmux.

## Layout

    bootstrap.sh  gets pyinfra, then runs deploy.py — the entry point
    deploy.py     the whole installer; the TOOLS table is the part you edit
    fish/         config.fish, conf.d/, functions/ — linked into ~/.config/fish;
                  config.local.fish, fish_variables — untracked links back out
    foot/         foot.ini — linked as ~/.config/foot, Linux only
    ghostty/      config — linked as ~/.config/ghostty, macOS only
    tmux/         tmux.conf — linked as ~/.config/tmux
    CLAUDE.md     conventions for working in here

Why anything is the way it is: `git log --grep='^Decision:'`.

:-)
