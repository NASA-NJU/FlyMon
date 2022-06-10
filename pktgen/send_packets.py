# Python 3.8.10
from scapy.all import *
import argparse
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--len", dest="len", type=int, required=False, default=64, help="e.g., 64")
parser.add_argument("-n", "--num", dest="num", type=int, required=False, default=1, help="e.g., 1")
parser.add_argument("-p", "--port", dest="port", type=str, required=True, help="e.g., eno0")
parser.add_argument("-s", "--srcip", dest="srcip", type=str, required=True, help="e.g., 10.0.0.0/24")
parser.add_argument("-d", "--dstip", dest="dstip", type=str, required=False, default="172.16.0.0/16", 
                                        help="e.g., 30.60.90.0/24 ")

args = parser.parse_args()
packet_num = args.num
packet_size = args.len
port = args.port
if packet_num <= 0 or packet_size < 64 :
    print(f"Invalid Inputs: packet_num {packet_num} packet_size {packet_size}")
    exit(1)
net_src = ipaddress.ip_network(args.srcip)
net_dst = ipaddress.ip_network(args.dstip)
count = 0
skip_num = 0
while count != packet_num:
    for src_ip in net_src.hosts():
        pos = 0
        for dst_ip in net_dst.hosts():
            if pos < skip_num:
                pos += 1
                continue
            if count < packet_num:
                pkt = Ether(src="00:00:00:00:00:00", dst="ff:ff:ff:ff:ff:ff") / IP(src=src_ip, dst=dst_ip) / UDP(dport=4321, sport=1234)
                pkt = pkt / ('a'* (packet_size-4 - len(pkt)))
                sendp(pkt, iface=port, verbose=0)
                skip_num += 1
                if skip_num >= 2**(32 - net_dst.prefixlen):
                    skip_num = 0
                count += 1
                print(f"[{port}]: send a packet with src_ip={src_ip}, dst_ip={dst_ip}, pktlen={packet_size}.")
                break
            else:
                print("Done.")
                exit(0)