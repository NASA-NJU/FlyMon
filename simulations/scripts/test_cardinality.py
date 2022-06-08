import bin.tester
import time
import functools
from multiprocessing import  Process
import math

TEST_DIR_BASE = 'test/'

def logtime():
    return time.strftime("%m_%d_%H_%M", time.localtime())

def _instance_method_alias(obj, arg1, arg2=None):
    """
    Alias for instance method that allows the method to be called in a 
    multiprocessing pool
    """
    obj.runTest(arg1, arg2)
    return

def test_tbc_hll_flow_cardinality():
    test_dir = TEST_DIR_BASE + 'TBC_CARDINALITY/'
    test_file = 'test_tbc_cardinality.cpp_template'
    test_args = {
        "WORK_DIR" : '/home/hzheng/workSpace/SketchLab',
        "DATA_FILE" : 'data/WIDE/fifteen1.dat',
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "TBC_NUM" : 1,
        "BLOCK_NUM" : 5,
        "SUB_BLOCK_NUM" : 1,
        "MEMORY" : 0, # TBD
        "RESULT_CSV" : '', #TBD
        "THREASHOLD" : 20000, 
    }
    out_file = 'logs/test_flow_cardinality_'+logtime()+'.log'
    # MEMORY = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]  ## Bytes
    # MEMORY = [4, 8, 16, 32, 64, 128, 256, 512, 1024]  ## Bytes
    MEMORY = [8192]  ## Bytes
    for m in MEMORY:
        test_args['MEMORY'] = m
        test_args['RESULT_CSV'] = 'outputs_30/' + 'test_tmu_hll_cardinalities.csv'
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(30):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")

def test_beaucoup_flow_cardinality():
    test_dir = TEST_DIR_BASE + 'BEAUCOUP/'
    test_file = 'test_beaucoup_cardinality.cpp_template'
    test_args = {
        "WORK_DIR" : '/home/hzheng/workSpace/SketchLab',
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        # "DATA_FILE" : 'data/WIDE/thirty_sec_0.dat',
        "DATA_FILE" : 'data/WIDE/fifteen1.dat',
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
    out_file = 'logs/test_beaucoup_ddosvictim_'+logtime()+'.log'
    test_args['RESULT_CSV'] = 'outputs/' + 'test_beaucoup_cardinality.csv'
    for i in range(len(COUPON_MAX_LIST)):
        test_args['COUPON_NUM_MAX'] = COUPON_MAX_LIST[i]
        test_args['COUPON_NUM'] = COUPON_NUM_LIST[i]
        test_args['P_RATIO'] = int(math.log(COUPON_P_LIST[i], 2))
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes("test_beaucoup")
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(30):  
            p = Process(target=_bound_instance_method_alias,args=(i,"test_beaucoup")) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")

if __name__ == '__main__':
    test_tbc_hll_flow_cardinality()
    test_beaucoup_flow_cardinality()

    
