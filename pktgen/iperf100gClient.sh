#!/bin/bash

iperf3 -c $ip  -i 5 -t 100 -P 11 -p 5201 & 
iperf3 -c $ip  -i 5 -t 100 -P 11 -p 5202 & 
iperf3 -c $ip  -i 5 -t 100 -P 11 -p 5203 & 