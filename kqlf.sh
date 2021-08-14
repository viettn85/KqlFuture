if [ $1 == 'help' ]
then
    while read line; do echo $line; done < kqlf.help
elif [ $1 == 'auth' ]
then
    if [ $# == 3 ]
    then
        echo $2
        echo $3
        authendKey = $2
        python3 src/api/auth.py future \"${authendKey}\" $3
    fi
elif [ $1 == 'orders' ]
then
    python3 src/orders/contracts.py $1
elif [ $1 == 'positions' ]
then
    python3 src/orders/contracts.py $1

elif [ $1 == 'update' ]
then
    python3 src/crawler/intraday.py $2
elif [ $1 == 'scan' ]
then
    python3 src/scan/ducky.py
elif [ $1 == 'buy' ]
then
    python3 src/orders/contracts.py $1 $2 $3 $4 $5 # scan buy 2 920
elif [ $1 == 'sell' ]
then
    python3 src/orders/contracts.py $1 $2 $3 $4 $5 # scan sell 2 920
elif [ $1 == 'cancel' ]
then
    python3 src/orders/contracts.py $1 $2 # scan cancel 5475036
elif [ $1 == 'ducky' ]
then
    python3 src/scan/ducky.py $2 # scan cancel 5475036
elif [ $1 == 'cashflow' ]
then
    python3 src/cashflow/analysis.py $2 # scan cancel 5475036
elif [ $1 == 'shoot' ]
then
    python3 src/chart/ducky.py # kqlf shoot
elif [ $1 == 'bottom' ]
then
    python3 src/scan/bottom.py $2 $3
fi