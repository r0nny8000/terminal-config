# herdr has no setting that labels a tab after its directory, so the shell in a
# herdr pane does it. On every prompt, not only on cd: Claude Code renames the
# tab to its /rename name, and the folder name should return as soon as Claude
# exits. The label is read back each time because fish cannot see that rename.
if set -q HERDR_TAB_ID; and command -q herdr
    function __herdr_tab_label --on-event fish_prompt
        set -l name (path basename $PWD)
        set -l label (herdr tab get $HERDR_TAB_ID 2>/dev/null | string match -rg '"label":"([^"]*)"')
        if test "$label" != "$name"
            herdr tab rename $HERDR_TAB_ID $name >/dev/null 2>&1
        end
    end
end
