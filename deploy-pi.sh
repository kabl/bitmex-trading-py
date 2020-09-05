#!/usr/bin/env bash

scp -P 23 -r ./src *.ini *.sh requirements.txt README.md pi@37.35.121.16:/home/pi/bitmex_trading_py/