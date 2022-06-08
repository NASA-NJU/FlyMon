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

def test_tbc_maxtable_max_interval():
    test_dir = TEST_DIR_BASE + 'TBC_MAX_TABLE/'
    test_file = 'test_tbc_max_table.cpp_template'
    test_args = {
        "WORK_DIR" : '/home/hzheng/workSpace/SketchLab',
        "DATA_FILE" : 'data/WIDE/fifteen1.dat',
        # "DATA_FILE" : 'data/WIDE/head1000.dat',
        "MEMORY" : 0, # TBD
        "DEPTH" : 3,
        "RESULT_CSV" :  'outputs/' + 'tbc_maxtable_max_interval.csv'
    }
    out_file = 'logs/test_tbc_maxtable_'+logtime()+'.log'
    M_LIST = [10000]
    # M_LIST = [5000, 4000, 3000, 2000, 1000, 900, 800, 700, 600, 500, 400, 300, 200, 100]
    # M_LIST = [100]
    for i in range(len(M_LIST)):
        test_args['MEMORY'] = M_LIST[i]  * 1024
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
    test_tbc_maxtable_max_interval()
