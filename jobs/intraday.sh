#!/bin/bash
cd /Users/viet_tran/Workplace/kql/KqlFuture
echo "Run Intraday Job"
/usr/local/bin/python3 src/app/run.py > logs/intraday.log
