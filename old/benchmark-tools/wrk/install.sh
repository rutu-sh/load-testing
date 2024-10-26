#!/bin/bash

function install {
    sudo apt-get update -y && sudo apt-get install -y wrk smem jq
}

"$@"