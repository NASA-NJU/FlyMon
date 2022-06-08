import bin.tester
import time
import functools
from multiprocessing import  Process

TEST_DIR_BASE = 'test/'

def logtime():
    return time.strftime("%m_%d_%H_%M", time.localtime())

def _instance_method_alias(obj, arg):
    """
    Alias for instance method that allows the method to be called in a 
    multiprocessing pool
    """
    obj.runTest(arg)
    return

def test_tbc_flow_entropy():
    test_dir = TEST_DIR_BASE + 'TBC_MRAC/'
    test_file = 'test_tbc_mrac.cpp_template'
    test_args = {
        "WORK_DIR" : '/home/hzheng/workSpace/SketchLab',
        "DATA_FILE" : 'data/WIDE/fifteen1.dat',
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "MEMORY" : 0, # TBD
        "RESULT_CSV" :  'outputs_30/entropy/' + 'tbc_flow_distribution_entroy.csv'
    }
    out_file = 'logs/test_tbc_mrac_'+logtime()+'.log'
    M_LIST = [600, 700, 800, 900, 1000]
    # M_LIST = [100]
    for i in range(len(M_LIST)):
        test_args['MEMORY'] = M_LIST[i] # * 1024 in the templates
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(10):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")

def test_univmon_entropy():
    test_dir = TEST_DIR_BASE + 'UnivMon/'
    test_file = 'test_univmon.cpp_template'
    test_args = {
        "WORK_DIR" : '/home/hzheng/workSpace/SketchLab',
        "DATA_FILE" : 'data/WIDE/fifteen1.dat',
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "TOTAL_MEMORY" : 0, # TBD
        "UNIV_DEP" : 0,
        "RESULT_CSV" :  'outputs_30/entropy/' + 'tbc_univmon_entropy.csv'
    }
    out_file = 'logs/test_tbc_maxtable_'+logtime()+'.log'
    M_LIST = [600, 700, 800, 900, 1000]
    D_LIST = [ 14,  14,  14,  14,  14,  14,  14,  14,   14]
    # M_LIST = [100]
    for i in range(len(M_LIST)):
        test_args['TOTAL_MEMORY_KB'] = M_LIST[i]
        test_args['UNIV_DEP'] = D_LIST[i]
        test_once = bin.tester.Tester(test_dir, test_file, test_args, out_file)
        test_once.generate_codes()
        _bound_instance_method_alias = functools.partial(_instance_method_alias, test_once)
        process_list = []
        for i in range(10):  
            p = Process(target=_bound_instance_method_alias,args=(i,)) 
            p.start()
            process_list.append(p)
            time.sleep(5)
        for p in process_list:
            p.join()
    print("Done.")

if __name__ == '__main__':
    test_tbc_flow_entropy()
    test_univmon_entropy()
