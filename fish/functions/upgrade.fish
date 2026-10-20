function upgrade --description 'Update all system packages without prompting'
    # Homebrew refuses to run as root and never asks for confirmation,
    # so the macOS path needs neither sudo nor -y.
    if test (uname) = Darwin
        brew update
        and brew upgrade
        and brew autoremove
        and brew cleanup
    else
        sudo apt update
        and sudo apt full-upgrade -y
        and sudo apt autoremove -y
    end
end
