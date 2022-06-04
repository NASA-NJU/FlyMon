# -*- coding:UTF-8 -*-
import os
import logging
import time
import traceback
import json
import cmd
import argparse
import sys

import bfrt_grpc.client as gc

# import bfrt_grpc.client as client
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
            cmug_configs = json.load(open(config_file, 'r'))
            self.runtime = None
            self.grpc_setup(0, 'flymon')
            self.task_manager = TaskManager(self.runtime, cmug_configs)
            self.resource_manager = ResourceManager(self.runtime, cmug_configs)
            self.data_collector = DataCollector(self.runtime, cmug_configs)
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
        args = parser.parse_args(arg.split())
        if parser.error_message or args is None:
            print(parser.error_message)
            return
        # Normal Logic
        self.resource_manager.show_status(args.group_id)
        print("\n")
    
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
        args = parser.parse_args(arg.split())
        if parser.error_message or args is None:
            print(parser.error_message)
            return
        if args.task_id == -1:
            self.task_manager.show_tasks()
        else:
            self.task_manager.show_task(args.task_id)
        print("\n")

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
        args = parser.parse_args(arg.split())
        if parser.error_message or args is None:
            print(parser.error_message)
            return
        try:
            task_instance = self.task_manager.register_task(args.filter, args.key, args.attribute, args.mem_size)
            print("Required resources:")
            for re in task_instance.resource_list():
                print(str(re))
            locations = self.resource_manager.allocate_resources(task_instance.id, task_instance.resource_list())
            if locations is not None:
                task_instance.locations = locations
                re = self.task_manager.install_task(task_instance.id)
                if re is True:
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

    def do_read_data(self, arg):
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
        args = parser.parse_args(arg.split())
        if parser.error_message or args is None:
            print(parser.error_message)
            return
        try:
            task_instance = self.task_manager.get_instance(args.task_id)
            if task_instance is None:
                print(f"Invalid task id {args.task_id}")
                return
            data = self.data_collector.read(task_instance)
            print(f"Read all data for task: {task_instance.id}")
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
        args = parser.parse_args(arg.split())
        if parser.error_message or args is None:
            print(parser.error_message)
            return
        try:
            task_instance = self.task_manager.get_instance(args.task_id)
            if task_instance is None:
                print(f"Invalid task id {args.task_id}")
                return
            self.resource_manager.release_task(task_instance)
            self.task_manager.uninstall_task(task_instance.id)
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
        try:
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
        args = parser.parse_args(arg.split())
        if parser.error_message or args is None:
            print(parser.error_message)
            return
        try:
            self.forward_table = self.bfrt_info.table_get("FlyMonIngress.simple_fwd")
            self.forward_table.entry_add(
                self.target,
                [self.forward_table.make_key([gc.KeyTuple('ig_intr_md.ingress_port', args.source)])],
                [self.forward_table.make_data([gc.DataTuple('port', args.dest)],
                                            "FlyMonIngress.hit")])
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            return

    def do_query_task(self):
        pass

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