import bin.tester
import time
import functools
from multiprocessing import  Process

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

def test_univmon_heavyhitter():
    test_dir = TEST_DIR_BASE + 'UnivMon/'
    test_file = 'test_univmon.cpp_template'
    test_args = {
        "WORK_DIR" : '/home/hzheng/workSpace/SketchLab',
        "DATA_FILE" : 'data/WIDE/thirty_sec_0.dat',
        # "DATA_FILE" : 'data/WIDE/one_sec_15.dat',
        "TOT_MEM_IN_BUCKETS" : 0,
        "TOTAL_MEMORY_KB" : 0,
        "UNIV_DEP" : 0,
        "RESULT_CSV" : ""
    }
    out_file = 'logs/test_univmon_flow_heavyhitter_'+logtime()+'.log'
    test_args['RESULT_CSV'] = 'outputs_30/heavyhitters_new/' + 'heavyhitter_univmon_30s.csv'
    # M_LIST = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
    MEMORY = [200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]
    D_LIST = [ 14,  14,  14,  14,  14,  14,  14,  14,  14,  14,  14,  14,  14,  14,  14,  14,   14]
    for i in range(len(MEMORY)):
        test_args['TOTAL_MEMORY_KB'] = MEMORY[i]
        test_args['UNIV_DEP'] = D_LIST[i]
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(15):
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")

def test_beaucoup_heavyhitter():
    test_dir = TEST_DIR_BASE + 'BEAUCOUP/'
    test_file = 'test_beaucoup_heavyhitter.cpp_template'
    test_args = {
        "WORK_DIR" : '/home/hzheng/workSpace/SketchLab',
        "DATA_FILE" : 'data/WIDE/thirty_sec_0.dat',
        # "DATA_FILE" : 'data/WIDE/one_sec_15.dat',
        "MEMORY_KB" : 0,  #TBD
        "THRESHOLD" : 0,
        "TABLE_NUM" : 3,
        "RESULT_CSV" : ""    ## TBD
    }
    out_file = 'logs/test_beaucoup_heavyhitter_'+logtime()+'.log'
    test_args['RESULT_CSV'] = 'outputs_30/heavyhitters_new/' + 'heavyhitter_beaucoup_3d.csv'
    test_args['THRESHOLD'] = 1024
    # M_LIST = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
    # M_LIST = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    M_LIST = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]
    for i in range(len(M_LIST)):
        test_args['MEMORY_KB'] = M_LIST[i]
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes("test_beaucoup")
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(15):  
            p = Process(target=_bound_instance_method_alias,args=(i,"test_beaucoup")) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")

def test_tbc_cmsketch_heavy_hitter():
    test_dir = TEST_DIR_BASE + 'TBC_CMSketch/'
    test_file = 'test_tbc_cmsketch.cpp_template'
    test_args = {
        "WORK_DIR" : '/home/hzheng/workSpace/SketchLab',
        "DATA_FILE" : 'data/WIDE/thirty_sec_0.dat',
        "TBC_NUM" : 1,
        "BLOCK_NUM" : 3,
        "SUB_BLOCK_NUM" : 16,
        "MEMORY" : 0 , # TBD
        "RESULT_CSV_FLOW_SIZE" :  'outputs_30/' + 'tbc_cmsketch_flowsize_ignore.csv',
        "RESULT_CSV_HEAVY_HITTER": 'outputs_30/heavyhitters_new/' + 'heavyhitter_tmu_cmsketch.csv' 
    }
    out_file = 'logs/test_tbc_cketch_'+logtime()+'.log'
    M_LIST = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]
    # M_LIST = [1500]
    for i in range(len(M_LIST)):
        test_args['MEMORY'] = M_LIST[i] * 1024
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(15):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")

def test_tbc_cusketch_heavy_hitter():
    test_dir = TEST_DIR_BASE + 'TBC_CUSketch/'
    test_file = 'test_tbc_cusketch.cpp_template'
    test_args = {
        "WORK_DIR" : '/home/hzheng/workSpace/SketchLab',
        "DATA_FILE" : 'data/WIDE/thirty_sec_0.dat',
        "TBC_NUM" : 1,
        "BLOCK_NUM" : 3,
        "SUB_BLOCK_NUM" : 16,
        "MEMORY" : 0 , # TBD
        # "RESULT_CSV_FLOW_SIZE" :  'outputs/' + 'tbc_cusketch_flowsize.csv',
        # "RESULT_CSV_HEAVY_HITTER": 'outputs/' + 'tbc_cusketch_heavyhitter.csv' 
        "RESULT_CSV_FLOW_SIZE" :  'outputs_30/' + 'test_tbc_acusketch_flowsize_ignore.csv',
        "RESULT_CSV_HEAVY_HITTER": 'outputs_30/heavyhitters_new/' + 'heavyhitter_tmu_sumax.csv' 
    }
    # out_file = 'logs/test_tbc_cuketch_'+logtime()+'.log'
    out_file = 'logs/original_cuketch_'+logtime()+'.log'
    M_LIST = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]
    for i in range(len(M_LIST)):
        test_args['MEMORY'] = M_LIST[i] * 1024
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

def test_tbc_beaucoup_heavy_hitter():
    test_dir = TEST_DIR_BASE + 'TBC_BEAUCOUP_HH/'
    test_file = 'test_tbc_beaucoup_hh.cpp_template'
    test_args = {
        "WORK_DIR" : '/home/hzheng/workSpace/SketchLab',
        "DATA_FILE" : 'data/WIDE/thirty_sec_0.dat',
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "BLOCK_NUM" : 3,
        "MEMORY_BYTES" : 0 , # TBD
        "RESULT_CSV": 'outputs_30/heavyhitters_new/' + 'heavyhitter_tmu_beaucoup_3d.csv' 
    }
    # out_file = 'logs/test_tbc_cuketch_'+logtime()+'.log'
    out_file = 'logs/original_tmu_beaucoup_'+logtime()+'.log'
    M_LIST = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]
    # M_LIST = [1000]
    for i in range(len(M_LIST)):
        test_args['MEMORY_BYTES'] = M_LIST[i] * 1024
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(15):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")

if __name__ == '__main__':
    # test_tbc_beaucoup_heavy_hitter()
    # test_univmon_heavyhitter()
    # test_beaucoup_heavyhitter()
    test_tbc_cmsketch_heavy_hitter()
    test_tbc_cusketch_heavy_hitter()
    
