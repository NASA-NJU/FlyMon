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

def test_tmu_hll_ddos_victim():
    test_dir = TEST_DIR_BASE + 'TEST_TBC_DDOS_VICTIM/'
    test_file = 'test_tbc_ddos_victim.cpp_template'
    test_ddos_visctim_args = {
        "WORK_DIR" : '/home/hzheng/workSpace/SketchLab',
        "DATA_FILE" : 'data/WIDE/fifteen1.dat',
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
    M_LIST = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]
    for mem in M_LIST:
        print("Running %d KB..." %(mem,))
        test_ddos_visctim_args['HLL_MEMORY'] = mem
        test_ddos_visctim_args['HLL_BLOCK_NUM'] = 3
        test_ddos_visctim_args['HLL_BLOCK_SIZE'] = (mem * 1024) / 2 / test_ddos_visctim_args['HLL_BLOCK_NUM']
        test_ddos_visctim_args['HLL_SUB_BLOCK_NUM'] = 8
        test_ddos_visctim_args['ADDRESS_MOVE'] = 3
        test_ddos_visctim_args['ITEM_SELECT'] = 0
        test_ddos_visctim_args['DDOS_THRESHOLD'] = 128
        test_ddos_visctim_args['RESULT_CSV'] = 'outputs_30/ddosvictims/' + 'ddosvictim_tmu_hll_3d_8m.csv'
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
    test_dir = TEST_DIR_BASE + 'BEAUCOUP/'
    test_file = 'test_beaucoup_ddos.cpp_template'
    test_args = {
        "WORK_DIR" : '/home/hzheng/workSpace/SketchLab',
        "DATA_FILE" : 'data/WIDE/fifteen1.dat',
        "MEMORY_KB" : 0,  #TBD
        "THRESHOLD" : 0,
        "RESULT_CSV" : ""    ## TBD
    }
    out_file = 'logs/test_beaucoup_ddosvictim_'+logtime()+'.log'
    test_args['RESULT_CSV'] = 'outputs_30/ddosvictims/' + 'ddosvictim_beaucoup_%dd.csv' % (table_num)
    test_args['TABLE_NUM'] = table_num
    # M_LIST = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
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

def test_tbc_beaucoup_ddos_victim():
    test_dir = TEST_DIR_BASE + 'TBC_BEAUCOUP_DDOS/'
    test_file = 'test_tbc_beaucoup_ddos.cpp_template'
    test_args = {
        "WORK_DIR" : '/home/hzheng/workSpace/SketchLab',
        "DATA_FILE" : 'data/WIDE/fifteen1.dat',
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "BLOCK_NUM" : 3,
        "MEMORY_BYTES" : 0 , # TBD
        "RESULT_CSV": 'outputs_30/ddosvictims/' + 'ddosvictim_tmu_beaucoup_3d.csv' 
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
    test_tbc_beaucoup_ddos_victim()
    test_beaucoup_ddos_victim(table_num=1)
    test_beaucoup_ddos_victim(table_num=3)
    test_tmu_hll_ddos_victim()
    

    
