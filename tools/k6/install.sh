function install() {
    sudo apt-get update -y && sudo apt-get install -y k6
}

"$@"