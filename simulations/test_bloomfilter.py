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

def test_tbc_bloom_filter():
    test_dir = TEST_DIR_BASE + 'TBC_BLOOMFILTER/'
    test_file = 'test_tbc_bloomfilter.cpp_template'
    test_args = {
        "WORK_DIR" : '/home/hzheng/workSpace/SketchLab',
        "DATA_FILE" : 'data/WIDE/fifteen1.dat',
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "MEMORY_BYTES" : 0, # TBD
        "TBC_NUM" : 1,
        "BLOOM_K" : 3,
        "RESULT_CSV" :  'outputs/' + 'tbc_bloom_fp_no_optmi.csv'
    }
    out_file = 'logs/test_tbc_maxtable_'+logtime()+'.log'
    # M_LIST = [15000]
    M_LIST = [1000, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    for i in range(len(M_LIST)):
        test_args['MEMORY_BYTES'] = M_LIST[i]  * 1024
        # test_args['BLOOM_K'] = (test_args['MEMORY_BYTES'] / 2) / 20000 * 0.693
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

def test_tbc_bloom_filter_wo_optm():
    test_dir = TEST_DIR_BASE + 'TBC_BLOOMFILTER_WO_OPTM/'
    test_file = 'test_tbc_bloomfilter_wo_optm.cpp_template'
    test_args = {
        "WORK_DIR" : '/home/hzheng/workSpace/SketchLab',
        "DATA_FILE" : 'data/WIDE/fifteen1.dat',
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "MEMORY_BYTES" : 0, # TBD
        "TBC_NUM" : 1,
        "BLOOM_K" : 3,
        "RESULT_CSV" :  'outputs/' + 'tbc_bloom_fp_no_optmi.csv'
    }
    out_file = 'logs/test_tbc_maxtable_'+logtime()+'.log'
    # M_LIST = [15000]
    M_LIST = [1000, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    for i in range(len(M_LIST)):
        test_args['MEMORY_BYTES'] = M_LIST[i]  * 1024
        # test_args['BLOOM_K'] = (test_args['MEMORY_BYTES'] / 2) / 20000 * 0.693
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
    test_tbc_bloom_filter_wo_optm()
    test_tbc_bloom_filter()
