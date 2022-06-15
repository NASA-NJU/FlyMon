#!/bin/bash

for i in `seq 1 100`
do
    echo $i: `date +%s`
    ping -i 0.01 -c 65 -q 172.16.100.2 > latencyflymon/latency_sec_${i}.txt
done