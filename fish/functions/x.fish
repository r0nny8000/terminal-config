function x --description 'tmux shortcut, picks a session with fzf when called bare'
    if test (count $argv) -gt 0
        tmux $argv
        return
    end

    set -l session (tmux ls -F '#S' 2>/dev/null | fzf --prompt='session> ' --preview 'tmux capture-pane -ep -t {}')
    or return

    # Inside tmux, attach would nest a client; switch-client moves the current one.
    if set -q TMUX
        tmux switch-client -t "=$session"
    else
        tmux attach -t "=$session"
    end
end
