#!/bin/bash

function install {
    sudo apt-get install -y wrk smem jq
    rm -rf /tmp/go-wrk && git clone https://github.com/tsliwowicz/go-wrk.git /tmp/go-wrk && cd /tmp/go-wrk && go build && sudo mv go-wrk /usr/local/bin/
}

"$@"