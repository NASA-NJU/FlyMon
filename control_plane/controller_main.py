# -*- coding:UTF-8 -*-
import os
import logging
from collections import namedtuple
import bfrt_grpc.client as client
import time
import traceback
import json
import cmd

logger = logging.getLogger('FlyMon')
if not len(logger.handlers):
    logger.addHandler(logging.StreamHandler())


class FlyMonRuntime(cmd.Cmd):
    intro = 'FlyMonRuntime: Interactive control plane utility of FlyMon. \n'
    prompt = 'flymon>'

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.flymon_manager = "This is resource manager"

    # cmd 1: add port.
    def do_add_port(self, port, speed):
        pass
    def complete_add_port(self):
        pass
    
    # cmd 2: add task.
    def do_add_task(self):
        print(self.resource_manager)
        pass
    def complete_add_task(self):
        pass

    # cmd 3: del task.
    def do_del_task(self):
        pass
    def complete_del_task(self):
        pass

    # cmd 4: read data
    def do_read_data(self):
        pass
    def complete_read_data(self):
        pass

    # cmd 5: query task.
    def do_query_task(self):
        pass
    def complete_query_task(self):
        pass

    # Other cmds.
    def do_EOF(self, line):
        print("")
        return True
    
    def do_shell(self, line):
        "Run a shell command"
        print "running shell command:", line
        output = os.popen(line).read()
        print output
        self.last_output = output

if __name__ == "__main__":
    # setup()
    FlyMonRuntime().cmdloop()

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