# -*- coding:UTF-8 -*-
import os
import logging
import time
import traceback
import json
import cmd
import argparse
from scapy.all import Ether, IP, UDP, sendp
import ipaddress
import prettytable as pt

import bfrt_grpc.client as gc
from task_manager import TaskManager
from resource_manager import ResourceManager
from data_collector import DataCollector
from flymonlib.flymon_runtime import FlyMonRuntime_BfRt

logger = logging.getLogger('FlyMon')
if not len(logger.handlers):
    logger.addHandler(logging.StreamHandler())

class FlyMonArgumentParser(argparse.ArgumentParser):
    """
    Arg parser used for FlyMonRuntime.
    """
    def __init__(self, *args, **kwargs):
        super(FlyMonArgumentParser, self).__init__(*args, **kwargs)

        self.error_message = ''

    def error(self, message):
        self.error_message = message

    def parse_args(self, *args, **kwargs):
        # catch SystemExit exception to prevent closing the application
        result = None
        try:
            result = super(FlyMonArgumentParser, self).parse_args(*args, **kwargs)
        except SystemExit:
            pass
        return result

VPORT_DICT = {}
for i in range(64):
    VPORT_DICT[i] = f'veth{2*i+1}'

class FlyMonController(cmd.Cmd):
    intro = """
----------------------------------------------------
    ______   __            __  ___                
   / ____/  / /  __  __   /  |/  /  ____     ____ 
  / /_     / /  / / / /  / /|_/ /  / __ \   / __ \\
 / __/    / /  / /_/ /  / /  / /  / /_/ /  / / / /
/_/      /_/   \__, /  /_/  /_/   \____/  /_/ /_/ 
              /____/                                 
----------------------------------------------------
    An on-the-fly network measurement system.       
    **NOTE**: FlyMon's controller will clear all previous data plane 
              tasks/datas when setup.
    """
    prompt = 'flymon> '

    def __init__(self, config_file = 'cmu_groups.json'):
        cmd.Cmd.__init__(self)
        try:
            self.cmug_configs = json.load(open(config_file, 'r'))
            self.runtime = None
            self.grpc_setup(0, 'flymon')
            self.task_manager = TaskManager(self.runtime, self.cmug_configs)
            self.resource_manager = ResourceManager(self.runtime, self.cmug_configs)
            self.data_collector = DataCollector(self.runtime, self.cmug_configs)
        except Exception as e:
            print(traceback.format_exc())
            print(f"{e} when loading configure file.")
            exit(1)


    def do_show_cmug(self, arg):
        """
        Show the status of a CMU-Group.
        Args list:
            "-g", "--cmu_group" type=int, required=True, show wich CMU-Group?
        Exception:
            No exception here.
        """
        parser = FlyMonArgumentParser()
        parser.add_argument("-g", "--cmu_group", dest="group_id", type=int, required=True, help="Show which cmu-group?")
        try:
            args = parser.parse_args(arg.split())
            if parser.error_message or args is None:
                print(parser.error_message)
                return
            # Normal Logic
            self.resource_manager.show_status(args.group_id)
            print("\n")
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            return
        
    def do_show_task(self, arg):
        """
        Show the status of a CMU-Group.
        Args list:
            "-t" "--task_id" the ID of a task, e.g., 1
        Exception:
            No exception here.
        """
        parser = FlyMonArgumentParser()
        parser.add_argument("-t", "--task_id", dest="task_id", type=int, default=-1, help="e.g., 1")
        try:
            args = parser.parse_args(arg.split())
            if parser.error_message or args is None:
                print(parser.error_message)
                return
            if args.task_id == -1:
                self.task_manager.show_tasks()
            else:
                self.task_manager.show_task(args.task_id)
            print("\n")
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            return

    def do_add_task(self, arg):
        """ Add a task to CMU-Group.
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
        """
        parser = FlyMonArgumentParser()
        parser.add_argument("-f", "--filter", dest="filter", type=str, required=True, default="*,*", help="e.g., 10.0.0.0/8,20.0.0.0/16 or 10.0.0.0/8,* or *,*  Default: *,*")
        parser.add_argument("-k", "--key", dest="key", type=str, required=True, help="e.g., hdr.ipv4.src_addr/24, hdr.ipv4.dst_addr/32")
        parser.add_argument("-a", "--attribute", dest="attribute", type=str, required=True, help="e.g., frequency(1)")
        parser.add_argument("-m", "--mem_size", dest="mem_size", type=int, required=True, help="e.g., 32768")
        parser.add_argument("-q", "--quiet", "--flag", action="store_true", required=False, help="do not need the log?")
        try:
            args = parser.parse_args(arg.split())
            if parser.error_message or args is None:
                print(parser.error_message)
                return
            task_instance = self.task_manager.register_task(args.filter, args.key, args.attribute, args.mem_size)
            if not args.quiet:
                print("Required resources:")
                for re in task_instance.resource_list():
                    print(str(re))
            locations = self.resource_manager.allocate_resources(task_instance.id, task_instance.resource_list())
            if locations is not None:
                task_instance.locations = locations
                re = self.task_manager.install_task(task_instance.id)
                if re is True:
                    if not args.quiet:
                        self.task_manager.show_task(task_instance.id)
                        print(f"[Success] Allocate TaskID: {task_instance.id} \n")
                else:
                    print(f"[Failed] when install rules for task {task_instance.id}\n")
                    self.resource_manager.release_task(task_instance)
            else:
                print(f"[Failed] when allocating resources for task {task_instance.id}\n")
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            return

    def do_read_task(self, arg):
        """
        Read the data of a task.
        Args list:
            "-t" "--task_id" the ID of a task, e.g., 1
        Return:
            The data of the input task
        Exception:
            Parse error?
        """
        parser = FlyMonArgumentParser()
        parser.add_argument("-t", "--task_id", dest="task_id", type=int, required=True, help="e.g., 1")
        try:
            args = parser.parse_args(arg.split())
            if parser.error_message or args is None:
                print(parser.error_message)
                return          
            task_instance = self.task_manager.get_instance(args.task_id)
            if task_instance is None:
                print(f"Invalid task id {args.task_id}")
                return
            data = self.data_collector.read_task(task_instance)
            print(f"Read all data for task: {task_instance.id}")
            for row in data:
                print(row)
            print("")
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            return


    def do_read_cmug(self, arg):
        """
        Read the data of a task.
        Args list:
            "-g" "--group_ip" the ID of a CMU group, e.g., 1
        Return:
            The memory status of a cmu-group.
        Exception:
            Parse error?
        """
        parser = FlyMonArgumentParser()
        parser.add_argument("-g", "--group_id", dest="group_id", type=int, required=True, help="e.g., 1")
        try:
            args = parser.parse_args(arg.split())
            if parser.error_message or args is None:
                print(parser.error_message)
                return
            data = self.data_collector.read_group(args.group_id)
            print(f"Read all data for CMU-Group {args.group_id}")
            for row in data:
                print(row)
            print("----------------------------------------------------")
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            return

    def do_del_task(self, arg):
        """
        Delete a task.
        Args list:
            "-t", "--task" type=int, required=True
        Return:
            Deleted task id or -1.
        """
        parser = FlyMonArgumentParser()
        parser.add_argument("-t", "--task_id", dest="task_id", type=int, required=True, help="e.g., 1")
        parser.add_argument("-c", "--clear", dest="clear", type=bool, required=False, default=False, help="e.g., False")
        try:
            args = parser.parse_args(arg.split())
            if parser.error_message or args is None:
                print(parser.error_message)
                return
            task_instance = self.task_manager.get_instance(args.task_id)
            if task_instance is None:
                print(f"Invalid task id {args.task_id}")
                return
            self.resource_manager.release_task(task_instance)
            self.task_manager.uninstall_task(task_instance.id)
            if args.clear:
                self.data_collector.clear_task(task_instance)
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            return

    def do_add_port(self, arg):
        '''
        Enable a port on tofino
        Args list:
            "-p", "--port" type=int, required=True
            "-s", "--speed" type=str, required=True
            "-f", "--fec" type=str, required=False
        Return:
            Enabled port id or -1.
        '''
        parser = FlyMonArgumentParser()
        parser.add_argument("-p", "--port", dest="port", type=int, required=True, help="D_P port of the port, int from 0 to 259")
        parser.add_argument("-s", "--speed", dest="speed", type=str, required=True, help="The speed of the port, should be a string in [\"10G\", \"25G\", \"40G\", \"100G\"]")
        parser.add_argument("-f", "--fec", dest="fec", type=str, required=False, default="BF_FEC_TYP_NONE", help="\"BF_FEC_TYP_NONE\" as default")
        try:
            args = parser.parse_args(arg.split())
            if parser.error_message or args is None:
                print(parser.error_message)
                return
            # 100G and 40G port should be only added on lane0
            if args.speed in ["100G", "40G"] and args.port % 4 != 0:
                print("100G and 40G port should be only added on lane0")
                return
            # if the port rate is 100G, the FEC should be RS
            if args.speed == "100G":
                args.fec = "BF_FEC_TYP_RS"
            self.port_table = self.bfrt_info.table_get("$PORT")
            self.port_table.entry_add(
                self.target,
                [self.port_table.make_key([gc.KeyTuple('$DEV_PORT', args.port)])],
                [self.port_table.make_data([gc.DataTuple('$SPEED', str_val="BF_SPEED_"+args.speed),
                                            gc.DataTuple('$FEC', str_val=args.fec),
                                            # gc.DataTuple('$N_LANES', args.port%4+1),
                                            gc.DataTuple('$PORT_ENABLE', bool_val=True)])])
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            return


    def do_add_forward(self, arg):
        '''
        Add a forward rule in simple_fwd
        Args list:
            "-s", "--source" type=int, required=True
            "-d", "--destination" type=int, required=True
        Return:
            Added rule or -1.
        '''
        parser = FlyMonArgumentParser()
        parser.add_argument("-s", "--source", dest="source", type=int, required=True, help="Source port of the forwarding, int from 0 to 259")
        parser.add_argument("-d", "--destination", dest="dest", type=int, required=True, help="Destination port of the forwarding, int from 0 to 259")
        try:
            args = parser.parse_args(arg.split())
            if parser.error_message or args is None:
                print(parser.error_message)
                return
            if args.source not in VPORT_DICT.keys() or args.dest not in VPORT_DICT.keys():
                print(f"Invalid port number {args.source} and {args.dest}")
                return
            self.forward_table = self.bfrt_info.table_get("FlyMonIngress.simple_fwd")
            self.forward_table.entry_add(
                self.target,
                [self.forward_table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', args.source)])],
                [self.forward_table.make_data([gc.DataTuple('port', args.dest)],
                                            "FlyMonIngress.hit")])
        except Exception as e:
            print("OK, the forwarding rules already exist.")
            return

    def do_del_forward(self, arg):
        '''
        Add a forward rule in simple_fwd
        Args list:
            "-s", "--source" type=int, required=True
            "-d", "--destination" type=int, required=True
        Return:
            Added rule or -1.
        '''
        parser = FlyMonArgumentParser()
        parser.add_argument("-s", "--source", dest="source", type=int, required=True, help="Source port of the forwarding, int from 0 to 259")
        try:
            args = parser.parse_args(arg.split())
            if parser.error_message or args is None:
                print(parser.error_message)
                return
            if args.source not in VPORT_DICT.keys() or args.dest not in VPORT_DICT.keys():
                print(f"Invalid port number {args.source} and {args.dest}")
                return
            
        except Exception as e:
            print("OK, the forwarding rules already exist.")
            return

    def do_default_setup(self, arg):
        """Default configs in our testbd.
            self.do_add_port("-p 16 -s 40G")
            self.do_add_port("-p 24 -s 40G")
            self.do_add_forward("-s 16 -d 24")
            self.do_add_forward("-s 24 -d 16")
        """
        self.do_add_port("-p 16 -s 100G")
        self.do_add_port("-p 8 -s 100G")
        self.do_add_forward("-s 16 -d 8")
        self.do_add_forward("-s 8 -d 16")

    def do_teardown(self, arg):
        """Default configs in our testbd.
            self.do_add_port("-p 16 -s 40G")
            self.do_add_port("-p 24 -s 40G")
            self.do_add_forward("-s 16 -d 24")
            self.do_add_forward("-s 24 -d 16")
        """
        self.port_table = self.bfrt_info.table_get("$PORT")
        self.port_table.entry_del(self.target)
        self.forward_table = self.bfrt_info.table_get("FlyMonIngress.simple_fwd")
        self.forward_table.entry_del(self.target)

    def do_send_packets(self, arg):
        """Send several packets to model's virtual ports.
            -n packet_num
            -s packet_size
            -p virtual_port
            -s network address set of src_ip
            -d network address set of dst_ip (optional)
        """
        parser = FlyMonArgumentParser()
        parser.add_argument("-l", "--len", dest="len", type=int, required=False, default=64, help="e.g., 64")
        parser.add_argument("-n", "--num", dest="num", type=int, required=False, default=1, help="e.g., 1")
        parser.add_argument("-p", "--port", dest="port", type=int, required=True, help="e.g., 1")
        parser.add_argument("-s", "--srcip", dest="srcip", type=str, required=True, help="e.g., 10.0.0.0/24")
        parser.add_argument("-d", "--dstip", dest="dstip", type=str, required=False, default="30.60.90.1", 
                                             help="e.g., 30.60.90.1 or 30.60.90.0/24 ")
        try:
            args = parser.parse_args(arg.split())
            if parser.error_message or args is None:
                print(parser.error_message)
                return
            packet_num = args.num
            packet_size = args.len
            port = args.port
            if packet_num < 0 or packet_size < 0 or port not in VPORT_DICT.keys():
                print("Invalid Inputs.")
                return
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
                            sendp(pkt, iface=VPORT_DICT[port], verbose=0)
                            skip_num += 1
                            if skip_num >= 2**(32 - net_dst.prefixlen):
                                skip_num = 0
                            count += 1
                            print(f"Send a packet with src_ip={src_ip}, dst_ip={dst_ip}, pktlen={packet_size}.")
                            break
                        else:
                            print("Done.")
                            return
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            return

    def do_query_task(self, arg):
        """Query a task for a given flowkey.
        Args:
            -t : integer, task_id.
            -k : keys (no space), src_ip/prefix1,dst_ip/prefix2,src_port/prefix3,dst_port/prefix4,protocol/prefix5
                 e.g., 10.0.0.0/24,*,*,*,*
        """
        parser = FlyMonArgumentParser()
        parser.add_argument("-t", "--task_id", dest="task_id", type=int, required=True, help="e.g., 1")
        parser.add_argument("-k", "--key", dest="key", type=str, required=False, default= None,
                                     help="e.g., 10.0.0.0/24,*,*,*,*, \
                                           need to follow the seq of : src_ip/prefix1,src_ip/prefix1,src_ip/prefix1,src_ip/prefix1,src_ip/prefix1")
        try:
            args = parser.parse_args(arg.split())
            if parser.error_message or args is None:
                print(parser.error_message)
                return
            task_instance = self.task_manager.get_instance(args.task_id)
            if task_instance is None:
                print(f"Invalid task id {args.task_id}")
                return
            if args.key is None:
                self.data_collector.query_task(task_instance, None)
            else:
                flow_key = task_instance.generate_key_bytes(args.key)
                self.data_collector.query_task(task_instance, flow_key)
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            return

    def do_reset_all(self, arg):
        """
        Dangerous! Reset the status of the data plane and the control plane.
        """
        try:
            self.task_manager = TaskManager(self.runtime, self.cmug_configs)
            self.resource_manager = ResourceManager(self.runtime, self.cmug_configs)
            self.data_collector = DataCollector(self.runtime, self.cmug_configs)
            print("Reset Done.")
        except Exception as e:
            print(traceback.format_exc())
            print(f"{e} when reset.")
            exit(1)

    def do_delay_test(self, arg):
        """
        Perform the delay test corresponding to the experiments in the paper.
        """
        try:
            # the dict of the commands: {"name of algorithm": [commands]}
            command_dict = {
                "CM Sketch" :    ["-f 10.0.0.0/8,* -k hdr.ipv4.src_addr -a frequency(1) -m 96"],
                "BeauCoup" :     ["-f 10.0.0.0/8,* -k hdr.ipv4.src_addr -a distinct(hdr.ipv4.dst_addr) -m 48"],
                "Bloom Filter" : ["-f 10.0.0.0/8,* -k hdr.ipv4.src_addr -a existence() -m 32"],
                "SuMax(Max)" :   ["-f 10.0.0.0/8,* -k hdr.ipv4.src_addr -a max(pkt_size) -m 48"],
                "HyperLogLog" :  ["-f 10.0.0.0/8,* -k hdr.ipv4.src_addr -a distinct() -m 32"],
                "SuMax(Sum)" :   ["-f 10.0.0.0/8,* -k hdr.ipv4.src_addr -a frequency_sumax(1) -m 32",
                                  "-f 10.0.0.0/8,* -k hdr.ipv4.src_addr -a frequency_sumax(1) -m 32",
                                  "-f 10.0.0.0/8,* -k hdr.ipv4.src_addr -a frequency_sumax(1) -m 32"],
                "MRAC" :         ["-f 10.0.0.0/8,* -k hdr.ipv4.src_addr -a frequency_sumax(1) -m 32"]
            }
            # the dict of the delay: {"name of algorithm": [delay]} 
            delay_dict = {k:[] for k,_ in command_dict.items()}

            # the delay experiment is performed five time, and the avg. value is used
            for _ in range(5):
                for alg, cmds in command_dict.items():
                    start_time = time.time()
                    for cmd in cmds:
                        print(cmd)
                        _ = self.do_add_task(cmd)
                    end_time = time.time()
                    delay_dict[alg].append(end_time - start_time)
                    self.do_reset_all("")
            
            # print the result
            print("The results of the delay experiments are shown below:")
            tb = pt.PrettyTable()
            tb.field_names = ["Algorithm on CMU", "Deployment Delay (ms)"]
            for alg, lats in delay_dict.items():
                # print(alg, f"'s average delay is:\t{sum(lats)/len(lats)*1e3}ms")
                tb.add_row([alg, '%.2f'%(sum(lats)/len(lats)*1e3)])
            print(tb)
                    
        except Exception as e:
            print(traceback.format_exc())
            print(f"{e} when reset.")
            exit(1)


    def do_reconfigure_test(self, arg):
        """
        We initiate 8 reconfiguration events to evaluate 
        the forwarding performance of the network during reconfiguration.
        """
        try:
            event_list = [
                # Batch 1, T = 20
                ("add" , "-f 10.0.0.0/8,* -k hdr.ipv4.src_addr,hdr.ports.src_port -a max(queue_size) -m 24 -q"),
                ("add" , "-f 20.0.0.0/8,* -k hdr.ipv4.dst_addr -a frequency(1) -m 12 -q"),
                # Batch 2, T = 50
                ("del" , "-t 1"),
                ("add" , "-f 30.0.0.0/8,* -k hdr.ipv4.src_addr -a existence() -m 12 -q"),
                ("realoc" , 
                    [
                        ("del" , "-t 2"),
                        ("add" , "-f 20.0.0.0/8,* -k hdr.ipv4.dst_addr -a frequency(1) -m 24 -q")
                    ]
                ),
                # Batch 3, T = 90
                ("del" , "-t 3"),
                ("realoc" , 
                    [
                        ("del" , "-t 4"),
                        ("add" , "-f 40.0.0.0/8,* -k hdr.ipv4.src_addr,hdr.ipv4.dst_addr -a distinct() -m 16 -q"),
                    ]
                ),
                ("del" , "-t 2"),
                ("add" , "-f 40.0.0.0/8,* -k hdr.ipv4.src_addr,hdr.ipv4.dst_addr -a distinct() -m 32 -q"),
            ]
            self.do_reset_all("")
            sec = 1
            while len(event_list) != 0:
                time.sleep(10)
                tp, cmd = event_list.pop(0)
                print(f"Time {sec*10} event type: {tp}.")
                sec = sec + 1
                if tp == "add":
                    _ = self.do_add_task(cmd)
                elif tp == "del":
                    _ = self.do_del_task(cmd)
                else:
                    for tb2, cmd2 in cmd:
                        if tb2 == "add":
                            _ = self.do_add_task(cmd2)
                        elif tb2 == "del":
                            _ = self.do_del_task(cmd2)
                
            self.do_reset_all("")
        except Exception as e:
            print(traceback.format_exc())
            print(f"{e} when reset.")
            exit(1)



    def emptyline(self):
        pass
    
    def do_EOF(self, line):
        print("")
        return True
    
    def do_shell(self, line):
        "Run a shell command"
        print("running shell command:", line)
        output = os.popen(line).read()
        print(output)
        self.last_output = output

    def grpc_setup(self, client_id=0, p4_name=None):
        '''
        Set up connection to gRPC server and bind
        Args: 
         - client_id Client ID
         - p4_name Name of P4 program, 'flymon' in this controller.
        '''
        self.bfrt_info = None

        grpc_addr = 'localhost:50052'        

        self.interface = gc.ClientInterface(grpc_addr, client_id=client_id,
                device_id=0, notifications=None, perform_subscribe=True)
        self.interface.bind_pipeline_config(p4_name)
        self.bfrt_info = self.interface.bfrt_info_get()

        self.target = gc.Target(device_id=0, pipe_id=0xffff)

        self.runtime = FlyMonRuntime_BfRt(self.target, self.bfrt_info)

if __name__ == "__main__":
    FlyMonController().cmdloop()