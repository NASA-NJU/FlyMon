#!/bin/bash

epoch_num=30

for i in `seq 1 12`
do
    knum_normal=$[RANDOM%2000+9000]
    python3 trace_gen.py -n ${knum_normal} -o epoch${i}_k${knum_normal}.pcap
done

for i in `seq 13 18`
do
    knum_surge=$[RANDOM%10000+90000]
    python3 trace_gen.py -n ${knum_surge} -o epoch${i}_k${knum_surge}.pcap
done

for i in `seq 19 30`
do
    knum_normal=$[RANDOM%2000+9000]
    python3 trace_gen.py -n ${knum_normal} -o epoch${i}_k${knum_normal}.pcap
done