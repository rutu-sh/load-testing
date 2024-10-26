#!/bin/bash

function install {
    sudo apt-get update -y && \
    sudo apt-get install -y python3-pip python3-locust smm jq && \
}

"$@"