#!/bin/bash
cd /Users/viet_tran/Workplace/kql/KqlFuture
echo "Run Intraday Job"
nohup python3 src/crawler/intraday.py realtime > logs/intraday.log &
