function speedtest --description 'Download speed from Hetzner Nuremberg in MB/s and Mbit/s'
    argparse --max-args 1 h/help -- $argv
    or return

    set -l base https://nbg1-speed.hetzner.com

    if set -q _flag_h
        echo "Usage: speedtest [SIZE]"
        echo "       speedtest [-h | --help]"
        echo ""
        echo "Measure download speed with a Hetzner test file (Nuremberg)."
        echo "Runs: curl -s -o /dev/null -w '%{speed_download}' $base/100MB.bin"
        echo ""
        echo "Sizes:"
        printf "  %-6s%s\n" 100M "100MB.bin (default)"
        printf "  %-6s%s\n" 1G "1GB.bin, for fast lines"
        printf "  %-6s%s\n" 10G "10GB.bin"
        echo ""
        echo "Options:"
        echo "  -h, --help  Show this help message and exit"
        return 0
    end

    # The server only offers these three files; there is no 10MB.bin.
    set -l file
    switch "$argv[1]"
        case '' 100M
            set file 100MB.bin
        case 1G
            set file 1GB.bin
        case 10G
            set file 10GB.bin
        case '*'
            echo "speedtest: unknown size '$argv[1]'; use 100M, 1G or 10G" >&2
            return 1
    end

    echo "Downloading $file from nbg1-speed.hetzner.com ..."

    # curl rather than wget: macOS ships curl but not wget, and
    # %{speed_download} gives bytes/s directly.
    set -l bytes (curl -s -o /dev/null -w '%{speed_download}' $base/$file)
    set -l code $status
    if test $code -ne 0
        echo "speedtest: download failed (curl exit $code)" >&2
        return 1
    end

    # Decimal units, because ISP plans quote Mbit/s as 10^6 bits.
    printf "%.1f MB/s  %.1f Mbit/s\n" (math $bytes / 1000000) (math $bytes x 8 / 1000000)
end
