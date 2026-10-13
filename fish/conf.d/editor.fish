# Programs like git and crontab open $EDITOR. The guard keeps a machine without
# Neovim on their built-in default instead of a command that does not exist.
if command -q nvim
    set -gx EDITOR nvim
end
