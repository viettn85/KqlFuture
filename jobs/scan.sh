#!/bin/bash
cd /Users/viet_tran/Workplace/kql/KqlFuture
echo "Run Ducky Pattern Scanning"
nohup python3 src/scan/ducky.py scan > logs/scan.log &
