function term --description 'Full-screen foot on the Linux console, for 24-bit colour'
    # cage ignores the console's keyboard setting and reads only XKB_DEFAULT_*,
    # so without these it falls back to a US layout.
    if test -r /etc/default/keyboard
        for line in (string match --regex '^XKB[A-Z]+=.*' </etc/default/keyboard)
            set -l key (string replace --regex '^XKB([A-Z]+)=.*' '$1' -- $line)
            set -l value (string replace --regex '^[^=]*=' '' -- $line | string trim --chars '"')
            if test -n "$value"
                set --function --export XKB_DEFAULT_$key $value
            end
        end
    end
    cage foot
end
