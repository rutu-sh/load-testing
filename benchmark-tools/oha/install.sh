#!/bin/bash

function install {
    sudo apt-get update -y && sudo apt-get install -y smem jq
    echo "deb [signed-by=/usr/share/keyrings/azlux-archive-keyring.gpg] http://packages.azlux.fr/debian/ stable main" | sudo tee /etc/apt/sources.list.d/azlux.list
    sudo wget -O /usr/share/keyrings/azlux-archive-keyring.gpg https://azlux.fr/repo.gpg
    sudo apt update
    sudo apt install oha
}

"$@"