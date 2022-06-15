# Python 3.8.10
from scapy.all import *
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--number", dest="number", type=int, required=True, default=64, help="Number of distinct flows.")
parser.add_argument("-o", "--output", dest="output", type=str, required=False, default="test.pacp", help="the name of output file.")

args = parser.parse_args()
packet_num = args.number
outfile = args.output

def write(file, pkt):
    wrpcap(file, pkt, append=True)  #appends packet to output file

if packet_num <= 0 :
    print(f"Invalid Inputs: packet_num {packet_num}")
    exit(1)

count = 0
distinct = {}
while count != packet_num:
    src_addr = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0x1f1f1f1f)))
    dst_addr = socket.inet_ntoa(struct.pack('>I', random.randint(0x1f1f1f1f, 0xffffffff)))
    pkt = Ether(src="00:00:00:00:00:00", dst="ff:ff:ff:ff:ff:ff") / IP(src=src_addr, dst=dst_addr) / UDP(dport=4321, sport=1234)
    pkt = pkt / ('a'* (64-4 - len(pkt)))
    write(outfile, pkt)
    count += 1
    if count % 1000 == 0:
        print(f"Generated {count} pkts.")
    distinct[(src_addr, dst_addr)] = 1

print(f"flow distinct: {len(distinct)}")
