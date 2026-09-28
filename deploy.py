"""
Installs the terminal tools, links this repo into ~/.config/fish and makes fish
the login shell. Safe to re-run: it completes whatever is missing.

    pyinfra @local deploy.py              # this machine
    pyinfra @local deploy.py --dry        # show what would change, touch nothing
    pyinfra username@pi.local deploy.py   # a machine over SSH
    pyinfra @docker/debian:13 deploy.py   # smoke test
"""

import re
from io import StringIO
from pathlib import Path

from pyinfra import host, logger
from pyinfra.api.exceptions import DeployError
from pyinfra.facts.files import File, FileContents, Link
from pyinfra.facts.server import Arch, Command, Home, Kernel, User, Which
from pyinfra.operations import apt, brew, files, server

# One row per tool: what the fish functions call -> (homebrew formula, apt
# package). None means that platform cannot supply it, or already has it.
# Base-system tools (awk, sed, grep, find, perl, caffeinate, systemd-inhibit,
# xattr, qlmanage) are deliberately absent.
TOOLS = {
    # tool          homebrew        apt
    "fish":        ("fish",         "fish"),
    "curl":        (None,           "curl"),
    "git":         ("git",          "git"),
    "tig":         ("tig",          "tig"),
    "nvim":        ("neovim",       "neovim"),
    "tree":        ("tree",         "tree"),
    "lsd":         ("lsd",          "lsd"),
    "glow":        ("glow",         "glow"),
    "fzf":         ("fzf",          "fzf"),
    "hostname":    (None,           "hostname"),
    "python":      (None,           "python-is-python3"),  # macOS: pyenv, see MANUAL
    "bat":         ("bat",          "bat"),                # apt installs it as batcat
    "cpu monitor": ("mactop",       "btop"),               # mactop is Apple Silicon only
    "sha256sum":   ("coreutils",    None),                 # gsha256sum; Debian has it
    "zoxide":      ("zoxide",       "zoxide"),
    "bandwhich":   ("bandwhich",    None),                 # Debian: release archive, below
}

# No package manager has these: reported, never installed.
MANUAL = {
    "claude":  "https://claude.com/claude-code",
    "nerdctl": "https://github.com/containerd/nerdctl/releases",
    "python":  "https://github.com/pyenv/pyenv",
}

# Debian stable has no bandwhich (sid only), so take the release binary.
BANDWHICH = "0.23.1"
BANDWHICH_URL = (
    "https://github.com/imsnif/bandwhich/releases/download/"
    f"v{BANDWHICH}/bandwhich-v{BANDWHICH}-{{arch}}-unknown-linux-gnu.tar.gz"
)

# What this repo owns inside ~/.config/fish. Everything else there — fish's own
# fish_variables and completion cache — belongs to the machine, not the repo.
ENTRIES = ("config.fish", "conf.d", "functions")

DEPLOY_DIR = Path(__file__).parent.resolve()

darwin = host.get_fact(Kernel) == "Darwin"
user = host.get_fact(User)
home = host.get_fact(Home)
sudo = user != "root"  # root needs none, and a bare container has none installed
config_home = host.get_fact(Command, command='echo "${XDG_CONFIG_HOME:-$HOME/.config}"')
fish_dir = f"{config_home}/fish"

if darwin:
    # command -v on the absolute paths too: brew is a symlink so a File fact
    # reports False, and an SSH shell may not have it on PATH at all.
    brew_bin = host.get_fact(
        Command,
        command="command -v brew || command -v /opt/homebrew/bin/brew "
        "|| command -v /usr/local/bin/brew || true",
    )
    if not brew_bin:
        raise DeployError("Homebrew is required on macOS, install it first: https://brew.sh")
    brew_dir = brew_bin.rsplit("/", 1)[0]
    brew_env = {"PATH": f"{brew_dir}:/usr/bin:/bin:/usr/sbin:/sbin"}
    # Keep the PATH entry, not the versioned Cellar path it resolves to, so a
    # Homebrew upgrade does not invalidate the passwd entry.
    fish_path = f"{brew_dir}/fish"
else:
    fish_path = "/usr/bin/fish"

# Under @local the links point into this checkout, so editing a function is live.
# Anywhere else the files have to be copied to the target first.
if host.name == "@local":
    link_base = str(DEPLOY_DIR / "fish")
else:
    link_base = f"{home}/.local/share/terminal-config"
    for entry in ENTRIES:
        src = DEPLOY_DIR / "fish" / entry
        dest = f"{link_base}/{entry}"
        if src.is_dir():
            files.sync(name=f"Copy {entry}", src=str(src), dest=dest, delete=True)
        else:
            files.put(name=f"Copy {entry}", src=str(src), dest=dest)

# --- links (first: a package failure must never cost a working config) -------

# force=True replaces the whole-repo symlink left by the old install.sh. An
# existing real directory is left alone, so fish_variables and the completion
# cache survive and stay out of the repo.
files.directory(name="Keep ~/.config/fish a real directory", path=fish_dir, force=True)

for entry in ENTRIES:
    files.link(
        name=f"Link {entry} into the repo",
        path=f"{fish_dir}/{entry}",
        target=f"{link_base}/{entry}",
        force=True,  # anything real there is moved to <path>.<timestamp>
    )

# config.fish sources this unconditionally. Create it only when nothing is there
# at all: it is usually a symlink to a synced file, and files.put would overwrite
# it while files.file(touch=True) raises OperationError on a symlink.
local_config = f"{fish_dir}/config.local.fish"
if (
    host.get_fact(Link, path=local_config) is None
    and host.get_fact(File, path=local_config) is None
):
    files.put(
        name="Create an empty config.local.fish",
        src=StringIO(
            "# Secrets and machine-specific values; tool config goes in conf.d/.\n"
        ),
        dest=local_config,
    )

# --- tools -------------------------------------------------------------------

if darwin:
    brew.packages(
        name="Install the tools from Homebrew",
        packages=sorted({formula for formula, _ in TOOLS.values() if formula}),
        _env=brew_env,
        _ignore_errors=True,  # one unavailable formula must not stop the rest
    )
else:
    # Deliberately no _ignore_errors: apt is transactional, so a failure means
    # the table is wrong and the Docker smoke test should go red.
    apt.packages(
        name="Install the tools from apt",
        packages=sorted({package for _, package in TOOLS.values() if package}),
        update=True,
        cache_time=3600,
        _sudo=sudo,
    )

    # raspi-utils-core exists only on Raspberry Pi OS; asking apt for it anywhere
    # else fails the whole transaction. Replaces install.sh's apt-cache probe.
    model = "".join(host.get_fact(FileContents, path="/proc/device-tree/model") or [])
    if "Raspberry Pi" in model:
        apt.packages(
            name="Install vcgencmd for cpu --temp",
            packages=["raspi-utils-core"],
            _sudo=sudo,
        )

    if not host.get_fact(Which, command="bandwhich"):
        server.shell(
            name=f"Install bandwhich {BANDWHICH} from its release archive",
            commands=[
                f"curl -fsSL {BANDWHICH_URL.format(arch=host.get_fact(Arch))}"
                " | tar -xz --no-same-owner -C /usr/local/bin bandwhich"
            ],
            _sudo=sudo,
            _ignore_errors=True,  # a download failure is not a reason to stop
        )

for tool, url in MANUAL.items():
    if not host.get_fact(Which, command=tool):
        logger.warning(f"{tool} is not installed and needs a manual install: {url}")

# --- login shell -------------------------------------------------------------

# chsh only accepts shells listed here, and the file may not exist yet. Gate the
# write on a plain read: _sudo propagates into the FindInFile fact files.line
# gathers, so declaring it unconditionally asks for a sudo password on every run,
# including runs with nothing to do. /etc/shells is world-readable.
shells = host.get_fact(FileContents, path="/etc/shells") or []
if fish_path not in (line.strip() for line in shells):
    files.line(
        name="List fish in /etc/shells",
        path="/etc/shells",
        line=f"^{re.escape(fish_path)}$",
        replace=fish_path,
        _sudo=sudo,
    )

# getpwnam asks the system user database: /etc/passwd on Linux, Directory
# Services on macOS. perl's q() avoids $ARGV, so nothing needs shell quoting.
current_shell = host.get_fact(
    Command, command=f"perl -e 'print((getpwnam(q({user})))[8])'"
)
if current_shell != fish_path:
    server.shell(
        name="Make fish the login shell",
        commands=[f"chsh -s {fish_path} {user}"],
        _sudo=sudo,
        _ignore_errors=True,
    )
