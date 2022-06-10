This directory contains some scripts to inject dubugging packets or replay packet traces (i.e., pcap files).

* `send_packets.py` generates specified debugging packets to a port.
* `trace_sender.sh` uses [tcpreplay](https://tcpreplay.appneta.com/) to send packets according a pcap file.

There are some dependences:

* Python 3.8.10
* Scapy
* Tcpreplay



https://fasterdata.es.net/performance-testing/network-troubleshooting-tools/iperf/multi-stream-iperf3/

For iperf3

iperf3 at 40Gbps and above
Achieving line rate on a 40G or 100G test host requires parallel streams. However, using iperf3, it isn't as simple as just adding a -P flag because each iperf3 process is single-threaded. This means all the parallel streams for one test use the same CPU core. If you are core limited, which is often the case for a 40G or 100G host, adding parallel streams won't help you unless you add additional iperf3 processes which can use additional cores.

Note  that it is not possible to do this using pscheduler to manage iperf3 tests, so this is typically better suited to lab or testbed environments.

To run multiple iperf3 processes for a testing a high-speed host, do the following:

Start multiple servers:

   iperf3 -s -p 5101&; iperf3 -s -p 5102&; iperf3 -s -p 5103 &
and then run multiple clients, using the "-T" flag to label the output:

   iperf3 -c hostname -T s1 -p 5101 &;  
   iperf3 -c hostname -T s2 -p 5102 &; 
   iperf3 -c hostname -T s3 -p 5103 &;
Also, there are a number of additional host tuning settings needed for 40/100G hosts. The TCP autotuning settings may not be large enough for 40G, and you may want to try using the iperf3 -w option to set the window even larger (e.g.: -w 128M). Be sure to check your IRQ settings as well.