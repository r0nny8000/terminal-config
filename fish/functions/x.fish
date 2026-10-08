function x --description 'tmux shortcut, lists sessions when called bare'
    if test (count $argv) -eq 0
        tmux ls
    else
        tmux $argv
    end
end
