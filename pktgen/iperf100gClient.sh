#!/bin/bash

ip=172.16.100.1

if [ $# -lt 1 ]; then
    echo "### HINT ###: Please input the number of process"
    echo "Example: iperf100gServer.sh"
    exit
fi

for i in `seq 2 $1`
do
    echo "iperf3 -c $ip -w 12M -T s$i -p 520$i &"
    iperf3 -c $ip -w 12M -T s"$i" -p 520"$i" &
done

echo "iperf3 -c $ip -w 12M -T s1 -p 5201"
iperf3 -c $ip -w 12M -T s1 -p 5201
