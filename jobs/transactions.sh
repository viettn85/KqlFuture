#!/bin/bash
cd /Users/viet_tran/Workplace/kql/KqlFuture
echo "Run Transaction Job"
nohup python3 src/crawler/transactions.py realtime > logs/transactions.log &
