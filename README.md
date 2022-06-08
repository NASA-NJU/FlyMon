<h1 align="center">
  <br>
  FlyMon
  <br>
</h1>

<h4 align="center">A reference implementation of SIGCOMM'22 Paper <a href="www.google.com" target="_blank">FlyMon</a>.</h4>

<p align="center">
  <a href="#-key-features">Key Features</a> •
  <a href="#-hardware-implementation">Hardware Implementation</a> •
  <a href="#-simulation-framework">Simulation Framework</a> •
  <a href="#-license">License</a> •
  <a href="#-links">Links</a>
</p>

## 🎯 Key Features

* P416-based hardware implementation.
* Jinja2 templates used to generate P4 codes according to variable configurations (e.g., CMU-Groups, Memory Size, Candidate Key Set).
* Several built-in algorithms used to measure various flow attributes.
* A reference control plane framework realizing task reconfiguration, resource management, data collection, and task query.
* A simulation framework to fast explore built-in algorithms' accuracy.

> 🔔 We are improving the richness and reliability of this project. Please submit an issue if you find any problems or suggestiones.

> ⚠️ This repository serves as an early exploration for academics purpose. We do not provide production-level quality assurance. Please deploy the codes cautiously in your environment.

## 🚄 Hardware Implementation

### 🕶️ Overview

The figure below shows that the FlyMon hardware implementation is based on the Tofino hardware platform, including the SDE, runtime interfaces, etc.

<div align="center">
<img src="docs/controlplane.svg" width=80% />
</div>

To better test and use FlyMon, we made some engineering efforts to implement the data plane and the control plane.

For the data plane, our P4 codes are generated using [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) templates (we need to thank the author of [BeauCoup](https://github.com/Princeton-Cabernet/BeauCoup) brings us inspiration). The Jinja2 templates (located in [p4_templates](./p4_templates/)) allow us to flexibly and quickly extend our data plane codes to avoid various bugs. For example, when deploying 9 CMU-Groups, the P4 codes reach over 5000 LOC, which is difficult to maintain manually. More importantly, we can easily modify the configuration of the data plane, such as the number of CMU-Groups, the set of candidate keys, the size of the static memory of a single CMU, etc.

For the control plane, we provide user-friendly, interactive interfaces to dynamically configure tasks (i.e., add and delete tasks). We perform layers of abstraction, gradually shielding the underlying hardware details. When compiling the data plane code, the [FlyMon compiler](./flymon_compiler.py) also generates [a configuration file](./control_plane/cmu_groups.json) for the control plane, which is used to adjust the control plane's interfaces to adapt to user-customized underlayer data plane configurations.

Below we show how to use these codes.

### ⚙️ Requirements

This repository has strict hardware and software requirements.

**Hardware Requirements**

* A tofino-based hardware switch (e.g., Wdege-100BF-XX) or a tofino model.
* At least one server with QSFP28 connectors and wires if you use a hardware switch.

**Software Requirements**

* Switch OS: OpenNetworkLinux 4.14.151
* Python: 3.8.10 
* SDE: Version 9.7.0+ (the same is best)

> 🔔 In this document, all 'python' and 'pip' refer to the python version of 3.8.10.

There are some dependencies for control plane functions. To install them.
```bash
git clone "https://github.com/NASA-NJU/FlyMon.git"
cd FlyMon
pip install -r ./requirements.txt
```

### 🔨 Build Data Plane

To generate your custom data plane code, use the Jinja2 code generator we provide.

```bash
python flymon_compiler.py -n 9 -m memory_level_mini
```

The above command will generate 9 CMU-Groups in the data plane (see [p4src](./p4src/)), and each CMU has a static (maximum) memory type of 'memory_level_mini' (32 counters in each register).  

> 🔔 For easy viewing of memory status, we generate mini-level CMUs (i.e., only 32 16-bit counters in each CMU) here. You can choose a larger level of memory (e.g., memory_level_8) for more practical purposes. The available memory levels are list in `flymon_compiler.py`.

Once the data plane codes are generated, you can build the p4 codes with bf-p4c. Here we give a setup script if you don't known how to compile the codes.

```bash
# If you are working on SDE 9.7.0+
# Make sure you are in the directory of FlyMon, currently.
export FLYMON_DIR=`pwd`     
./setup.sh
```
> 🔔 You also need to check if SDE environment variables (e.g., `SDE` and `SDE_INSTALL`) are set correctly.

> 🔔 The compilation process usually takes 20~60 minutes. Yes, it compiles so slowly QAQ. We expect some deep optimizations for the compiler. Noth taht although the compilation is slow, this does not affect the forwarding performance of the switch after the compilation is complete.

### 🚀 Running FlyMon

Launching FlyMon requires starting the data plane and the control plane separately.

Firstly, load the program for the data plane.

```bash
$SDE/run_switchd.sh -p flymon
```

If you are working on a Tofino Model, we need to run the model **before** running the switchd. You also need to setup several virtual ports for the model.

```bash
$SDE/run_tofino_model.sh -p flymon
$SDE/run_switchd.sh -p flymon
```

Secondly, start the FlyMon interactive control plane in another terminal.
```
cd $FLYMON_DIR/control_plane/
./run_controller.sh
```

If all goes well, you will be taken to the command line interface of FlyMon.

```
----------------------------------------------------
    ______   __            __  ___                
   / ____/  / /  __  __   /  |/  /  ____     ____ 
  / /_     / /  / / / /  / /|_/ /  / __ \   / __ \
 / __/    / /  / /_/ /  / /  / /  / /_/ /  / / / /
/_/      /_/   \__, /  /_/  /_/   \____/  /_/ /_/ 
              /____/                                 
----------------------------------------------------
    An on-the-fly network measurement system.       
    **NOTE**: FlyMon's controller will clear all previous data plane 
              tasks/datas when setup.
    
flymon> 
```
<details><summary><b>You can use `tab`, 'help', and '-h' to get the relevant commands and their prompts.</b></summary>

```
flymon> <tab><tab>
EOF            default_setup  read_cmug      show_task
add_forward    del_task       read_task      
add_port       help           shell          
add_task       query_task     show_cmug   


flymon> add_task -h
usage: controller_main.py [-h] -f FILTER -k KEY -a ATTRIBUTE -m MEM_SIZE

optional arguments:
  -h, --help            show this help message and exit
  -f FILTER, --filter FILTER
                        e.g., 10.0.0.0/8,20.0.0.0/16 or 10.0.0.0/8,* or *,* Default: *,*
  -k KEY, --key KEY     e.g., hdr.ipv4.src_addr/24, hdr.ipv4.dst_addr/32
  -a ATTRIBUTE, --attribute ATTRIBUTE
                        e.g., frequency(1)
  -m MEM_SIZE, --mem_size MEM_SIZE
                        e.g., 32768


flymon> help add_task
 Add a task to CMU-Group.
        Args:
            "-f", "--filter" required=True, e.g., SrcIP=10.0.0.*,DstIP=*.*.*.*
            "-k", "--key" required=True, e.g., hdr.ipv4.src_addr/24,hdr.ipv4.dst_addr
            "-a", "--attribute" type=[frequency, distinct, max, existence], required=True,
            "-m", "--mem_size" type=int, required=True
            **A Complete Example** : 
                add_task -f 10.0.0.0/8,* -k hdr.ipv4.src_addr/24 -a frequency(1) -m 48
                        This will allocate the task, which monitors on packet with SrcIP=10.0.0.*, 
                        and count for key=SrcIP/24, attribute=PacketCount, memory with 48 counters (3x16 count-min sketch)
        Returns:
            Added task id or -1.
        Exceptions:
            parser error of the key, the attribute, the memory. 
```
</details>

Currently, we implement the functions of task deployment, deletion, status show, data reading, etc. We also implement other features, such as the simple configuration of ports and installation forwarding rules. But these functions can also be completed from the original SDE interfaces.

### 📝 Use Cases

We demonstrate the dynamic features of FlyMon through several typical use cases. The flexibility of FlyMon lies in the ability to arbitrarily adjust the flow key, flow attribute, and memory size. The tasks that FlyMon can perform are not limited to the below use cases. We will add more use cases in the future.

<details><summary><b>Frequency Estimation</b></summary>

Suppose we want to measure the frequency (i.e., number of packets) of each SrcIP for the traffic with SrcIP in 10.0.0.0/8.
We can define the key as SrcIP/24 and attribute as frequency(1). We can deploy this measurement task with the `add_task` command.

```
flymon> add_task -f 10.0.0.0/8,* -k hdr.ipv4.src_addr -a frequency(1) -m 48
```

The above command will deploy a Count-Min Sketch (d=3, w=16) in the data plane for this task.

If there are enough resources in the data plane to deploy this measurement task, you will get the following output.

```
Required resources:
[ResourceType: CompressedKey, Content: hdr.ipv4.src_addr/32]
[ResourceType: CompressedKey, Content: hdr.ipv4.src_addr/32]
[ResourceType: CompressedKey, Content: hdr.ipv4.src_addr/32]
[ResourceType: Memory, Content: 16]
[ResourceType: Memory, Content: 16]
[ResourceType: Memory, Content: 16]
----------------------------------------------------
[Active Task] 
Filter= [('10.0.0.0', '255.0.0.0'), ('0.0.0.0', '0.0.0.0')]
ID = 1
Key = hdr.ipv4.src_addr/32
Attribute = frequency(1)
Memory = 48(3*16)
Locations:
 - loc0 = group_id=5, group_type=2, hkeys=[1], cmu_id=1, memory_type:HALF offset:0)
 - loc1 = group_id=5, group_type=2, hkeys=[1], cmu_id=2, memory_type:HALF offset:0)
 - loc2 = group_id=5, group_type=2, hkeys=[1], cmu_id=3, memory_type:HALF offset:0)

[Success] Allocate TaskID: 1 
```
The above output tells us that the task is successfully deployed to CMU-Group 5 and the task identifier in FlyMon is 1. The controller deploys the task with a 3 rows CM-Sketch and divides the 48 counters evenly over the 3 rows. Since we set the memory of each CMU to 32 (i.e., `memory_level_mini`), the memory type of each row is HALF.
We can check the status of CMU-Group and information about the task by `show_cmug` command and `show_task` command, respectively.
```
flymon> show_task -t 1
----------------------------------------------------
[Active Task] 
Filter= [('10.0.0.0', '255.0.0.0'), ('0.0.0.0', '0.0.0.0')]
ID = 1
Key = hdr.ipv4.src_addr/32
Attribute = frequency(1)
Memory = 48(3*16)
Locations:
 - loc0 = group_id=5, group_type=2, hkeys=[1], cmu_id=1, memory_type:HALF offset:0)
 - loc1 = group_id=5, group_type=2, hkeys=[1], cmu_id=2, memory_type:HALF offset:0)
 - loc2 = group_id=5, group_type=2, hkeys=[1], cmu_id=3, memory_type:HALF offset:0)


flymon> show_cmug -g 5
------------------------------------------------------------
                   Status of CMU-Group 5                    
------------------------------------------------------------
Compressed Key 1 (32b): hdr.ipv4.src_addr/32
Compressed Key 2 (16b): Empty
------------------------------------------------------------
CMU-1 Rest Memory: 16
CMU-2 Rest Memory: 16
CMU-3 Rest Memory: 16
------------------------------------------------------------
```

We can read the full memory of the task with the `read_task` command.

```
flymon> read_task -t 1
Read all data for task: 1
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

Now, we inject some traffic into the switch to verify the measurement task.

> 🔔 You can inject traffic into the physical switch through an additional server.  You can also inject traffic into the Tofino Model's virtual interface via software (e.g., [scapy](https://scapy.net/)). Both require the FlyMon data plane's simple_fwd table to be configured in advance. We offer `add_port` and `add_forward` commands to fast configure you switch/model. 

If you are using Tofino Model, we provide some commands to help you perform the tests.

```
flymon> add_forward -s 0 -d 1

flymon> send_packets -l 64 -n 5 -p 0 -s 10.0.0.0/8
```

The `add_forward` command inserts a forwarding rule in `simple_fwd` table of the data plane. It will forward the packets from Port-0 to Port-1 (i.e., DP Port). The `send_packets` command sends 5 packets with length 64 and SrcIP in network range 10.0.0.0/8.

After generating the traffic, we can check the memory of the task again.

```
flymon> read_task -t 1
Read all data for task: 1
[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0]
[0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1]
[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1]
```

The memory above is a visual representation of the Count-min sketch. To query a specific Key (e.g., SrcIP=10.0.0.1), we can use the `query_task` command.

```
flymon> query_task -t 1 -k 10.0.0.1,*,*,*,*

1
```

</details>



<details><summary><b>Dynamic Memory Allocation</b></summary>
Below we show FlyMon's dynamic memory allocation. First we issue two tasks with different memory sizes under the same CMU-Group.

```
flymon> reset_all
flymon> add_task -f 10.0.0.0/8,* -k hdr.ipv4.src_addr/24 -a frequency(1) -m 48
flymon> add_task -f 20.0.0.0/8,* -k hdr.ipv4.src_addr/24 -a frequency(1) -m 24
```
These two tasks have the same key and attribute, but focus on different sets of traffic. The resource manager will assign them to the same CMU-Group.

> 🔔 The `reset_all` command is optional. It will clear all data plane tasks and controller plane status. The purpose of executing this command here is to make it easier for users to follow this manual. In other words, when this command is executed, all subsequent tasks will be allocated from TaskID=1, which is convenient for later manuals with the fixed task_id and CMU-Group allocations. If you do not execute this command. You need to correctly select the TaskID assigned to you by the task manager when you read/query the task.

The first task will be allocated 3x16 buckets, while the second task will be allocated 3x8 buckets. To verify this, we inject some packets into the switch.

> 🔔 You can inject traffic into the physical switch through an additional server.  You can also inject traffic into the Tofino Model's virtual interface via software (e.g., scapy). Both require the FlyMon data plane's simple_fwd table to be configured in advance. We offer `add_port` and `add_forward` commands to fast configure you switch/model. 

If you are using Tofino Model, we provide some commands to help you perform the tests.

```
flymon> add_forward -s 0 -d 1

flymon> send_packets -l 64 -n 10 -p 0 -s 10.0.0.0/8
Send a packet with src_ip=10.0.0.1, pktlen=64.
Send a packet with src_ip=10.0.0.2, pktlen=64
...
flymon> send_packets -l 64 -n 10 -p 0 -s 20.0.0.0/8
Send a packet with src_ip=20.0.0.1, pktlen=64.
Send a packet with src_ip=20.0.0.2, pktlen=64.
...
```

After injecting the traffic of 10.0.0.0/8 and 20.0.0.0/8, we observe the memory status of whole CMU-Group, Task 1, and Task 2 respectively.

```
flymon> read_cmug -g 5
Read all data for CMU-Group 5
[1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
[0, 0, 2, 0, 3, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 3, 0, 2, 2, 0, 3, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0]
[0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
----------------------------------------------------

flymon> read_task -t 1
Read all data for task: 1
[1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0]
[0, 0, 2, 0, 3, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 3]
[0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1]

flymon> read_task -t 2
Read all data for task: 2
[2, 2, 1, 1, 1, 1, 1, 1]
[0, 2, 2, 0, 3, 0, 0, 3]
[1, 2, 2, 1, 1, 1, 1, 1]
```

We can find that the data of both Task 1 and Task 2 are on CMU-Group 5. The memory range of task 1 is [0,16), while the memory range of task 2 is [16,24).

Next, we delete task 1 and its data.

```
flymon> del_task -t 1 -c True

flymon> read_cmug -g 5
Read all data for task: 5
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 3, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
```

Finally, we find that all the data of task 1 is cleared. This use case demonstrates that FlyMon can dynamically distribute measurement tasks to different size and location memory ranges, and achieve isolation between tasks.

</details>


<details><summary><b>Single-key Distinct Counting (Flow Cardinality)</b></summary>

FlyMon uses the HyperLogLog algorithm to implement single-key distinct Count statistics. If we want to count the different number of IP-Pair in the network, we can deploy this task with the following command.

```
flymon> reset_all
flymon> add_task -f *,* -k hdr.ipv4.src_addr -a distinct() -m 32
```
> 🔔 The `reset_all` command is optional. It will clear all data plane tasks and controller plane status. The purpose of executing this command here is to make it easier for users to follow this manual. In other words, when this command is executed, all subsequent tasks will be allocated from TaskID=1, which is convenient for later manuals with the fixed task_id and CMU-Group allocations. If you do not execute this command. You need to correctly select the TaskID assigned to you by the task manager when you read/query the task.

We can inject some packets into the switch like this. For example, using scapy to generate 100 packets with different IP addresses. 

> 🔔 Since the memory in our demo scenario is relatively small (i.e., only 32 16-bits counters in each CMU), we choose a very small size of traffic to be measured. HyperLogLog usually yields more reliable measurements (i.e., smaller variance) in larger traffic scenarios.

If you are using Tofino Model, we provide some commands to help you perform the tests.

```
flymon> add_forward -s 0 -d 1

flymon> send_packets -l 64 -n 100 -p 0 -s 10.0.0.0/8
Send a packet with src_ip=10.0.0.1, pktlen=64.
Send a packet with src_ip=10.0.0.2, pktlen=64.
...
Send a packet with src_ip=10.0.0.98, pktlen=64.
Send a packet with src_ip=10.0.0.99, pktlen=64.
Send a packet with src_ip=10.0.0.100, pktlen=64.
```

After inserting the traffic, we can query the measurement data of the single-key distinct counting task.

```
flymon> read_task -t 1
Read all data for task: 1
[0, 49151, 57113, 0, 34029, 49119, 57145, 62474, 42159, 40861, 65403, 0, 0, 40893, 65371, 0, 57113, 58411, 38092, 49151, 57145, 0, 0, 49119, 65403, 0, 0, 40861, 65371, 50281, 46222, 40893]

```
As you can see, the output of the original measurement data is not intuitive. We implement the HLL algorithm data parsing in the `query_test` command.

```
flymon> query_task -t 1
133
```

The results seem not accurate enough because we used a minimal number of packets and a tiny amount of memory. HyperLogLog usually yields more reliable measurements (i.e., more minor variance) in more significant traffic scenarios. More importantly, adjusting the data plane hash function parameters is also a technical task. We will further optimize the configuration of the FlyMon data plane's hash functions in the future.

</details>


<details><summary><b>Capture Maximum Packet Size</b></summary>

Here, we show how to use FlyMon to measure the max attribute and how to set standard metadata as an attribute parameter.
We do this by measuring the maximum packet size for each flow. We can deploy such a task with the following command.

```
flymon> reset_all
flymon> add_task -f *,* -k hdr.ipv4.src_addr -a max(pkt_size) -m 32
```

> 🔔 The `reset_all` command is optional. It will clear all data plane tasks and controller plane status. The purpose of executing this command here is to make it easier for users to follow this manual. In other words, when this command is executed, all subsequent tasks will be allocated from TaskID=1, which is convenient for later manuals with the fixed task_id and CMU-Group allocations. If you do not execute this command. You need to correctly select the TaskID assigned to you by the task manager when you read/query the task.

Then we generate several packets of different sizes. If you are using Tofino Model, we provide some commands to help you perform the tests.

```
flymon> add_forward -s 0 -d 1

flymon> send_packets -l 64 -n 10 -p 0 -s 10.0.0.0/8
...
flymon> send_packets -l 80 -n 10 -p 0 -s 10.0.0.0/8
...
```

Finally, we can get the following measurement results.

```
flymon> read_task -t 1
Read all data for task: 1
[80, 80, 80, 0, 0, 80, 0, 0, 80, 80, 0, 80, 80, 0, 80, 80]
[0, 0, 80, 0, 80, 0, 0, 0, 0, 80, 0, 0, 0, 0, 0, 80]
[0, 80, 80, 80, 0, 0, 0, 0, 80, 80, 80, 0, 80, 80, 80, 80]

flymon> query_task -t 1 -k 10.0.0.1,*,*,*,*
80
```

The underlying logic of the Max property is the SuMax algorithm, which obtains the closest estimate to the actual value by minimizing the value of multiple rows.
In addition to packet size, FlyMon currently supports standard metadata, including queue length, timestamp, etc.

</details>

## 📏 Simulation Framework

For the convenience of accuracy estimation, we implemented a simulated version of FlyMon in C++ to test the algorithms' accuracy. Note that the simulation is not a simple implementation of the algorithms with c++. It also uses match-action tables to construct the measurement algorithms, just like the hardware implementation. In addition, we built an automated testing framework for repeating the experiment. The simulation code is located in the [simulations](./simulations) directory.

## ⚠️ Licsense

The project is released under the [GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.html).

## 🔗 Links

* [Open-source Tofino](https://github.com/barefootnetworks/Open-Tofino).
* [BeauCoup](https://github.com/Princeton-Cabernet/BeauCoup).


