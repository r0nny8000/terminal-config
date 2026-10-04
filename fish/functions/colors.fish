function colors --description 'Show which colours the terminal can display'
    # Swatches are background colour behind spaces, so they look the same
    # whatever font is in use.
    function __colors_swatch --argument-names r g b
        printf '\e[48;2;%d;%d;%dm  \e[0m' $r $g $b
    end

    echo 'Basic 16 (the terminal palette, normal and bright)'
    for code in (seq 40 47)
        printf '\e[%dm    \e[0m ' $code
    end
    echo
    for code in (seq 100 107)
        printf '\e[%dm    \e[0m ' $code
    end
    echo
    echo

    # Read the theme from the live variables instead of repeating the hex
    # values from config.fish, so the two can never drift apart.
    echo 'fish theme (hex values in fish_color_* and fish_pager_color_*)'
    set -l theme_hexes
    for name in (set --names | string match --regex '^fish_(pager_)?color_.*')
        set -a theme_hexes (string match --regex --groups-only '(?:^|=)([0-9a-fA-F]{6})$' -- $$name)
    end
    for hex in (string lower -- $theme_hexes | sort -u)
        set -l r (math 0x(string sub --start 1 --length 2 $hex))
        set -l g (math 0x(string sub --start 3 --length 2 $hex))
        set -l b (math 0x(string sub --start 5 --length 2 $hex))
        __colors_swatch $r $g $b
        printf ' %s  ' $hex
    end
    echo
    echo

    echo 'Shades, 24-bit (black → pure colour → white)'
    set -l steps 12
    for hue in 'red 255 0 0' 'orange 255 128 0' 'yellow 255 255 0' 'green 0 200 0' \
        'cyan 0 255 255' 'blue 0 64 255' 'purple 128 0 255' 'magenta 255 0 255' \
        'grey 128 128 128'
        set -l parts (string split ' ' $hue)
        printf '%-9s ' $parts[1]
        set -l base $parts[2..4]
        for i in (seq 0 (math $steps - 1))
            __colors_swatch (for c in $base; math --scale 0 "$c * $i / $steps"; end)
        end
        for i in (seq 0 $steps)
            __colors_swatch (for c in $base; math --scale 0 "$c + (255 - $c) * $i / $steps"; end)
        end
        echo
    end
    echo

    # 256-colour mode has only 24 greys, so it shows this ramp as visible
    # steps; with 24-bit colour it blends smoothly.
    echo 'Gradient (smooth = 24-bit colour, stripes = 256 colours or fewer)'
    for i in (seq 0 63)
        set -l v (math --scale 0 "$i * 255 / 63")
        printf '\e[48;2;%d;%d;%dm \e[0m' $v $v $v
    end
    echo

    functions --erase __colors_swatch
end
