from argparse import ArgumentParser
import bin.tester
import time
import functools
from multiprocessing import  Process
import datetime
import os
import shutil  
import math
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dir", dest="work_dir", type=str, required=True, help="Directory of simulation codes.")
parser.add_argument("-r", "--repeat", dest="repeat", type=int, required=True, help="How many times to repeat each experiment.")
parser.add_argument("-m", "--mode", dest="mode", type=str, required=True, default="sample", help="e.g., Mode of testing? sample or all.")

args = parser.parse_args()
work_dir = args.work_dir
repeat_time = args.repeat


mode = args.mode
if mode not in ["sample", "all"]:
    print("Mode needs in [sample, all]")
    exit(1)

HEAVY_HITTER_MEMORY1 = None
HEAVY_HITTER_MEMORY2 = None
DDOS_VICTOM_MEMORY = None
BLOOM_MEMORY = None
CARD_MEMORY = None
ENTROPY_MEMORY = None
MAX_MEMORY = None

if mode == "all":
## Full Memory Settings (In KB or Bytes).
    HEAVY_HITTER_MEMORY1 = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
    HEAVY_HITTER_MEMORY2 = [200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
    DDOS_VICTOM_MEMORY = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    BLOOM_MEMORY = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 1000]
    CARD_MEMORY = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 8192]  
    ENTROPY_MEMORY = [200, 300, 400, 500]
    MAX_MEMORY = [10000, 5000, 4000, 3000, 2000, 1000, 900, 800, 700, 600, 500, 400, 300, 200, 100]
else:
## Sample Memory Settings for Debug or Test
    HEAVY_HITTER_MEMORY1 = [10, 50, 100, 200]
    HEAVY_HITTER_MEMORY2 = [200, 500, 5000]
    DDOS_VICTOM_MEMORY = [10, 50, 100, 500]
    BLOOM_MEMORY = [10, 50, 100]
    CARD_MEMORY = [4, 128, 1024, 8192]  
    ENTROPY_MEMORY = [200, 500]
    MAX_MEMORY = [10000, 5000, 500]

## Datas
data15 = work_dir  +'/data/fifteen1.dat'
data30 = work_dir  +'/data/thirty_sec_0.dat'
data60 = work_dir  +'/data/sixty_sec_0.dat'

## Our Dirs
log_dir = work_dir + '/log/'
test_dir_base = work_dir + 'test/'
result_dir = work_dir + 'result/'
result_dir_heavyhitter = result_dir + "heavyhitter/"
result_dir_heavyhitter_prob = result_dir + "heavyhitter_prob/"
result_dir_ddos = result_dir + "ddos/"
result_dir_card = result_dir + "cardinality/"
result_dir_entropy = result_dir + "entropy/"
result_dir_max =result_dir + "max_interval_time/"
result_dir_bloom = result_dir + "existence/"

if repeat_time <=0 or repeat_time>15:
    print("Invalid repeat times")
    exit(1)

# Clear
os.makedirs(result_dir_heavyhitter, exist_ok=True)
os.makedirs(result_dir_heavyhitter_prob, exist_ok=True)
os.makedirs(result_dir_ddos, exist_ok=True)
os.makedirs(result_dir_bloom, exist_ok=True)
os.makedirs(result_dir_card, exist_ok=True)
os.makedirs(result_dir_entropy, exist_ok=True)
os.makedirs(result_dir_max, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)
# remove old results.
shutil.rmtree(log_dir) 
shutil.rmtree(result_dir_heavyhitter) 
shutil.rmtree(result_dir_heavyhitter_prob) 
shutil.rmtree(result_dir_ddos)  
shutil.rmtree(result_dir_bloom)
shutil.rmtree(result_dir_card)
shutil.rmtree(result_dir_entropy)
shutil.rmtree(result_dir_max)
# create result dir.
os.makedirs(result_dir_heavyhitter, exist_ok=True)
os.makedirs(result_dir_heavyhitter_prob, exist_ok=True)
os.makedirs(result_dir_ddos, exist_ok=True)
os.makedirs(result_dir_bloom, exist_ok=True)
os.makedirs(result_dir_card, exist_ok=True)
os.makedirs(result_dir_entropy, exist_ok=True)
os.makedirs(result_dir_max, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)


def logtime():
    return time.strftime("%m_%d_%H_%M", time.localtime())

def _instance_method_alias(obj, arg1, arg2=None):
    """
    Alias for instance method that allows the method to be called in a 
    multiprocessing pool
    """
    obj.runTest(arg1, arg2)
    return

def test_univmon_heavyhitter():
    test_dir = test_dir_base + 'UnivMon_HH/'
    test_file = 'test_univmon_hh.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data15,
        # "DATA_FILE" : 'data/WIDE/one_sec_15.dat',
        "TOT_MEM_IN_BUCKETS" : 0,
        "TOTAL_MEMORY_KB" : 0,
        "UNIV_DEP" : 0,
        "RESULT_CSV" : ""
    }
    out_file = log_dir + 'test_univmon_flow_heavyhitter_'+logtime()+'.log'
    test_args['RESULT_CSV'] = result_dir_heavyhitter + 'univmon.csv'
    D_LIST = [ 14,  14,  14,  14,  14,  14,  14,  14,   14,   14,   14,   14,   14,   14,   14,   14,   14,    14]
    for i in range(len(HEAVY_HITTER_MEMORY2)):
        test_args['TOTAL_MEMORY_KB'] = HEAVY_HITTER_MEMORY2[i]
        test_args['UNIV_DEP'] = D_LIST[i]
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(repeat_time):
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(3)
        for p in process_list:
            p.join()
    print("Done.")

def test_beaucoup_heavyhitter(table_num = 1):
    test_dir = test_dir_base + 'BEAUCOUP/'
    test_file = 'test_beaucoup_heavyhitter.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data15,
        # "DATA_FILE" : 'data/WIDE/one_sec_15.dat',
        "MEMORY_KB" : 0,  #TBD
        "THRESHOLD" : 0,
        "TABLE_NUM" : table_num,
        "RESULT_CSV" : ""    ## TBD
    }
    out_file = log_dir + 'test_beaucoup_heavyhitter_'+logtime()+'.log'
    test_args['RESULT_CSV'] = result_dir_heavyhitter + f'beaucoup_{table_num}d.csv'
    test_args['THRESHOLD'] = 1024
    for i in range(len(HEAVY_HITTER_MEMORY1)):
        test_args['MEMORY_KB'] = HEAVY_HITTER_MEMORY1[i]
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes("test_beaucoup")
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(repeat_time):  
            p = Process(target=_bound_instance_method_alias,args=(i,"test_beaucoup")) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")

def test_tbc_cmsketch_heavy_hitter():
    test_dir = test_dir_base + 'TBC_CMSketch/'
    test_file = 'test_tbc_cmsketch.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data15,
        "TBC_NUM" : 1,
        "BLOCK_NUM" : 3,
        "SUB_BLOCK_NUM" : 16,
        "MEMORY" : 0 , # TBD
        "RESULT_CSV_HEAVY_HITTER": result_dir_heavyhitter + 'flymon_cmsketch3d.csv' 
    }
    out_file = log_dir + 'test_tbc_cketch_'+logtime()+'.log'
    for i in range(len(HEAVY_HITTER_MEMORY1)):
        test_args['MEMORY'] = HEAVY_HITTER_MEMORY1[i] * 1024 # it use Bytes in the code.
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(repeat_time):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")

def test_tbc_cusketch_heavy_hitter():
    test_dir = test_dir_base + 'TBC_CUSketch/'
    test_file = 'test_tbc_cusketch.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data15,
        "TBC_NUM" : 1,
        "BLOCK_NUM" : 3,
        "SUB_BLOCK_NUM" : 16,
        "MEMORY" : 0 , # TBD
        # "RESULT_CSV_FLOW_SIZE" :  'outputs/' + 'tbc_cusketch_flowsize.csv',
        # "RESULT_CSV_HEAVY_HITTER": 'outputs/' + 'tbc_cusketch_heavyhitter.csv' 
        # "RESULT_CSV_FLOW_SIZE" :  result_dir + 'test_tbc_acusketch_flowsize_ignore.csv',
        "RESULT_CSV_HEAVY_HITTER": result_dir_heavyhitter + 'flymon_sumax3d.csv' 
    }
    # out_file = log_dir + 'test_tbc_cuketch_'+logtime()+'.log'
    out_file = log_dir + 'original_cuketch_'+logtime()+'.log'
    for i in range(len(HEAVY_HITTER_MEMORY1)):
        test_args['MEMORY'] = HEAVY_HITTER_MEMORY1[i] * 1024 # it use Bytes in the code.
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(repeat_time):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")

def test_tbc_beaucoup_heavy_hitter(block_num):
    test_dir = test_dir_base + 'TBC_BEAUCOUP_HH/'
    test_file = 'test_tbc_beaucoup_hh.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data15,
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "BLOCK_NUM" : block_num,
        "MEMORY_BYTES" : 0 , # TBD
        "RESULT_CSV": result_dir_heavyhitter + f'flymon_beaucoup_{block_num}d.csv'
    }
    # out_file = log_dir + 'test_tbc_cuketch_'+logtime()+'.log'
    out_file = log_dir + 'original_tmu_beaucoup_'+logtime()+'.log'
    # M_LIST = [1000]
    for i in range(len(HEAVY_HITTER_MEMORY1)):
        test_args['MEMORY_BYTES'] = HEAVY_HITTER_MEMORY1[i] * 1024  # it use Bytes in the code.
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(repeat_time):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")


# def test_tmu_hll_ddos_victim(m=8, offset=3):
#     test_dir = test_dir_base + 'TEST_TBC_DDOS_VICTIM/'
#     test_file = 'test_tbc_ddos_victim.cpp_template'
#     test_ddos_visctim_args = {
#         "WORK_DIR" : work_dir,
#         "DATA_FILE" : 'data/WIDE/thirty_sec_0.dat',
#         # "DATA_FILE" : 'data/WIDE/one_sec_15.dat',
#         "RESULT_CSV" : '', ##TBD
#         "TBC_NUM" : 1,
#         "BLOCK_NUM" : 5,
#         "SUB_BLOCK_NUM" : 16,
#         "HLL_BLOCK_NUM" : 1,
#         "HLL_MEMORY" : 0,     ## TBD
#         "HLL_BLOCK_SIZE" : 0, ## TBD
#         "HLL_SUB_BLOCK_NUM" : 8,
#         "ADDRESS_MOVE" : 3,
#         "HLL_COIN_LEVEL" : 0,
#         "HLL_COFF" : 1,
#         "DDOS_THRESHOLD" : 256,
#         "ITEM_SELECT" : 0
#     }
#     out_file_3 = log_dir + 'test_ddos_victim_new_3RowHll_'+logtime()+'.log'
    
#     for mem in DDOS_VICTOM_MEMORY:
#         print("Running %d KB..." %(mem,))
#         test_ddos_visctim_args['HLL_MEMORY'] = mem
#         test_ddos_visctim_args['HLL_BLOCK_NUM'] = 3
#         test_ddos_visctim_args['HLL_BLOCK_SIZE'] = (mem * 1024) / 2 / test_ddos_visctim_args['HLL_BLOCK_NUM']
#         test_ddos_visctim_args['HLL_SUB_BLOCK_NUM'] = m
#         test_ddos_visctim_args['ADDRESS_MOVE'] = offset
#         test_ddos_visctim_args['ITEM_SELECT'] = 0
#         test_ddos_visctim_args['DDOS_THRESHOLD'] = 128
#         test_ddos_visctim_args['RESULT_CSV'] = 'outputs_30/ddosvictims_new/' + 'ddosvictim_tmu_hll_3d_%dm.csv' % (m)
#         test_once = bin.tester.Tester(test_dir, test_file, test_ddos_visctim_args, out_file_3)
#         test_once.generate_codes()
#         _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
#         process_list = []
#         for i in range(15):  
#             p = Process(target=_bound_instance_method_alias,args=(i,)) 
#             p.start()
#             process_list.append(p)
#             time.sleep(5)
#         for p in process_list:
#             p.join()
       
def test_beaucoup_ddos_victim(table_num=1):
    test_dir = test_dir_base + 'BEAUCOUP/'
    test_file = 'test_beaucoup_ddos.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data60,
        "MEMORY_KB" : 0,  #TBD
        "THRESHOLD" : 0,
        "RESULT_CSV" : ""    ## TBD
    }
    out_file = log_dir + 'test_beaucoup_ddosvictim_'+logtime()+'.log'
    test_args['RESULT_CSV'] = result_dir_ddos + f'beaucoup_d{table_num}.csv'
    test_args['TABLE_NUM'] = table_num
    for i in range(len(DDOS_VICTOM_MEMORY)):
        test_args['MEMORY_KB'] = DDOS_VICTOM_MEMORY[i]
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes("test_beaucoup")
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(repeat_time):  
            p = Process(target=_bound_instance_method_alias,args=(i,"test_beaucoup")) 
            p.start()
            process_list.append(p)
            time.sleep(3)
        for p in process_list:
            p.join()
    print("Done.")

def test_tbc_beaucoup_ddos_victim(d = 3):
    test_dir = test_dir_base + 'TBC_BEAUCOUP_DDOS/'
    test_file = 'test_tbc_beaucoup_ddos.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data60,
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "BLOCK_NUM" : d,
        "MEMORY_BYTES" : 0 , # TBD
        "RESULT_CSV": result_dir_ddos + f'flymon_beaucoup_{d}d.csv'
    }
    # out_file = log_dir + 'test_tbc_cuketch_'+logtime()+'.log'
    out_file = log_dir + 'original_tmu_beaucoup_'+logtime()+'.log'
    for i in range(len(DDOS_VICTOM_MEMORY)):
        test_args['MEMORY_BYTES'] = DDOS_VICTOM_MEMORY[i] * 1024 # in bytes
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(repeat_time):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(3)
        for p in process_list:
            p.join()
    print("Done.")

def test_tbc_bloom_filter():
    test_dir = test_dir_base + 'TBC_BLOOMFILTER/'
    test_file = 'test_tbc_bloomfilter.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data15,
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "MEMORY_BYTES" : 0, # TBD
        "TBC_NUM" : 1,
        "BLOOM_K" : 3,
        "RESULT_CSV" : result_dir_bloom + 'bloom_with_optmi.csv'
    }
    out_file = log_dir + 'test_tbc_bloom_w_'+logtime()+'.log'

    for i in range(len(BLOOM_MEMORY)):
        test_args['MEMORY_BYTES'] = BLOOM_MEMORY[i]  * 1024
        # test_args['BLOOM_K'] = (test_args['MEMORY_BYTES'] / 2) / 20000 * 0.693
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(repeat_time):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")

def test_tbc_bloom_filter_wo_optm():
    test_dir = test_dir_base + 'TBC_BLOOMFILTER_WO_OPTM/'
    test_file = 'test_tbc_bloomfilter_wo_optm.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data15,
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "MEMORY_BYTES" : 0, # TBD
        "TBC_NUM" : 1,
        "BLOOM_K" : 3,
        "RESULT_CSV" :  result_dir_bloom + 'bloom_without_optmi.csv'
    }
    out_file = log_dir + 'test_tbc_bloom_wo_'+logtime()+'.log'

    for i in range(len(BLOOM_MEMORY)):
        test_args['MEMORY_BYTES'] = BLOOM_MEMORY[i]  * 1024
        # test_args['BLOOM_K'] = (test_args['MEMORY_BYTES'] / 2) / 20000 * 0.693
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(repeat_time):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")


def test_tbc_hll_flow_cardinality():
    test_dir = test_dir_base + 'TBC_CARDINALITY/'
    test_file = 'test_tbc_cardinality.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data15,
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "TBC_NUM" : 1,
        "BLOCK_NUM" : 5,
        "SUB_BLOCK_NUM" : 1,
        "MEMORY" : 0, # TBD
        "RESULT_CSV" : '', #TBD
        "THREASHOLD" : 20000, 
    }
    out_file = log_dir + 'test_flow_cardinality_hll_'+logtime()+'.log'

    for m in CARD_MEMORY:
        test_args['MEMORY'] = m
        test_args['RESULT_CSV'] = result_dir_card + 'hyperloglog.csv'
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(repeat_time):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")

def test_beaucoup_flow_cardinality():
    test_dir = test_dir_base + 'BEAUCOUP/'
    test_file = 'test_beaucoup_cardinality.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        # "DATA_FILE" : 'data/WIDE/thirty_sec_0.dat',
        "DATA_FILE" : data15,
        "MEMORY_KB" : 100,  #TBD
        "COUPON_NUM_MAX" : 32,
        "COUPON_NUM" : 0, #TBD
        "P_RATIO" : 0,
        "THRESHOLD" : 0,
        "RESULT_CSV" : ""    ## TBD
    }
    # COUPON_MAX_LIST = [32,    64,    96,     128,     256,     512,     1024]
    # COUPON_NUM_LIST = [30,    64,    96,     117,     232,     462,     923]
    # COUPON_P_LIST =   [8192,  4096,  4096,   8192,    8192,    8192,    8192]
    COUPON_MAX_LIST = [32,    64,    96,     128,    256]
    COUPON_NUM_LIST = [32,    64,    96,     127,    254]
    COUPON_P_LIST =   [4096,  4096,  4096,   4096,  4096]
    out_file = log_dir + 'test_beaucoup_ddosvictim_'+logtime()+'.log'
    test_args['RESULT_CSV'] = result_dir_card + 'beaucoup.csv'
    for i in range(len(COUPON_MAX_LIST)):
        test_args['COUPON_NUM_MAX'] = COUPON_MAX_LIST[i]
        test_args['COUPON_NUM'] = COUPON_NUM_LIST[i]
        test_args['P_RATIO'] = int(math.log(COUPON_P_LIST[i], 2))
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes("test_beaucoup")
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(repeat_time):  
            p = Process(target=_bound_instance_method_alias,args=(i,"test_beaucoup")) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")


def test_tbc_flow_entropy():
    test_dir = test_dir_base + 'TBC_MRAC/'
    test_file = 'test_tbc_mrac.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data15,
        # "DATA_FILE" : 'data/head1000.dat',
        "MEMORY" : 0, # TBD
        "RESULT_CSV" :  result_dir_entropy + 'flymon_mrac.csv'
    }
    out_file = log_dir + 'test_tbc_mrac_'+logtime()+'.log'
    for i in range(len(ENTROPY_MEMORY)):
        test_args['MEMORY'] = ENTROPY_MEMORY[i] # * 1024 in the templates
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(repeat_time):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")

def test_univmon_entropy():
    test_dir = test_dir_base + 'UnivMon_Entropy/'
    test_file = 'test_univmon_entropy.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data15,
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "TOTAL_MEMORY" : 0, # TBD
        "UNIV_DEP" : 0,
        "RESULT_CSV" :  result_dir_entropy + 'univmon.csv'
    }
    out_file =  log_dir + 'test_tbc_maxtable_'+logtime()+'.log'
    D_LIST = [ 14,  14,  14,  14,  14,  14,  14,  14,   14]
    # M_LIST = [100]
    for i in range(len(ENTROPY_MEMORY)):
        test_args['TOTAL_MEMORY_KB'] = ENTROPY_MEMORY[i]
        test_args['UNIV_DEP'] = D_LIST[i]
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(repeat_time):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")


def test_tbc_maxtable_max_interval(depth=3):
    test_dir = test_dir_base + 'TBC_MAX_TABLE/'
    test_file = 'test_tbc_max_table.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data15,
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "MEMORY" : 0, # TBD
        "DEPTH" : depth,
        "RESULT_CSV" :  result_dir_max + f'sumax_d{depth}.csv'
    }
    out_file = log_dir + 'test_tbc_maxtable_'+logtime()+'.log'
    # M_LIST = [10000]
    # M_LIST = [5000, 4000, 3000, 2000, 1000, 900, 800, 700, 600, 500, 400, 300, 200, 100]
    # M_LIST = [100]
    for i in range(len(MAX_MEMORY)):
        test_args['MEMORY'] = MAX_MEMORY[i]  * 1024
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(repeat_time):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")


def test_tbc_heavyhitter_prob():
    test_dir = test_dir_base + 'TBC_CMSketch_Prob/'
    test_file = 'test_tbc_cmsketch_prob.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data15,
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "MEMORY" : 0, # TBD
        "DEPTH" : 3,
        "RESULT_CSV" :  result_dir_heavyhitter_prob + 'cm_sketch_prob.csv'
    }
    out_file = log_dir + 'test_tbc_probhh_'+logtime()+'.log'
    test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
    test_once.generate_codes()
    _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
    p = Process(target=_bound_instance_method_alias,args=(0,)) 
    p.start()
    p.join()
    print("Done.")

if __name__ == '__main__':
 
    # Heavy Hitters
    test_univmon_heavyhitter()
    test_beaucoup_heavyhitter(table_num=1)
    test_tbc_beaucoup_heavy_hitter(block_num=1)
    test_tbc_beaucoup_heavy_hitter(block_num=3)
    test_tbc_cmsketch_heavy_hitter()
    test_tbc_cusketch_heavy_hitter()
    
    # Probabilistic Heavy Hitters
    test_tbc_heavyhitter_prob()

    ## DDoS Victims
    test_tbc_beaucoup_ddos_victim(d=1)
    test_tbc_beaucoup_ddos_victim(d=3)
    test_beaucoup_ddos_victim(table_num=1)
    test_beaucoup_ddos_victim(table_num=3)

    ## Bloomfilter
    test_tbc_bloom_filter_wo_optm()
    test_tbc_bloom_filter()

    # Cardinality
    test_tbc_hll_flow_cardinality()
    test_beaucoup_flow_cardinality()

    # Entropy
    test_univmon_entropy()
    test_tbc_flow_entropy()

    # Max Table
    test_tbc_maxtable_max_interval(depth=2)
    test_tbc_maxtable_max_interval(depth=3)

