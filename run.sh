#!/bin/bash
cd /root/icbc-test
/root/icbc-test/venv/bin/python main.py >> log.txt

killall -9 chromedriver
killall -9 chrome
