#!/bin/bash

function install {
    source ~/.bashrc
    sudo apt-get update && sudo apt-get install -y smem jq
    rm -rf /tmp/go-wrk && git clone https://github.com/tsliwowicz/go-wrk.git /tmp/go-wrk && cd /tmp/go-wrk && go build && sudo mv go-wrk /usr/local/bin/
}

"$@"