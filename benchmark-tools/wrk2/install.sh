#!/bin/bash

function install {
    sudo apt-get update -y && \
    sudo apt-get install -y build-essential libssl-dev git zlib1g-dev smem jq && \
    git clone https://github.com/giltene/wrk2.git && \
    cd wrk2 && \
    make && \
    sudo cp wrk /usr/local/bin/wrk2
}

"$@"