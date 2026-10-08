function cc --description 'Claude CLI, keeps the machine awake during sessions'
    # argparse strips the flags from $argv; the tmux re-run below needs them.
    set -l original_args $argv
    argparse a/auto 'r/resume=?' C/no-caffeinate h/help -- $argv
    or return

    # caffeinate is macOS-only; systemd-inhibit is the Linux equivalent.
    # --what=idle matches caffeinate -di and needs no authorisation, whereas
    # inhibiting sleep requires polkit and would fail before claude ever runs.
    set -l keepawake
    if command -q caffeinate
        set keepawake caffeinate -di
    else if command -q systemd-inhibit
        set keepawake systemd-inhibit --what=idle --who=cc --why="claude session"
    end

    if set -q _flag_h
        set -l shown "$keepawake"
        test -n "$shown"; or set shown "nothing available on this system"

        echo "Usage: cc [-a | --auto] [-r | --resume [ID]] [-C | --no-caffeinate] [ARGS]..."
        echo "       cc [-h | --help]"
        echo ""
        echo "Short alias for the claude CLI."
        echo "Wraps claude to prevent sleep during sessions, using: $shown"
        echo "Runs inside tmux session cc-<parent>/<dir> when started outside tmux."
        echo ""
        echo "Options:"
        echo "  -a, --auto            Enable auto permission mode (passes --permission-mode auto)"
        echo "  -r, --resume [ID]     Resume a session (interactive picker, or by session ID)"
        echo "  -C, --no-caffeinate   Don't prevent system sleep (skips the wrapper)"
        echo "  -h, --help            Show this help message and exit"
        return 0
    end

    # Over SSH, a dropped connection hangs up the shell and kills claude with it.
    # A tmux server outlives the connection; running cc again in the same
    # directory reattaches instead of starting a second claude.
    if not set -q TMUX; and command -q tmux
        set -l parts (string split -n / $PWD)
        set -l dir (string join / $parts[-2..-1])
        test -n "$dir"; or set dir root
        set -l session cc-(string replace -ar '[.:]' - $dir)
        tmux new-session -A -s $session -c $PWD fish -c 'cc $argv' -- $original_args
        return
    end

    set -l claude_args $argv
    if set -q _flag_a
        set -p claude_args --permission-mode auto
    end
    if set -q _flag_resume
        if test -n "$_flag_resume"
            set -p claude_args --resume $_flag_resume
        else
            set -p claude_args --resume
        end
    end

    if set -q _flag_C; or test -z "$keepawake"
        claude $claude_args
    else
        command $keepawake claude $claude_args
    end
end
