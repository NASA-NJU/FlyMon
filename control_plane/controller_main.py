# -*- coding:UTF-8 -*-
import os
import logging
import time
import traceback
import json
import cmd
import argparse
import sys
import bfrt_grpc.client as client
from task_manager import TaskManager
from resource_manager import ResourceManager
from data_collector import DataCollector

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
    """
    prompt = 'flymon> '

    def __init__(self, config_file = 'cmu_groups.json'):
        cmd.Cmd.__init__(self)
        try:
            cmug_configs = json.load(open(config_file, 'r'))
            # Z seem no need to pass it to TaskManager
            self.task_manager = TaskManager(cmug_configs)
            self.resource_manager = ResourceManager(cmug_configs)
            self.data_collector = DataCollector(cmug_configs)
            self.cnt = 0
        except Exception as e:
            print(f"{e} when loading configure file.")
            exit(1)

    # cmd 1: add port.
    def do_show_status(self, arg):
        """
        Show the status of a CMU-Group.
        Args list:
            "-g", "--cmu_group" type=int, required=True, show wich CMU-Group?
        """
        parser = FlyMonArgumentParser()
        parser.add_argument("-g", "--cmu_group", dest="group_id", type=int, required=True, help="Show which cmu-group?")
        args = parser.parse_args(arg.split())
        self.cnt += 1
        if parser.error_message:
            print(parser.error_message)
            return
        # Normal Logic
        self.resource_manager.show_status(args.group_id)

    def do_add_task(self, arg):
        """
        Add a task to CMU-Group.
        Args list:
            "-k", "--key" required=True, e.g., hdr.ipv4.src_addr/24
            "-a", "--attribute" type=[frequency, distinct, max, existence], required=True,
            "-m", "--mem_size" type=int, required=True
            "-n", "--mem_num" type=int, required=False, default=1
        Return:
            Added task id or -1.
        """
        parser = FlyMonArgumentParser()
        parser.add_argument("-k", "--key", dest="key", type=str, required=True, help="e.g., hdr.ipv4.src_addr/24")
        parser.add_argument("-a", "--attribute", dest="attribute", type=str, required=True, help="e.g., frequency(1)")
        parser.add_argument("-m", "--mem_size", dest="mem_size", type=int, required=True, help="32768")
        args = parser.parse_args(arg.split())
        task_instance = self.task_manager.register_task(args.key, args.attribute, args.mem_size)
        # 分配到哪些 (CMU_GROUP, CMU_ID)
        locations = self.resource_manager.allocate_resources(task_instance.resource_list())
        # 根据locations 下发规则
        task_instance.install(locations)
        # self.data_collector.xxxx(querier)
        if parser.error_message:
            print(parser.error_message)
            return
        # Normal Logic
        # task_manager.

    def do_read_data(self):
        # read data
        pass

    def do_del_task(self, arg):
        """
        Delete a task.
        Args list:
            "-t", "--task" type=int, required=True
        Return:
            Deleted task id or -1.
        """
        pass

    def do_add_port(self):
        pass
    

    def complete_read_data(self):
        pass

    def do_query_task(self):
        pass
    def complete_query_task(self):
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

if __name__ == "__main__":
    # setup()
    FlyMonController().cmdloop()

# class TMUController(BfRuntimeTest):
#     def setUp(self):
#         self.client_id = 0
#         self.p4_name = "tmus"
#         BfRuntimeTest.setUp(self, self.client_id, self.p4_name)

#     def runTest(self):
#         ## Setup port
#         self.bfrt_info = self.interface.bfrt_info_get(self.p4_name)
#         self.target = client.Target(device_id=0, pipe_id=0xffff)
#         js_file = open("../tmu_config.json", 'r')
#         configs = json.load(js_file)

#         self.TMU_CONFIGS = configs["tmu_configs"]
#         self.RU_CONFIGS = configs["ru_configs"]
#         self.CU_TARGET_BITS = configs["cu_target_bits"]
#         self.MEM_SIZE = configs["mem_size"]

#         self.config_bloomfilter() ## Setup BloomFilter to filter the dup heavy keys.

#         tmu0 = TMU(self.target, self.bfrt_info, self.TMU_CONFIGS[0], self.CU_TARGET_BITS, self.MEM_SIZE)
#         # task = tmu_task_examples.get_task_cmsketch_five_tuple()
#         task = tmu_task_examples.get_task_cmsketch_ip_pair(threshold=1024) # If the packet count larger than 1024, collect its fullkey.
#         time_begin = time.time()
#         tmu0.register_task(task) # Deploy a 5-tuple heavy key task in the data plane.
#         time_end = time.time()
#         print("task_deploy time: %s ms", ((time_end - time_begin)*1000))
#         try:
#             while True:
#                 logger.info("Continue listening the heavykey from data plane..")
#                 # tmu0.read_task_data(task_five_tuple_counting)
#                 # The learn object can be retrieved using a lesser qualified name on the condition
#                 # that it is unique
#                 learn_filter = self.bfrt_info.learn_get("digest")
#                 learn_filter.info.data_field_annotation_add("a", "ipv4")
#                 learn_filter.info.data_field_annotation_add("b", "ipv4")
#                 try:
#                     digest = self.interface.digest_get(timeout=5)
#                     data_list = learn_filter.make_data_list(digest)
#                     data_dict = data_list[0].to_dict()
#                     print(data_dict)
#                 except:
#                     tmu0.read_task_data(task)
#                     pass

#         except KeyboardInterrupt:
#                 print("Terminated mannually.")
#         except Exception as e:
#                 traceback.print_exc()
#             pass
    
#     def config_bloomfilter(self):
#         # temporarily removed.
#         pass