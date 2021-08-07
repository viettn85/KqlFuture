#!/bin/bash
cd /Users/viet_tran/Workplace/kql/KqlFuture
echo "Run"
nohup python3 src/crawler/transactions.py > logs/transactions.log &
