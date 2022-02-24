import logging
from collections import namedtuple
from bfruntime_client_base_tests import BfRuntimeTest
import ptf.testutils as testutils
import bfrt_grpc.client as client
import time
import traceback
import json 
from tmu_utils import *
import tmu_task_examples 


logger = logging.getLogger('Test')
if not len(logger.handlers):
    logger.addHandler(logging.StreamHandler())

class TMUController(BfRuntimeTest):
    def setUp(self):
        self.client_id = 0
        self.p4_name = "tmus"
        BfRuntimeTest.setUp(self, self.client_id, self.p4_name)

    def runTest(self):
        ## Setup port
        self.bfrt_info = self.interface.bfrt_info_get(self.p4_name)
        self.target = client.Target(device_id=0, pipe_id=0xffff)
        js_file = open("../tmu_config.json", 'r')
        configs = json.load(js_file)

        self.TMU_CONFIGS = configs["tmu_configs"]
        self.RU_CONFIGS = configs["ru_configs"]
        self.CU_TARGET_BITS = configs["cu_target_bits"]
        self.MEM_SIZE = configs["mem_size"]

        self.config_bloomfilter() ## Setup BloomFilter to filter the dup heavy keys.

        tmu0 = TMU(self.target, self.bfrt_info, self.TMU_CONFIGS[0], self.CU_TARGET_BITS, self.MEM_SIZE)
        # task = tmu_task_examples.get_task_cmsketch_five_tuple()
        task = tmu_task_examples.get_task_cmsketch_ip_pair(threshold=1024) # If the packet count larger than 1024, collect its fullkey.
        time_begin = time.time()
        tmu0.register_task(task) # Deploy a 5-tuple heavy key task in the data plane.
        time_end = time.time()
        print("task_deploy time: %s ms", ((time_end - time_begin)*1000))
        try:
            while True:
                logger.info("Continue listening the heavykey from data plane..")
                # tmu0.read_task_data(task_five_tuple_counting)
                # The learn object can be retrieved using a lesser qualified name on the condition
                # that it is unique
                learn_filter = self.bfrt_info.learn_get("digest")
                learn_filter.info.data_field_annotation_add("a", "ipv4")
                learn_filter.info.data_field_annotation_add("b", "ipv4")
                try:
                    digest = self.interface.digest_get(timeout=5)
                    data_list = learn_filter.make_data_list(digest)
                    data_dict = data_list[0].to_dict()
                    print(data_dict)
                except:
                    tmu0.read_task_data(task)
                    pass

        except KeyboardInterrupt:
                print("Terminated mannually.")
        except Exception as e:
                traceback.print_exc()
            pass
    
    def config_bloomfilter(self):
        # temporarily removed.
        pass