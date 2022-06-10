This directory contains some scripts to inject dubugging packets or replay packet traces (i.e., pcap files).

* `send_packets.py` generates specified debugging packets to a port.
* `trace_sender.sh` uses [tcpreplay](https://tcpreplay.appneta.com/) to send packets according a pcap file.

* `iperf100gServer/Client.sh` use multiple iperf3 processes to generate near to 100Gbps traffic between two hosts.

There are some dependences:

* Python 3.8.10
* Scapy
* Tcpreplay


