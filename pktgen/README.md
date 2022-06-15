This directory contains some scripts to inject dubugging packets or replay packet traces (i.e., pcap files).

* `send_packets.py` generates specified debugging packets to a port.
* `trace_sender.sh` uses [tcpreplay](https://tcpreplay.appneta.com/) to send packets according a pcap file.

* `iperf100gServer/Client.sh` use multiple iperf3 processes to generate near to 100Gbps traffic between two hosts.

There are some dependences:

* Python 3.8.10
* Scapy
* Tcpreplay

How to generate 100G iperf flows:


sudo ifconfig enp130s0 172.16.100.2

sudo ip route add 172.16.100.0/24 dev enp130s0f1


echo 'net.core.wmem_max=12582912' >> /etc/sysctl.conf
echo 'net.core.rmem_max=12582912' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_rmem = 4096 87380 12582912' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_wmem = 4096 87380 12582912' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_window_scaling = 1' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_sack = 1' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_no_metrics_save = 1' >> /etc/sysctl.conf
echo 'net.core.netdev_max_backlog = 5000' >> /etc/sysctl.conf
sysctl -p


### For edit packets


tcprewrite --mtu=100 --mtu-trunc -i one_sec_more/one_sec_1.pcap -o one_sec_ready/one_sec_1_ready.pcap

### For analyze

 ./analyze_pcap.py -i ../pkts/one_sec_ready/one_sec_1_ready.pcap -d ready_info -o traceinfo1


### For send packets

sudo tcpreplay -i enp130s0f1 -tK --loop 1  --pktlen one_sec_1_ready.pcap

add_task -f *,* -k hdr.ipv4.src_addr,hdr.ipv4.dst_addr -a frequency(1) -m 24576


evaluate_are -t 1 -f trace_info/traceinfo1.json