from argparse import ArgumentParser
import bin.tester
import time
import functools
from multiprocessing import  Process



parser = ArgumentParser()
parser.add_argument("-d", "--dir", dest="work_dir", type=str, required=True, help="Directory of simulation codes.")
args = parser.parse_args()
work_dir = args.work_dir
data = work_dir  +'/data/WIDE/fifteen1.dat'
log_dir = work_dir + '/log/'
test_dir_base = work_dir + 'test/'
result_dir = work_dir + 'results/'
result_dir_heavyhitter = result_dir + "heavyhitter"

HEAVY_HITTER_MEMORY = [200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]

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
    test_dir = test_dir_base + 'UnivMon/'
    test_file = 'test_univmon.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data,
        # "DATA_FILE" : 'data/WIDE/one_sec_15.dat',
        "TOT_MEM_IN_BUCKETS" : 0,
        "TOTAL_MEMORY_KB" : 0,
        "UNIV_DEP" : 0,
        "RESULT_CSV" : ""
    }
    out_file = log_dir + 'test_univmon_flow_heavyhitter_'+logtime()+'.log'
    test_args['RESULT_CSV'] = result_dir_heavyhitter + 'univmon.csv'
    D_LIST = [ 14,  14,  14,  14,  14,  14,  14,  14,   14,   14,   14,   14,   14,   14,   14,   14,   14,    14]
    for i in range(len(HEAVY_HITTER_MEMORY)):
        test_args['TOTAL_MEMORY_KB'] = HEAVY_HITTER_MEMORY[i]
        test_args['UNIV_DEP'] = D_LIST[i]
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(15):
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
        "DATA_FILE" : work_dir+'/data/WIDE/fifteen1.dat',
        # "DATA_FILE" : 'data/WIDE/one_sec_15.dat',
        "MEMORY_KB" : 0,  #TBD
        "THRESHOLD" : 0,
        "TABLE_NUM" : table_num,
        "RESULT_CSV" : ""    ## TBD
    }
    out_file = log_dir + 'test_beaucoup_heavyhitter_'+logtime()+'.log'
    test_args['RESULT_CSV'] = result_dir_heavyhitter + 'beaucoup_%dd.csv' %(table_num)
    test_args['THRESHOLD'] = 1024
    for i in range(len(HEAVY_HITTER_MEMORY)):
        test_args['MEMORY_KB'] = HEAVY_HITTER_MEMORY[i]
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
    test_dir = test_dir_base + 'TBC_CMSketch/'
    test_file = 'test_tbc_cmsketch.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : work_dir+'/data/WIDE/fifteen1.dat',
        "TBC_NUM" : 1,
        "BLOCK_NUM" : 3,
        "SUB_BLOCK_NUM" : 16,
        "MEMORY" : 0 , # TBD
        "RESULT_CSV_HEAVY_HITTER": result_dir_heavyhitter + 'flymon_cmsketch.csv' 
    }
    out_file = log_dir + 'test_tbc_cketch_'+logtime()+'.log'
    for i in range(len(HEAVY_HITTER_MEMORY)):
        test_args['MEMORY'] = HEAVY_HITTER_MEMORY[i] * 1024 # it use Bytes in the code.
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
    test_dir = test_dir_base + 'TBC_CUSketch/'
    test_file = 'test_tbc_cusketch.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data,
        "TBC_NUM" : 1,
        "BLOCK_NUM" : 3,
        "SUB_BLOCK_NUM" : 16,
        "MEMORY" : 0 , # TBD
        # "RESULT_CSV_FLOW_SIZE" :  'outputs/' + 'tbc_cusketch_flowsize.csv',
        # "RESULT_CSV_HEAVY_HITTER": 'outputs/' + 'tbc_cusketch_heavyhitter.csv' 
        # "RESULT_CSV_FLOW_SIZE" :  result_dir + 'test_tbc_acusketch_flowsize_ignore.csv',
        "RESULT_CSV_HEAVY_HITTER": result_dir_heavyhitter + 'flymon_sumax.csv' 
    }
    # out_file = 'logs/test_tbc_cuketch_'+logtime()+'.log'
    out_file = log_dir + 'original_cuketch_'+logtime()+'.log'
    for i in range(len(HEAVY_HITTER_MEMORY)):
        test_args['MEMORY'] = HEAVY_HITTER_MEMORY[i] * 1024 # it use Bytes in the code.
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

def test_tbc_beaucoup_heavy_hitter():
    test_dir = test_dir_base + 'TBC_BEAUCOUP_HH/'
    test_file = 'test_tbc_beaucoup_hh.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : data,
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "BLOCK_NUM" : 3,
        "MEMORY_BYTES" : 0 , # TBD
        "RESULT_CSV": result_dir_heavyhitter + 'flymon_beaucoup_3d.csv' 
    }
    # out_file = 'logs/test_tbc_cuketch_'+logtime()+'.log'
    out_file = 'logs/original_tmu_beaucoup_'+logtime()+'.log'
    # M_LIST = [1000]
    for i in range(len(HEAVY_HITTER_MEMORY)):
        test_args['MEMORY_BYTES'] = HEAVY_HITTER_MEMORY[i] * 1024  # it use Bytes in the code.
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


def test_tmu_hll_ddos_victim(m=8, offset=3):
    test_dir = test_dir_base + 'TEST_TBC_DDOS_VICTIM/'
    test_file = 'test_tbc_ddos_victim.cpp_template'
    test_ddos_visctim_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : 'data/WIDE/thirty_sec_0.dat',
        # "DATA_FILE" : 'data/WIDE/one_sec_15.dat',
        "RESULT_CSV" : '', ##TBD
        "TBC_NUM" : 1,
        "BLOCK_NUM" : 5,
        "SUB_BLOCK_NUM" : 16,
        "HLL_BLOCK_NUM" : 1,
        "HLL_MEMORY" : 0,     ## TBD
        "HLL_BLOCK_SIZE" : 0, ## TBD
        "HLL_SUB_BLOCK_NUM" : 8,
        "ADDRESS_MOVE" : 3,
        "HLL_COIN_LEVEL" : 0,
        "HLL_COFF" : 1,
        "DDOS_THRESHOLD" : 256,
        "ITEM_SELECT" : 0
    }
    out_file_3 = 'logs/test_ddos_victim_new_3RowHll_'+logtime()+'.log'
    M_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    for mem in M_LIST:
        print("Running %d KB..." %(mem,))
        test_ddos_visctim_args['HLL_MEMORY'] = mem
        test_ddos_visctim_args['HLL_BLOCK_NUM'] = 3
        test_ddos_visctim_args['HLL_BLOCK_SIZE'] = (mem * 1024) / 2 / test_ddos_visctim_args['HLL_BLOCK_NUM']
        test_ddos_visctim_args['HLL_SUB_BLOCK_NUM'] = m
        test_ddos_visctim_args['ADDRESS_MOVE'] = offset
        test_ddos_visctim_args['ITEM_SELECT'] = 0
        test_ddos_visctim_args['DDOS_THRESHOLD'] = 128
        test_ddos_visctim_args['RESULT_CSV'] = 'outputs_30/ddosvictims_new/' + 'ddosvictim_tmu_hll_3d_%dm.csv' % (m)
        test_once = bin.tester.Tester(test_dir, test_file, test_ddos_visctim_args, out_file_3)
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

       
def test_beaucoup_ddos_victim(table_num=1):
    test_dir = test_dir_base + 'BEAUCOUP/'
    test_file = 'test_beaucoup_ddos.cpp_template'
    test_args = {
        "WORK_DIR" : work_dir,
        "DATA_FILE" : 'data/WIDE/sixty_sec_0.dat',
        "MEMORY_KB" : 0,  #TBD
        "THRESHOLD" : 0,
        "RESULT_CSV" : ""    ## TBD
    }
    out_file = 'logs/test_beaucoup_ddosvictim_'+logtime()+'.log'
    test_args['RESULT_CSV'] = 'outputs_30/ddosvictims_new/' + 'ddosvictim_beaucoup_%dd.csv' % (table_num)
    test_args['TABLE_NUM'] = table_num
    # M_LIST = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
    M_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    for i in range(len(M_LIST)):
        test_args['MEMORY_KB'] = M_LIST[i]
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes("test_beaucoup")
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(10):  
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
        "DATA_FILE" : 'data/WIDE/sixty_sec_0.dat',
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "BLOCK_NUM" : d,
        "MEMORY_BYTES" : 0 , # TBD
        "RESULT_CSV": 'outputs_30/ddosvictims_new/' + 'ddosvictim_tmu_beaucoup_%dd.csv'%(d) 
    }
    # out_file = 'logs/test_tbc_cuketch_'+logtime()+'.log'
    out_file = 'logs/original_tmu_beaucoup_'+logtime()+'.log'
    M_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    # M_LIST = [1000]
    for i in range(len(M_LIST)):
        test_args['MEMORY_BYTES'] = M_LIST[i] * 1024
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(10):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(3)
        for p in process_list:
            p.join()
    print("Done.")

if __name__ == '__main__':
    ## Heavy Hitters
    test_univmon_heavyhitter()
    test_tbc_beaucoup_heavy_hitter()
    test_beaucoup_heavyhitter(table_num=1)
    test_tbc_cmsketch_heavy_hitter()
    test_tbc_cusketch_heavy_hitter()

    ## DDoS Victims
    test_tbc_beaucoup_ddos_victim(d=1)
    test_tbc_beaucoup_ddos_victim(d=3)
    test_beaucoup_ddos_victim(table_num=1)
    test_beaucoup_ddos_victim(table_num=3)
    test_tmu_hll_ddos_victim(m=8, offset=3)
    test_tmu_hll_ddos_victim(m=16, offset=4)
    test_tmu_hll_ddos_victim(m=64, offset=5)
    
