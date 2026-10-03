# Per-user installers such as claude's put their binary in ~/.local/bin. fish
# reads no ~/.profile, so without this nothing there is found. --global keeps
# it out of fish_variables, which belongs to the machine, not the repo.
fish_add_path --global --prepend ~/.local/bin
