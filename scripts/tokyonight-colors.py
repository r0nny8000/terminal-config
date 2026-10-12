"""Show the TokyoNight Night palette with what each colour is for.

Values and roles come from folke/tokyonight.nvim v4.14.1:
colors/storm.lua + colors/night.lua (hex values), colors/init.lua (derived
roles such as border or search) and groups/base.lua (highlight groups).
"ANSI" is the terminal palette slot foot's tokyonight-night theme gives the
colour.
"""

GROUPS = [
    ("Backgrounds", [
        ("bg_dark1",       "0c0e14", "",          "darkest background; no role in the core theme"),
        ("black",          "15161e", "black",     "borders (derived: bg blended 80% toward black)"),
        ("bg_dark",        "16161e", "",          "status line, popups, sidebars, inactive windows"),
        ("bg",             "1a1b26", "background", "main background (Normal)"),
        ("bg_highlight",   "292e42", "",          "current line (CursorLine, CursorColumn)"),
    ]),
    ("Greys and text", [
        ("fg_gutter",      "3b4261", "",          "line numbers, sign column"),
        ("terminal_black", "414868", "bright black", "unused code, completion hints"),
        ("dark3",          "545c7e", "",          "invisible characters (NonText), inlay hints"),
        ("comment",        "565f89", "",          "comments"),
        ("dark5",          "737aa2", "",          "concealed text, quickfix line numbers"),
        ("fg_dark",        "a9b1d6", "white",     "messages, sidebar text"),
        ("fg",             "c0caf5", "bright white / foreground", "main text (Normal)"),
    ]),
    ("Blues and cyans", [
        ("blue7",          "394b70", "",          "inlay hint background"),
        ("blue0",          "3d59a1", "",          "search match background; visual selection (blended 40%)"),
        ("blue",           "7aa2f7", "blue",      "directories, titles, selected tab, TODO"),
        ("cyan",           "7dcfff", "cyan",      "keywords, preprocessor"),
        ("blue1",          "2ac3de", "",          "types, special characters, completion matches"),
        ("blue2",          "0db9d7", "",          "info diagnostics"),
        ("blue5",          "89ddff", "",          "operators"),
        ("blue6",          "b4f9f8", "",          "no role in the core theme"),
    ]),
    ("Accents", [
        ("magenta",        "bb9af7", "magenta",   "identifiers, statements"),
        ("purple",         "9d7cd8", "",          "no role in the core theme"),
        ("magenta2",       "ff007c", "",          "no role in the core theme"),
        ("orange",         "ff9e64", "",          "constants, current line number, matching bracket, incremental search"),
        ("yellow",         "e0af68", "yellow",    "warnings"),
        ("green",          "9ece6a", "green",     "strings"),
        ("green1",         "73daca", "",          "success messages"),
        ("green2",         "41a6b5", "",          "no role in the core theme"),
        ("teal",           "1abc9c", "",          "hint diagnostics"),
        ("red",            "f7768e", "red",       "substitute highlight"),
        ("red1",           "db4b4b", "",          "errors"),
    ]),
    ("Git signs", [
        ("git.add",        "449dab", "",          "added lines"),
        ("git.change",     "6183bb", "",          "changed lines"),
        ("git.delete",     "914c54", "",          "deleted lines"),
    ]),
]

RESET = "\033[0m"


def rgb(hex_value):
    return tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))


def swatch(hex_value):
    r, g, b = rgb(hex_value)
    return f"\033[48;2;{r};{g};{b}m      {RESET}"


def sample_text(hex_value):
    # The same colour as text on the theme's background, the way it appears in use.
    r, g, b = rgb(hex_value)
    br, bg_, bb = rgb("1a1b26")
    return f"\033[48;2;{br};{bg_};{bb}m\033[38;2;{r};{g};{b}m Text {RESET}"


def main():
    print("TokyoNight Night (folke/tokyonight.nvim v4.14.1), 24-bit colours\n")
    for title, colours in GROUPS:
        print(f"\033[1m{title}{RESET}")
        for name, hex_value, ansi, purpose in colours:
            print(f"  {swatch(hex_value)}{sample_text(hex_value)} "
                  f"{name:<15} #{hex_value}  {ansi:<26} {purpose}")
        print()
    print("foot sets bright red..cyan to the same values as the normal ones, so")
    print("those ANSI slots have no separate brighter shade.")


if __name__ == "__main__":
    main()
