#!/bin/bash


function install_go_wrk {
    {
        cd setup/cloudlab-tools/tools/generic && \
        make install-go 
    } || {
        echo "Failed to install go-wrk"
        exit 1
    } 
    
    {
        source ${HOME}/.profile && \
        sudo apt-get update && \
        rm -rf /tmp/go-wrk && \
        git clone https://github.com/tsliwowicz/go-wrk.git /tmp/go-wrk && \
        cd /tmp/go-wrk && \
        go build && \
        sudo mv go-wrk /usr/local/bin/
    } || {
        echo "Failed to install go-wrk"
        exit 1
    }
}


function install_k6 {
    sudo gpg -k
    sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
    echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
    sudo apt-get update
    sudo apt-get install k6
}


function install_locust {
    sudo apt-get update -y && \
    sudo apt-get install -y python3-pip python3-locust 
}


function install_oha {
    echo "deb [signed-by=/usr/share/keyrings/azlux-archive-keyring.gpg] http://packages.azlux.fr/debian/ stable main" | sudo tee /etc/apt/sources.list.d/azlux.list
    sudo wget -O /usr/share/keyrings/azlux-archive-keyring.gpg https://azlux.fr/repo.gpg
    sudo apt update
    sudo apt install oha 
}


function install_wrk {
    sudo apt-get update -y && sudo apt-get install -y wrk 
}


function install_wrk2 {
    sudo apt-get update -y && \
    sudo apt-get install -y build-essential libssl-dev zlib1g-dev && \
    git clone https://github.com/giltene/wrk2.git && \
    cd wrk2 && \
    make && \
    sudo cp wrk /usr/local/bin/wrk2
}

function setup_loadgen {
    sudo apt-get update -y && sudo apt-get install -y smem jq iftop ifstat ethtool
}


"$@"