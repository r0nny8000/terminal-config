function signal --description 'Signal of every visible Wi-Fi access point'
    argparse t/table h/help -- $argv
    or return

    if set -q _flag_h
        echo "Usage: signal [-t | --table]"
        echo "       signal [-h | --help]"
        echo ""
        echo "Show every visible Wi-Fi access point, strongest first, as a bar diagram."
        echo "Runs: nmcli -t -f IN-USE,BSSID,SSID,CHAN,FREQ,SIGNAL,RATE dev wifi list --rescan yes"
        echo "      iw dev <iface> link, iw dev <iface> scan dump, ip neigh show dev <iface>"
        echo ""
        echo "Options:"
        echo "  -t, --table  Show a details table instead of the diagram"
        echo "  -h, --help  Show this help message and exit"
        return 0
    end

    if not command -q nmcli
        echo "signal: Linux only (needs nmcli)" >&2
        return 1
    end

    # Ask nmcli rather than /sys for the interface, so the function only
    # depends on the tools it already needs. LC_ALL=C keeps state names and
    # units English whatever the system locale.
    set -l iface
    for line in (LC_ALL=C nmcli -t -f DEVICE,TYPE,STATE device)
        set -l field (string split : -- $line)
        if test "$field[2]" = wifi -a "$field[3]" = connected
            set iface $field[1]
            break
        end
    end
    if test -z "$iface"
        echo "signal: not connected to Wi-Fi" >&2
        return 1
    end

    set -l match

    # A device's LAN MAC is not its BSSID: on the devices here they
    # differ in the first and last byte. So neighbours are keyed by bytes 2-5.
    # IPv6 entries repeat the same MAC and would make every match ambiguous.
    set -l neigh_ips
    set -l neigh_keys
    for line in (ip neigh show dev $iface)
        if set match (string match -r '^(\d+\.\d+\.\d+\.\d+) .*lladdr ([0-9a-fA-F:]{17})' -- $line)
            set -a neigh_ips $match[2]
            set -a neigh_keys (string lower -- (string sub -s 4 -l 11 -- $match[3]))
        end
    end

    set -l scan_bssids
    set -l scan_dbms
    for line in (iw dev $iface scan dump)
        if set match (string match -r '^BSS ([0-9a-f:]{17})' -- $line)
            set -a scan_bssids $match[2]
            set -a scan_dbms '?'
        else if set match (string match -r '^\s+signal: (-?\d+)' -- $line)
            set scan_dbms[-1] $match[2]
        end
    end

    # Real bitrates exist only for the connected access point.
    set -l link_rx '?'
    set -l link_tx '?'
    for line in (iw dev $iface link)
        if set match (string match -r '^\s+rx bitrate: (\S+)' -- $line)
            set link_rx $match[2]
        else if set match (string match -r '^\s+tx bitrate: (\S+)' -- $line)
            set link_tx $match[2]
        end
    end

    set -l ssids
    set -l ips
    set -l bssids
    set -l bands
    set -l chans
    set -l signals
    set -l dbms
    set -l marks
    set -l rxs
    set -l txs
    for line in (LC_ALL=C nmcli -t -f IN-USE,BSSID,SSID,CHAN,FREQ,SIGNAL,RATE dev wifi list --rescan yes)
        # Terse mode escapes ":" inside a value as "\:"; hide those while splitting.
        set -l field (string replace -a '\:' \x1f -- $line | string split :)
        set field (string replace -a \x1f : -- $field)

        set -l bssid $field[2]
        set -l ssid $field[3]
        test -n "$ssid"; or set ssid '(hidden)'

        # A wrong IP is worse than none, so only a unique match counts.
        set -l key (string lower -- (string sub -s 4 -l 11 -- $bssid))
        set -l ip
        set -l k 1
        for neigh_key in $neigh_keys
            test "$neigh_key" = "$key"; and set -a ip $neigh_ips[$k]
            set k (math $k + 1)
        end
        test (count $ip) -eq 1; or set ip '?'

        set -l dbm '?'
        set -l at (contains -i -- (string lower -- $bssid) $scan_bssids)
        and set dbm $scan_dbms[$at]

        set -l band '2.4 GHz'
        test (string split ' ' -- $field[5])[1] -ge 5000; and set band '5 GHz'

        # Others are not measured, so show their advertised maximum in brackets.
        set -l mark ''
        set -l rx "("(string replace ' Mbit/s' '' -- $field[7])")"
        set -l tx $rx
        if test "$field[1]" = '*'
            set mark connected
            set rx $link_rx
            set tx $link_tx
        end

        set -a ssids $ssid
        set -a ips $ip
        set -a bssids $bssid
        set -a bands $band
        set -a chans $field[4]
        set -a signals $field[6]
        set -a dbms $dbm
        set -a marks $mark
        set -a rxs $rx
        set -a txs $tx
    end

    # Strongest first; sweeping the 0-100 range keeps nmcli's order on ties
    # and needs no external sort.
    set -l order
    set -l level 100
    while test $level -ge 0
        set -l k 1
        for value in $signals
            test $value -eq $level; and set -a order $k
            set k (math $k + 1)
        end
        set level (math $level - 1)
    end

    echo "Signal of all visible networks:"
    echo ""

    if set -q _flag_t
        # Header first in each column, so string pad sizes it to fit.
        set -l c_ssid (string pad -r -- SSID $ssids[$order])
        set -l c_ip (string pad -r -- IP $ips[$order])
        set -l c_bssid (string pad -r -- BSSID $bssids[$order])
        set -l c_band (string pad -r -- Band $bands[$order])
        set -l c_ch (string pad -- Ch $chans[$order])
        set -l c_sig (string pad -- Signal (string replace -r '$' ' %' -- $signals[$order]))
        set -l c_dbm (string pad -w 6 -- dBm $dbms[$order])
        set -l c_rx (string pad -- 'Rx Mbit/s' $rxs[$order])
        set -l c_tx (string pad -- 'Tx Mbit/s' $txs[$order])

        set -l k 1
        while test $k -le (count $c_ssid)
            echo "| $c_ssid[$k] | $c_ip[$k] | $c_bssid[$k] | $c_band[$k] | $c_ch[$k] | $c_sig[$k] | $c_dbm[$k] | $c_rx[$k] | $c_tx[$k] |"
            if test $k -eq 1
                set -l dashes
                for cell in $c_ssid[1] $c_ip[1] $c_bssid[1] $c_band[1] $c_ch[1] $c_sig[1] $c_dbm[1] $c_rx[1] $c_tx[1]
                    set -a dashes (string repeat -n (string length -V -- $cell) -)
                end
                echo "| "(string join ' | ' -- $dashes)" |"
            end
            set k (math $k + 1)
        end
        return 0
    end

    # The first 5 bytes of the BSSID are what tells the devices apart here.
    # No IP here: most access points have none in ip neigh; the table keeps it.
    set -l l_ssid (string pad -r -- $ssids[$order])
    set -l l_short (string pad -r -- (string sub -l 14 -- $bssids[$order]))
    set -l l_band (string pad -r -- $bands[$order])
    set -l l_mark (string pad -r -- $marks[$order])
    set -l l_sig (string pad -w 2 -- $signals[$order])

    set -l k 1
    for value in $signals[$order]
        set -l bar (string repeat -n (math "round($value / 5)") █)
        echo "  $l_ssid[$k]  $l_short[$k]  $l_band[$k]  $l_mark[$k]    $l_sig[$k] %  $bar"
        set k (math $k + 1)
    end
end
