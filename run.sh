#!/usr/bin/env bash


PORT=/dev/ttyACM0
ROOT=root

mpremote connect port:$PORT mount $ROOT exec "import main"
