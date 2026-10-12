# fzf's own fish setup, as its README recommends: Ctrl-R searches history,
# Ctrl-T pastes files and directories, Alt-C changes into a directory.
if command -q fzf
    # fzf's default scheme on a 256-colour terminal uses fixed indexes above 15,
    # which the terminal theme does not remap; 16 makes it follow Tokyo Night.
    set -gx FZF_DEFAULT_OPTS --color=16
    fzf --fish | source
end
