#!/bin/bash

if [ $# -lt 2 ]; then
    echo "### HINT ###: Please input the name of pcap file (arg1) and target port name."
    echo "Example: ./trace_sender.sh eno1 xxxxx.pcap"
    exit

sudo tcpreplay -i $1 -tK --loop 1  $2