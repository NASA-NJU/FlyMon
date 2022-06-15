#!/bin/bash

if [ $# -lt 1 ]; then
    echo "### HINT ###: Please input the number of process"
    echo "Example: iperf100gServer.sh"
    exit
fi

rm -f *.txt

for i in `seq 2 $1`
do
    ip="172.16.100.1"
    port="520$i"
    iperf3 -s -B $ip -p $port > server$i.txt 2>&1 &
done

iperf3 -s -B 172.16.100.1 -p 5201 > server1.txt 2>&1